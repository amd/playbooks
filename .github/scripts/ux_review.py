# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
UX review agent for AMD Ryzen AI Halo playbooks.

Invoked from the /ux-review workflow on a pull request. Given the set of changed
playbook(s) in a PR, it runs two passes:

  1. Deterministic checks (no LLM): mechanical tag/consistency/copy-paste rules
     from ux_rules.json (e.g. missing @require:memory-config, legacy @setup tags,
     docker-vs-podman, stray trailing backticks, missing playbook.json fields).

  2. LLM rubric pass: sends the changed README to the model with the rubric in
     ux_rules.json for judgment-based findings (clarity, conciseness, consistency,
     grammar/spelling, correctness risk, disclaimers).

It prints a single ranked Markdown review (correctness -> consistency -> polish)
to stdout. The workflow posts that as a PR comment. This phase makes NO edits.

LLM plumbing (provider/base_url/model/extra_headers, both OpenAI and Anthropic
request shapes, retry/backoff) mirrors translate_playbook.py so the same repo
secrets and self-hosted runner are reused.

Usage:
  python ux_review.py --playbooks comfyui-image-gen,vllm-inference
  python ux_review.py --changed-files "$(git diff --name-only base sha)"
  python ux_review.py --playbooks deepseek-v4-flash-ds4 --dry-run
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
PLAYBOOKS_ROOT = REPO_ROOT / "playbooks"
RULES_PATH = SCRIPT_DIR / "ux_rules.json"

SEVERITY_LABEL = {
    "correctness": "Correctness",
    "consistency": "Consistency",
    "polish": "Polish",
}


# ---------------------------------------------------------------------------
# Config / discovery
# ---------------------------------------------------------------------------
def load_rules():
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


# A playbook id is a single folder name: letters, digits, dot, dash, underscore.
# Validating up front also blocks path-traversal (e.g. "../../etc") from an
# explicitly passed id.
VALID_PLAYBOOK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def find_playbook_dir(playbook_id):
    """Return (category, Path) for a playbook id, or (None, None)."""
    if not playbook_id or not VALID_PLAYBOOK_ID.match(playbook_id):
        return None, None
    for cat in ("core", "supplemental", "backup"):
        d = PLAYBOOKS_ROOT / cat / playbook_id
        if d.is_dir():
            return cat, d
    return None, None


def playbooks_from_changed_files(changed):
    """Extract unique playbook ids from a list of changed file paths."""
    ids = []
    seen = set()
    for line in changed:
        m = re.match(r"playbooks/(?:core|supplemental|backup)/([^/]+)/", line.strip())
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    return ids


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


# ---------------------------------------------------------------------------
# Deterministic checks
# ---------------------------------------------------------------------------
def _load_playbook_json(pb_dir):
    p = pb_dir / "playbook.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _pretty_id(rid):
    return rid.replace("-", " ").replace("_", " ").strip().capitalize()


def run_deterministic_rules(rules, pb_dir, readme):
    """Return a list of findings: (severity, title, detail)."""
    findings = []
    pj = _load_playbook_json(pb_dir)

    for rule in rules.get("deterministic_rules", []):
        rid = rule["id"]
        title = rule.get("title") or _pretty_id(rid)
        sev = rule.get("severity", "consistency")
        applies = rule.get("applies_to", "readme")
        rtype = rule["type"]
        msg = rule.get("message", rid)

        target = readme if applies == "readme" else ""

        try:
            if rtype == "must_contain":
                if rule["pattern"] not in target:
                    findings.append((sev, title, msg))

            elif rtype == "must_not_contain":
                if re.search(rule["pattern"], target):
                    findings.append((sev, title, msg))

            elif rtype == "paired_tags":
                # The pattern must, if present, appear within a device-scoped block.
                if rule["pattern"] in target and rule["requires_nearby"] not in target:
                    findings.append((sev, title, msg))

            elif rtype == "conflict":
                a = re.search(rule["pattern_a_regex"], target)
                b = re.search(rule["pattern_b_regex"], target)
                if a and b:
                    findings.append((sev, title, msg))

            elif rtype == "regex_present":
                if re.search(rule["pattern_regex"], target, re.MULTILINE):
                    findings.append((sev, title, msg))

            elif rtype == "json_field_present":
                if not pj or rule["field"] not in pj:
                    findings.append((sev, title, msg))

            elif rtype == "json_fields_present":
                missing = [f for f in rule["fields"] if not pj or f not in pj]
                if missing:
                    findings.append((sev, title, f"{msg} Missing: {', '.join(missing)}."))

            elif rtype == "cross_check_platform":
                has_content = rule["content_pattern"] in target
                has_platform = False
                if pj:
                    for _dev, oses in (pj.get("supported_platforms") or {}).items():
                        if rule["json_platform"] in (oses or []):
                            has_platform = True
                            break
                if has_content and not has_platform:
                    findings.append((sev, title, msg))

            elif rtype == "conditional_hint":
                triggered = re.search(rule["trigger_regex"], target)
                satisfied = any(k.lower() in target.lower() for k in rule["hint_keywords"])
                if triggered and not satisfied:
                    findings.append((sev, title, msg))

        except re.error as e:
            print(f"  [warn] rule '{rid}' has an invalid regex: {e}", file=sys.stderr)

    return findings


# ---------------------------------------------------------------------------
# LLM plumbing (mirrors translate_playbook.py)
# ---------------------------------------------------------------------------
def build_cfg(dry_run):
    extra_headers = {}
    raw = os.environ.get("LLM_EXTRA_HEADERS", "")
    if raw:
        try:
            extra_headers = json.loads(raw)
        except json.JSONDecodeError:
            print("ERROR: LLM_EXTRA_HEADERS is not valid JSON.", file=sys.stderr)
            sys.exit(2)
    cfg = {
        "provider": os.environ.get("LLM_PROVIDER", "openai").lower(),
        "base_url": os.environ.get("LLM_BASE_URL", ""),
        "model": os.environ.get("LLM_MODEL", "dry-run-model" if dry_run else ""),
        "extra_headers": extra_headers,
        "max_tokens": int(os.environ.get("LLM_MAX_TOKENS", "8192")),
        "dry_run": dry_run,
    }
    if not dry_run and (not cfg["base_url"] or not cfg["model"]):
        print("ERROR: set LLM_BASE_URL and LLM_MODEL (or use --dry-run).", file=sys.stderr)
        sys.exit(2)
    return cfg


def _http_post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)


def _call_openai(system_prompt, user_text, cfg, temperature):
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": cfg["model"],
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
    }
    headers = {"Content-Type": "application/json", **cfg["extra_headers"]}
    body = _http_post_json(url, payload, headers)
    return body["choices"][0]["message"]["content"]


def _call_anthropic(system_prompt, user_text, cfg, temperature):
    url = cfg["base_url"].rstrip("/") + "/v1/messages"
    payload = {
        "model": cfg["model"],
        "temperature": temperature,
        "max_tokens": cfg["max_tokens"],
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_text}],
    }
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        **cfg["extra_headers"],
    }
    body = _http_post_json(url, payload, headers)
    return "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")


def call_model(system_prompt, user_text, cfg, temperature=0, max_retries=6):
    fn = _call_anthropic if cfg["provider"] == "anthropic" else _call_openai
    last_err = None
    for attempt in range(max_retries):
        try:
            return fn(system_prompt, user_text, cfg, temperature)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError, IndexError) as e:
            last_err = e
            is_rate = isinstance(e, urllib.error.HTTPError) and e.code in (429, 503)
            retry_after = 0
            if is_rate:
                try:
                    retry_after = int(e.headers.get("Retry-After", "0"))
                except (ValueError, TypeError, AttributeError):
                    retry_after = 0
            base = 5 if is_rate else 2
            wait = max(retry_after, min(90, base * (2 ** attempt)))
            print(f"  [warn] model call failed (attempt {attempt + 1}): {e}; retrying in {wait}s", file=sys.stderr, flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Model call failed after {max_retries} attempts: {last_err}")


def _extract_json_obj(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if "```" in t:
            t = t[: t.rfind("```")]
        t = t.strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


def build_rubric_prompt(rules):
    rub = rules["llm_rubric"]
    lines = [rub["instructions"], "", "Review against these categories:"]
    for c in rub["categories"]:
        lines.append(f"- [{c['id']}] {c['prompt']}")
    lines += [
        "",
        "Return STRICT JSON only, no prose or fences, in this shape:",
        '{"findings": [{"severity": "correctness|consistency|polish", '
        '"title": "<short title>", "detail": "<1-3 sentences>", '
        '"location": "<line/snippet or empty>"}]}',
        "If there are no issues, return {\"findings\": []}.",
    ]
    return "\n".join(lines)


def run_llm_rubric(rules, pb_id, readme, cfg):
    """Return a list of (severity, title, detail) from the model, or []."""
    if cfg["dry_run"]:
        return [("polish", "dry-run", "LLM pass skipped (--dry-run).")]
    if not readme.strip():
        return []
    system = build_rubric_prompt(rules)
    user = f"Playbook id: {pb_id}\n\nREADME.md follows:\n\n{readme}"
    try:
        raw = call_model(system, user, cfg, temperature=0)
        obj = _extract_json_obj(raw)
    except (RuntimeError, ValueError, json.JSONDecodeError) as e:
        print(f"  [warn] LLM rubric pass failed for {pb_id}: {e}", file=sys.stderr)
        return [("polish", "LLM review unavailable",
                 "The model pass could not be completed; only deterministic checks are shown.")]
    out = []
    for f in obj.get("findings", []):
        sev = f.get("severity", "polish")
        if sev not in SEVERITY_LABEL:
            sev = "polish"
        title = str(f.get("title", "")).strip() or "(untitled)"
        detail = str(f.get("detail", "")).strip()
        loc = str(f.get("location", "")).strip()
        if loc:
            detail = f"{detail} _(around: {loc})_"
        out.append((sev, title, detail))
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render_report(per_playbook, severity_order):
    lines = ["## UX review", ""]
    total = sum(len(v) for v in per_playbook.values())
    if total == 0:
        lines.append("No UX issues found in the changed playbook(s). Nice work.")
        return "\n".join(lines)

    lines.append(
        "Automated UX review of the changed playbook(s). Findings are ranked "
        "correctness → consistency → polish. This is advisory — nothing has been "
        "changed. Reply to apply the ones you want (suggestion-block apply coming soon)."
    )
    lines.append("")

    for pb_id, findings in per_playbook.items():
        lines.append(f"### `{pb_id}`")
        if not findings:
            lines.append("_No issues found._")
            lines.append("")
            continue
        n = 1
        for sev in severity_order:
            group = [f for f in findings if f[0] == sev]
            if not group:
                continue
            lines.append(f"**{SEVERITY_LABEL[sev]}**")
            lines.append("")
            for _sev, title, detail in group:
                lines.append(f"{n}. **{title}** — {detail}")
                n += 1
            lines.append("")
    lines.append("---")
    lines.append("_Generated by the UX review agent. Edit `.github/scripts/ux_rules.json` to tune the checklist._")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="UX review agent for playbooks (advisory, no edits).")
    ap.add_argument("--playbooks", help="Comma-separated playbook ids to review.")
    ap.add_argument("--changed-files", help="Newline- or comma-separated changed file paths (e.g. from git diff).")
    ap.add_argument("--dry-run", action="store_true", help="Run deterministic checks only; skip the LLM pass.")
    ap.add_argument("--output", help="Write the report to this file in addition to stdout.")
    args = ap.parse_args()

    rules = load_rules()
    severity_order = rules.get("severity_order", ["correctness", "consistency", "polish"])

    ids = []
    if args.playbooks:
        ids = [x.strip() for x in args.playbooks.split(",") if x.strip()]
    elif args.changed_files:
        raw = args.changed_files.replace(",", "\n").splitlines()
        ids = playbooks_from_changed_files(raw)

    if not ids:
        report = ("## UX review\n\nNo changed playbook was detected in this PR, so there is "
                  "nothing to review. If you expected a review, confirm the PR changes files "
                  "under `playbooks/core/`, `playbooks/supplemental/`, or `playbooks/backup/`.")
        print(report)
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
        return

    cfg = build_cfg(args.dry_run)
    per_playbook = {}

    for pb_id in ids:
        _cat, pb_dir = find_playbook_dir(pb_id)
        if not pb_dir:
            per_playbook[pb_id] = [("correctness", "Playbook not found",
                                    f"No directory `playbooks/*/{pb_id}/` exists.")]
            continue
        readme = read_text(pb_dir / "README.md")
        findings = []
        findings += run_deterministic_rules(rules, pb_dir, readme)
        findings += run_llm_rubric(rules, pb_id, readme, cfg)
        per_playbook[pb_id] = findings

    report = render_report(per_playbook, severity_order)
    print(report)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
