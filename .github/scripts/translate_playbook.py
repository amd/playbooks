#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Playbook Translation Script

Automatically translates a playbook's prose into one or more target locales,
writing mirrored locale overlays under `translations/<locale>/`.

Design goals (see translations/README.md):
1. English under `playbooks/` stays the single canonical, executable source.
2. Only PROSE is translated. Fenced code blocks and HTML comments (which carry
   the special @os/@device/@require/@setup/@test/@github-only tags) are MASKED
   with sentinels before translation and restored verbatim afterward, so they
   can never be altered by the model. Inline code, links, and image paths are
   additionally protected via the system prompt + a structural validation gate.
3. Only `title` and `description` from playbook.json are translated, into
   `translations/<locale>/metadata/<id>.json`.
4. Reproducible: pinned model + temperature 0 + a content-hash manifest so
   unchanged English is never re-translated (idempotent).
5. Fully automatic gate: after translation, the number of masked segments
   (code fences + HTML comments) must match the source, and every sentinel must
   be restored. On mismatch the file is skipped and the run exits non-zero so
   CI can auto-open a tracking issue - no manual validation step.

Model access is via an OpenAI-compatible /chat/completions endpoint, configured
with env vars so the same script works against the internal AMD model (from a
self-hosted runner) or any other compatible endpoint:

    AMD_LLM_BASE_URL   e.g. https://<internal-endpoint>/v1
    AMD_LLM_MODEL      e.g. the pinned internal model name
    AMD_LLM_API_KEY    auth token (optional depending on endpoint)

Usage:
    python translate_playbook.py --playbook comfyui-image-gen \
        --locales zh-CN,es-LA,fr-FR

    # validate masking without calling the model:
    python translate_playbook.py --playbook comfyui-image-gen \
        --locales fr-FR --dry-run
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
PLAYBOOKS_ROOT = REPO_ROOT / "playbooks"
TRANSLATIONS_ROOT = REPO_ROOT / "translations"
GLOSSARY_PATH = SCRIPT_DIR / "glossary.json"
CATEGORIES = ["core", "supplemental"]

# Files whose prose is translated (kept in the mirrored tree).
PROSE_FILES = ["README.md", "platform.md"]

# Human-readable language names for the prompt.
LOCALE_NAMES = {
    "zh-CN": "Simplified Chinese (zh-CN)",
    "zh-TW": "Traditional Chinese (zh-TW)",
    "es-LA": "Latin American Spanish (es-LA)",
    "fr-FR": "French (fr-FR)",
}

# ---------------------------------------------------------------------------
# Masking: protect code fences and HTML comments (which hold the @-tags)
# ---------------------------------------------------------------------------
# Fenced code blocks: ``` or ~~~ ... closing fence. Multiline, non-greedy.
FENCE_RE = re.compile(r"(^|\n)(```|~~~).*?\n\2[ \t]*(?=\n|$)", re.DOTALL)
# HTML comments (covers copyright header + every @tag such as <!-- @os:windows -->)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Raw HTML blocks like <p ...>...</p> and standalone <img ...> (structural).
HTML_BLOCK_RE = re.compile(r"<(p|div|table|img|br|h[1-6])\b[^>]*>.*?(</\1>|$)", re.DOTALL | re.IGNORECASE)

SENTINEL = "\u2402L10N{}\u2403"  # unlikely to appear in prose or be altered
SENTINEL_FIND = re.compile(r"\u2402L10N(\d+)\u2403")


def mask_protected(text):
    """Replace protected spans with sentinels. Returns (masked, mapping)."""
    mapping = []

    def _sub(m):
        idx = len(mapping)
        mapping.append(m.group(0))
        return SENTINEL.format(idx)

    # Order matters: comments first (may contain '<'), then fences, then HTML.
    masked = HTML_COMMENT_RE.sub(_sub, text)
    masked = FENCE_RE.sub(_sub, masked)
    masked = HTML_BLOCK_RE.sub(_sub, masked)
    return masked, mapping


def unmask(text, mapping):
    def _restore(m):
        return mapping[int(m.group(1))]
    return SENTINEL_FIND.sub(_restore, text)


def count_protected(text):
    masked, mapping = mask_protected(text)
    return len(mapping)


# ---------------------------------------------------------------------------
# Model client (OpenAI-compatible /chat/completions)
# ---------------------------------------------------------------------------
def load_glossary():
    data = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    return data.get("do_not_translate", []), str(data.get("prompt_version", "1"))


def build_system_prompt(locale, glossary_terms):
    lang = LOCALE_NAMES.get(locale, locale)
    terms = ", ".join(glossary_terms)
    return (
        f"You are a professional technical translator localizing AMD developer "
        f"documentation into {lang}.\n"
        "Translate ONLY natural-language prose. Follow these rules exactly:\n"
        "1. Preserve the Markdown structure: headings (#), lists, tables, blockquotes, "
        "emphasis, and line breaks must stay in the same positions.\n"
        "2. NEVER translate or modify: code (fenced or inline `like this`), URLs, file "
        "paths, image paths, HTML, YAML/JSON keys, command names, flags, or environment "
        "variables.\n"
        "3. Any token of the form \u2402L10N<number>\u2403 is a placeholder for protected "
        "content. Copy every such placeholder verbatim and keep it in its original "
        "position. Do not add, remove, reorder, or renumber placeholders.\n"
        "4. Keep the following terms untranslated (verbatim): "
        f"{terms}.\n"
        "5. Translate Markdown link TEXT and image ALT text, but keep the target "
        "(the part in parentheses) unchanged.\n"
        "6. Do not add explanations, notes, or extra content. Return only the translated "
        "document."
    )


def _http_post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)


def _call_openai(system_prompt, user_text, cfg):
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": cfg["model"],
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
    }
    headers = {"Content-Type": "application/json", **cfg["extra_headers"]}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"
    body = _http_post_json(url, payload, headers)
    return body["choices"][0]["message"]["content"]


def _call_anthropic(system_prompt, user_text, cfg):
    url = cfg["base_url"].rstrip("/") + "/v1/messages"
    payload = {
        "model": cfg["model"],
        "temperature": 0,
        "max_tokens": cfg["max_tokens"],
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_text}],
    }
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        **cfg["extra_headers"],
    }
    if cfg["api_key"]:
        headers["x-api-key"] = cfg["api_key"]
    body = _http_post_json(url, payload, headers)
    # Concatenate text blocks from the Anthropic response.
    return "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")


def call_model(system_prompt, user_text, cfg, max_retries=4):
    fn = _call_anthropic if cfg["provider"] == "anthropic" else _call_openai
    last_err = None
    for attempt in range(max_retries):
        try:
            return fn(system_prompt, user_text, cfg)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError, IndexError) as e:
            last_err = e
            wait = 2 ** attempt
            print(f"  [warn] model call failed (attempt {attempt + 1}): {e}; retrying in {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Model call failed after {max_retries} attempts: {last_err}")


# ---------------------------------------------------------------------------
# Translation of a single markdown document
# ---------------------------------------------------------------------------
def translate_markdown(text, locale, cfg, glossary_terms):
    masked, mapping = mask_protected(text)
    n_protected = len(mapping)

    if cfg["dry_run"]:
        # Round-trip only: prove masking/unmasking is lossless.
        translated = masked
    else:
        system_prompt = build_system_prompt(locale, glossary_terms)
        translated = call_model(system_prompt, masked, cfg)

    # Validate every placeholder survived before restoring.
    out_sentinels = sorted(int(m) for m in SENTINEL_FIND.findall(translated))
    if out_sentinels != list(range(n_protected)):
        raise ValueError(
            f"placeholder mismatch: expected {n_protected} placeholders "
            f"(0..{n_protected - 1}), got {out_sentinels}"
        )

    restored = unmask(translated, mapping)

    # Structural gate: protected-span count must match the original source.
    if count_protected(restored) != n_protected:
        raise ValueError("protected-span count changed after restore")

    return restored


def translate_playbook_json(src_json_path, locale, cfg, glossary_terms):
    meta = json.loads(src_json_path.read_text(encoding="utf-8"))
    out = {"id": meta.get("id")}
    for field in ("title", "description"):
        val = meta.get(field)
        if not val:
            continue
        if cfg["dry_run"]:
            out[field] = val
        else:
            system_prompt = build_system_prompt(locale, glossary_terms) + (
                "\nTranslate the following short UI string. Return only the translation, "
                "no quotes or extra text."
            )
            out[field] = call_model(system_prompt, val, cfg).strip()
    return out


# ---------------------------------------------------------------------------
# Manifest / staleness
# ---------------------------------------------------------------------------
def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest(locale):
    path = TRANSLATIONS_ROOT / locale / "_manifest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"locale": locale, "files": {}}


def save_manifest(locale, manifest):
    path = TRANSLATIONS_ROOT / locale / "_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def find_playbook_dir(playbook_id):
    for cat in CATEGORIES:
        d = PLAYBOOKS_ROOT / cat / playbook_id
        if d.is_dir():
            return cat, d
    return None, None


def process_locale(playbook_id, cat, pb_dir, locale, cfg, glossary_terms, prompt_version):
    print(f"\n=== {playbook_id} -> {locale} ===", flush=True)
    manifest = load_manifest(locale)
    changed = 0
    failures = []

    # Prose files
    for fname in PROSE_FILES:
        src = pb_dir / fname
        if not src.exists():
            continue
        rel = f"playbooks/{cat}/{playbook_id}/{fname}"
        src_text = src.read_text(encoding="utf-8")
        src_hash = sha256(src_text)
        entry = manifest["files"].get(rel, {})
        out_path = TRANSLATIONS_ROOT / locale / "playbooks" / cat / playbook_id / fname

        up_to_date = (
            entry.get("source_sha256") == src_hash
            and entry.get("prompt_version") == prompt_version
            and entry.get("model") == cfg["model"]
            and out_path.exists()
        )
        if up_to_date and not cfg["force"]:
            print(f"  [skip] {rel} (up to date)", flush=True)
            continue

        try:
            translated = translate_markdown(src_text, locale, cfg, glossary_terms)
        except (ValueError, RuntimeError) as e:
            print(f"  [FAIL] {rel}: {e}", flush=True)
            failures.append((rel, str(e)))
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(translated, encoding="utf-8")
        manifest["files"][rel] = {
            "source_sha256": src_hash,
            "prompt_version": prompt_version,
            "model": cfg["model"],
        }
        changed += 1
        print(f"  [ok]   {rel}", flush=True)

    # Metadata (title/description from playbook.json)
    pj = pb_dir / "playbook.json"
    if pj.exists():
        rel = f"playbooks/{cat}/{playbook_id}/playbook.json"
        src_text = pj.read_text(encoding="utf-8")
        src_hash = sha256(src_text)
        entry = manifest["files"].get(rel, {})
        out_path = TRANSLATIONS_ROOT / locale / "metadata" / f"{playbook_id}.json"
        up_to_date = (
            entry.get("source_sha256") == src_hash
            and entry.get("prompt_version") == prompt_version
            and entry.get("model") == cfg["model"]
            and out_path.exists()
        )
        if up_to_date and not cfg["force"]:
            print(f"  [skip] {rel} metadata (up to date)", flush=True)
        else:
            try:
                meta_out = translate_playbook_json(pj, locale, cfg, glossary_terms)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(json.dumps(meta_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                manifest["files"][rel] = {
                    "source_sha256": src_hash,
                    "prompt_version": prompt_version,
                    "model": cfg["model"],
                }
                changed += 1
                print(f"  [ok]   {rel} -> metadata/{playbook_id}.json", flush=True)
            except (RuntimeError,) as e:
                print(f"  [FAIL] {rel} metadata: {e}", flush=True)
                failures.append((rel, str(e)))

    save_manifest(locale, manifest)
    return changed, failures


def main():
    ap = argparse.ArgumentParser(description="Translate a playbook into target locales.")
    ap.add_argument("--playbook", required=True, help="Playbook id (folder name)")
    ap.add_argument("--locales", required=True, help="Comma-separated locale codes, e.g. zh-CN,es-LA,fr-FR")
    ap.add_argument("--force", action="store_true", help="Retranslate even if up to date")
    ap.add_argument("--dry-run", action="store_true", help="Mask/round-trip only; do not call the model")
    args = ap.parse_args()

    cat, pb_dir = find_playbook_dir(args.playbook)
    if not pb_dir:
        print(f"ERROR: playbook '{args.playbook}' not found under playbooks/{{core,supplemental}}/", file=sys.stderr)
        sys.exit(2)

    extra_headers = {}
    raw_headers = os.environ.get("AMD_LLM_EXTRA_HEADERS", "")
    if raw_headers:
        try:
            extra_headers = json.loads(raw_headers)
        except json.JSONDecodeError:
            print("ERROR: AMD_LLM_EXTRA_HEADERS is not valid JSON.", file=sys.stderr)
            sys.exit(2)

    cfg = {
        "provider": os.environ.get("AMD_LLM_PROVIDER", "openai").lower(),
        "base_url": os.environ.get("AMD_LLM_BASE_URL", ""),
        "model": os.environ.get("AMD_LLM_MODEL", "dry-run-model" if args.dry_run else ""),
        "api_key": os.environ.get("AMD_LLM_API_KEY", ""),
        "extra_headers": extra_headers,
        "max_tokens": int(os.environ.get("AMD_LLM_MAX_TOKENS", "8192")),
        "force": args.force,
        "dry_run": args.dry_run,
    }
    if not args.dry_run and (not cfg["base_url"] or not cfg["model"]):
        print("ERROR: set AMD_LLM_BASE_URL and AMD_LLM_MODEL (or use --dry-run).", file=sys.stderr)
        sys.exit(2)

    glossary_terms, prompt_version = load_glossary()
    locales = [x.strip() for x in args.locales.split(",") if x.strip()]

    total_changed = 0
    all_failures = []
    for locale in locales:
        changed, failures = process_locale(
            args.playbook, cat, pb_dir, locale, cfg, glossary_terms, prompt_version
        )
        total_changed += changed
        all_failures.extend((locale, rel, err) for rel, err in failures)

    print(f"\nDone. {total_changed} file(s) written.", flush=True)
    if all_failures:
        print(f"{len(all_failures)} file(s) FAILED the structural gate:", flush=True)
        for locale, rel, err in all_failures:
            print(f"  - [{locale}] {rel}: {err}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
