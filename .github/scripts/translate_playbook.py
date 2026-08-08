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

Model access is via an OpenAI-compatible or Anthropic-style endpoint, configured
with env vars so the same script works against any compatible LLM API (from a
self-hosted runner or a local machine):

    LLM_BASE_URL   base URL of the LLM API, e.g. https://<endpoint>/v1
    LLM_MODEL      the model name to use for translation
    LLM_EXTRA_HEADERS  JSON map of extra request headers (e.g. an auth header)

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
DEPENDENCIES_DIR = PLAYBOOKS_ROOT / "dependencies"
TRANSLATIONS_ROOT = REPO_ROOT / "auto-translations"
GLOSSARY_PATH = SCRIPT_DIR / "glossary.json"
DISCLAIMER_PATH = SCRIPT_DIR / "disclaimers.json"
CATEGORIES = ["core", "supplemental"]

# Files whose prose is translated (kept in the mirrored tree).
PROSE_FILES = ["README.md", "platform.md"]

# Human-readable language names for the prompt - the 29 Lenovo languages plus
# fr-CA, added for the Canada launch (Quebec Bill 96 locale alignment).
LOCALE_NAMES = {
    "zh-CN": "Simplified Chinese (zh-CN)",
    "zh-TW": "Traditional Chinese (zh-TW)",
    "cs-CZ": "Czech (cs-CZ)",
    "da-DK": "Danish (da-DK)",
    "de-DE": "German (de-DE)",
    "el-GR": "Greek (el-GR)",
    "es-LA": "Latin American Spanish (es-LA)",
    "fi-FI": "Finnish (fi-FI)",
    "fr-FR": "French (fr-FR)",
    # Spelled out so the model produces genuinely Canadian French rather than a
    # near-copy of fr-FR - these two are the closest pair in the locale set.
    "fr-CA": "Canadian French (fr-CA, Quebec/OQLF conventions)",
    "hu-HU": "Hungarian (hu-HU)",
    "it-IT": "Italian (it-IT)",
    "ja-JP": "Japanese (ja-JP)",
    "ko-KR": "Korean (ko-KR)",
    "nl-NL": "Dutch (nl-NL)",
    "nb-NO": "Norwegian Bokmal (nb-NO)",
    "pl-PL": "Polish (pl-PL)",
    "pt-BR": "Brazilian Portuguese (pt-BR)",
    "pt-PT": "European Portuguese (pt-PT)",
    "ru-RU": "Russian (ru-RU)",
    "sv-SE": "Swedish (sv-SE)",
    "th-TH": "Thai (th-TH)",
    "tr-TR": "Turkish (tr-TR)",
    "uk-UA": "Ukrainian (uk-UA)",
    "ar": "Arabic (ar)",
    "he": "Hebrew (he)",
    "ro-RO": "Romanian (ro-RO)",
    "sr-Latn": "Serbian in Latin script (sr-Latn)",
    "sk-SK": "Slovak (sk-SK)",
    "sl-SI": "Slovenian (sl-SI)",
}

# ---------------------------------------------------------------------------
# Masking: protect code fences and HTML comments (which hold the @-tags)
# ---------------------------------------------------------------------------
# Fenced code blocks: ``` or ~~~ ... closing fence. Multiline, non-greedy.
# Capture the trailing newline (not just look ahead) so a restored code block is
# always line-terminated. Otherwise, if the model attaches translated prose to the
# closing-fence line (common in ja/ko/fi/tr where the verb follows the code
# reference), the fence stops closing and re-masking merges it with the next block.
FENCE_RE = re.compile(r"(^|\n)(```|~~~).*?\n\2[ \t]*(?:\n|$)", re.DOTALL)
# GitHub-only notices, masked as a single span so the block passes through in
# English. The website strips these blocks outright, so GitHub is the only place
# they ever render and there is nothing to gain from translating them - while a
# model rewrite risks corrupting the very markers the website's strip keys on.
# Must run before HTML_COMMENT_RE, which would otherwise protect only the two
# marker comments and leave the prose between them translatable.
GITHUB_ONLY_RE = re.compile(r"<!-- @github-only -->.*?<!-- @github-only:end -->", re.DOTALL)
# Same block, but anchored to the start of the marker's line so that repairing an
# existing translation also removes any stray prefix a model prepended to it.
GITHUB_ONLY_LINE_RE = re.compile(
    r"^[^\n]*?<!-- @github-only -->.*?<!-- @github-only:end -->",
    re.DOTALL | re.MULTILINE,
)
# HTML comments (covers copyright header + every @tag such as <!-- @os:windows -->)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Individual raw HTML tags (opening, closing, or self-closing). Masking each tag
# on its own - rather than a whole <p>...</p> block - keeps prose between tags
# translatable and is robust to malformed/unclosed tags in the source.
HTML_TAG_RE = re.compile(
    r"</?(?:p|div|table|thead|tbody|tr|td|th|img|br|hr|h[1-6]|a|span|sup|sub|details|summary)\b[^>]*/?>",
    re.IGNORECASE,
)
# Leading license/copyright HTML comment - stripped before translation and
# re-attached verbatim, so the model can never drop or alter it.
LICENSE_HEADER_RE = re.compile(r"^\ufeff?\s*<!--.*?SPDX-License-Identifier.*?-->\s*", re.DOTALL)
# Runs of non-BMP characters (emoji, U+10000 and above). These are literal UI
# glyphs rather than translatable prose, so masking them costs nothing and
# guarantees they survive byte-for-byte. It is also required: the LLM gateway
# returns HTTP 500 whenever the model's *response* contains a non-BMP character
# (a request carrying one is fine), which otherwise makes any playbook with an
# emoji impossible to translate.
NON_BMP_RE = re.compile(r"[^\u0000-\uffff]+")

SENTINEL = "\u2402L10N{}\u2403"  # unlikely to appear in prose or be altered
SENTINEL_FIND = re.compile(r"\u2402L10N(\d+)\u2403")

# Machine-translation disclaimer, injected at the top of each translated prose
# file (outside @github-only so it renders on GitHub and the website). Wrapped in
# a marker so it can be inserted/refreshed idempotently.
DISCLAIMER_MARKER = "auto-translated-disclaimer"
DISCLAIMER_BLOCK_RE = re.compile(
    r"[ \t]*<!-- " + re.escape(DISCLAIMER_MARKER) + r"\b.*?"
    r"<!-- " + re.escape(DISCLAIMER_MARKER) + r":end -->[ \t]*\n?",
    re.DOTALL,
)


def mask_protected(text):
    """Replace protected spans with sentinels. Returns (masked, mapping)."""
    mapping = []

    def _sub(m):
        idx = len(mapping)
        mapping.append(m.group(0))
        return SENTINEL.format(idx)

    # Order matters: whole github-only blocks, then comments (may contain '<'),
    # then fences, then HTML tags. Emoji last, so ones already inside a masked
    # span are not masked twice.
    masked = GITHUB_ONLY_RE.sub(_sub, text)
    masked = HTML_COMMENT_RE.sub(_sub, masked)
    masked = FENCE_RE.sub(_sub, masked)
    masked = HTML_TAG_RE.sub(_sub, masked)
    masked = NON_BMP_RE.sub(_sub, masked)
    return masked, mapping


def unmask(text, mapping):
    def _restore(m):
        return mapping[int(m.group(1))]
    # Restore iteratively: a masked span can itself contain sentinels (e.g. a
    # fenced ```markdown example that embeds HTML comments or nested fences), and
    # a single pass would leave those inner sentinels unrestored.
    for _ in range(len(mapping) + 1):
        new_text = SENTINEL_FIND.sub(_restore, text)
        if new_text == text:
            break
        text = new_text
    return text


def count_protected(text):
    masked, mapping = mask_protected(text)
    return len(mapping)


# ---------------------------------------------------------------------------
# Model client (OpenAI-compatible /chat/completions)
# ---------------------------------------------------------------------------
def load_glossary():
    data = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    return data.get("do_not_translate", []), str(data.get("prompt_version", "1"))


_DISCLAIMERS = None


def load_disclaimers():
    global _DISCLAIMERS
    if _DISCLAIMERS is None:
        _DISCLAIMERS = json.loads(DISCLAIMER_PATH.read_text(encoding="utf-8"))
    return _DISCLAIMERS


def disclaimer_block(locale):
    """The localized machine-translation admonition, wrapped in the idempotency
    marker. Body falls back to English when a locale has no curated string."""
    data = load_disclaimers()
    version = str(data.get("version", "1"))
    text = (data.get("locales", {}).get(locale) or data.get("en", "")).strip()
    quoted = "\n".join((f"> {line}" if line else ">") for line in text.split("\n"))
    return (
        f"<!-- {DISCLAIMER_MARKER} v{version} -->\n"
        f"> [!WARNING]\n"
        f"{quoted}\n"
        f"<!-- {DISCLAIMER_MARKER}:end -->"
    )


def ensure_disclaimer(text, locale):
    """Insert (or refresh) the disclaimer block right after the license header,
    before any content. Idempotent: an existing block is removed first, so this is
    safe to run repeatedly and to re-run after bumping the disclaimer version."""
    text = DISCLAIMER_BLOCK_RE.sub("", text)
    block = disclaimer_block(locale)
    m = LICENSE_HEADER_RE.match(text)
    if m:
        # Normalize whitespace around the insertion point so re-running is a no-op.
        header = text[:m.end()].rstrip()
        rest = text[m.end():].lstrip("\n")
        return f"{header}\n\n{block}\n\n{rest}"
    return f"{block}\n\n{text.lstrip(chr(10))}"


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
    # Concatenate text blocks from the Anthropic response.
    return "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")


def call_model(system_prompt, user_text, cfg, temperature=0, max_retries=6):
    fn = _call_anthropic if cfg["provider"] == "anthropic" else _call_openai
    last_err = None
    for attempt in range(max_retries):
        try:
            return fn(system_prompt, user_text, cfg, temperature)
        except (urllib.error.URLError, urllib.error.HTTPError, ConnectionError, TimeoutError, KeyError, IndexError) as e:
            last_err = e
            # Rate limiting (429) / overload (503): back off harder and honor
            # Retry-After when the server provides it.
            is_rate = isinstance(e, urllib.error.HTTPError) and e.code in (429, 503)
            retry_after = 0
            if is_rate:
                try:
                    retry_after = int(e.headers.get("Retry-After", "0"))
                except (ValueError, TypeError, AttributeError):
                    retry_after = 0
            base = 5 if is_rate else 2
            wait = max(retry_after, min(90, base * (2 ** attempt)))
            tag = "rate-limited" if is_rate else "failed"
            print(f"  [warn] model call {tag} (attempt {attempt + 1}): {e}; retrying in {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Model call failed after {max_retries} attempts: {last_err}")


# ---------------------------------------------------------------------------
# Translation of a single markdown document
# ---------------------------------------------------------------------------

# Large docs are translated section-by-section. A single giant request makes the
# model elide long runs of adjacent placeholder tokens (dense @-tag / code-fence
# clusters), dropping them and failing the structural gate. Splitting at headings
# keeps each request small so nothing gets dropped, and a failed section is
# isolated. Docs at/under this masked size stay single-shot (unchanged behavior).
MAX_CHUNK_CHARS = 6000
HEADING_RE = re.compile(r"^#{2,6} ", re.MULTILINE)


def _pack_sections(masked):
    """Split masked text at markdown headings (h2-h6) and pack the sections into
    chunks of at most MAX_CHUNK_CHARS. '\\n'.join(result) == masked exactly, so
    reassembly is lossless."""
    lines = masked.split("\n")
    sections = []
    cur = []
    for line in lines:
        if HEADING_RE.match(line) and cur:
            sections.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        sections.append("\n".join(cur))

    chunks = []
    buf = ""
    for sec in sections:
        if buf and len(buf) + 1 + len(sec) > MAX_CHUNK_CHARS:
            chunks.append(buf)
            buf = sec
        else:
            buf = sec if not buf else buf + "\n" + sec
    if buf:
        chunks.append(buf)
    return chunks


# A line made up solely of placeholder tokens (+ whitespace) is a whole-line
# structural marker - a masked @os/@device/@require/@github-only comment, a fenced
# code block, etc. These carry no translatable prose, and some models drop such
# bare-token lines when translating the surrounding text. They are passed through
# verbatim in the segmented fallback so they can never be dropped.
_SENTINEL_ONLY_LINE = re.compile(r"^\s*(?:\u2402L10N\d+\u2403\s*)+$")


def _translate_text_block(text, base_prompt, cfg, quality_retry):
    """Translate one masked text, preserving its placeholder subset exactly.
    Raises ValueError if the placeholders can't be reproduced."""
    expected = sorted(int(x) for x in SENTINEL_FIND.findall(text))
    # Nothing translatable (only placeholders/whitespace/punctuation): return as is.
    if not re.search(r"[^\W\d_]", SENTINEL_FIND.sub("", text)):
        return text

    last_seen = None
    for i in range(2):
        system_prompt = base_prompt
        temperature = 0.4 if quality_retry else 0
        if i > 0:
            system_prompt = base_prompt + (
                "\nCRITICAL: The previous attempt lost or duplicated some "
                "\u2402L10N<number>\u2403 placeholder tokens. Reproduce EVERY placeholder "
                "exactly once, in the same order, byte-for-byte. Do not omit any."
            )
            temperature = 0.6 if quality_retry else 0.3
        candidate = call_model(system_prompt, text, cfg, temperature=temperature)
        seen = sorted(int(x) for x in SENTINEL_FIND.findall(candidate))
        if seen == expected:
            return candidate
        last_seen = seen
    raise ValueError(
        f"placeholder mismatch in section: expected {expected}, got {last_seen}"
    )


def _translate_chunk(masked_chunk, base_prompt, cfg, quality_retry):
    """Translate one masked chunk. Fast path: a single request for the whole
    chunk. If that drops placeholders - some models omit whole-line structural
    markers (paired @tag comments around admonitions, etc.) - fall back to
    translating only the prose segments and passing the marker lines through
    verbatim, so they cannot be dropped."""
    try:
        return _translate_text_block(masked_chunk, base_prompt, cfg, quality_retry)
    except ValueError:
        pass  # fall through to the segmented, marker-safe path

    lines = masked_chunk.split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        if _SENTINEL_ONLY_LINE.match(lines[i]):
            out.append(lines[i])  # structural marker line: kept verbatim, never sent
            i += 1
            continue
        j = i
        while j < n and not _SENTINEL_ONLY_LINE.match(lines[j]):
            j += 1
        out.append(_translate_text_block("\n".join(lines[i:j]), base_prompt, cfg, quality_retry))
        i = j
    return "\n".join(out)


def translate_markdown(text, locale, cfg, glossary_terms, quality_retry=False):
    # Pull the license/copyright header out so the model can't drop or alter it;
    # it is re-attached verbatim after translation.
    header = ""
    m = LICENSE_HEADER_RE.match(text)
    body = text
    if m:
        header = m.group(0)
        body = text[m.end():]

    masked, mapping = mask_protected(body)
    n_protected = len(mapping)
    expected = list(range(n_protected))

    if cfg["dry_run"]:
        # Round-trip only: prove masking/unmasking is lossless.
        translated = masked
    else:
        base_prompt = build_system_prompt(locale, glossary_terms)
        if quality_retry:
            base_prompt += (
                "\nProduce the most natural, fluent phrasing a native professional would use, "
                "while preserving meaning and every placeholder exactly."
            )
        # Small docs: one request. Large docs: split at headings so the model
        # never sees a payload big enough to drop placeholder runs.
        chunks = _pack_sections(masked) if len(masked) > MAX_CHUNK_CHARS else [masked]
        translated = "\n".join(
            _translate_chunk(chunk, base_prompt, cfg, quality_retry) for chunk in chunks
        )

    # Validate every placeholder survived before restoring (also covers dry-run).
    out_sentinels = sorted(int(x) for x in SENTINEL_FIND.findall(translated))
    if out_sentinels != expected:
        raise ValueError(
            f"placeholder mismatch: expected {n_protected} placeholders "
            f"(0..{n_protected - 1}), got {out_sentinels}"
        )

    restored = unmask(translated, mapping)

    # Structural gate: protected-span count must match the original source.
    if count_protected(restored) != n_protected:
        raise ValueError("protected-span count changed after restore")

    return header + restored


# ---------------------------------------------------------------------------
# Automated quality scoring (GEMBA/MQM style) - no human review required.
# A defensible 0-100 adequacy/fluency score is produced for every file by an
# independent judge model (ideally stronger than the translator, e.g. Opus
# judging Sonnet) and stored in the manifest + quality report.
# ---------------------------------------------------------------------------
def _judge_cfg(cfg):
    c = dict(cfg)
    c["model"] = cfg.get("judge_model") or cfg["model"]
    return c


def judge_translation(src_text, translated, locale, cfg):
    """Returns (score:int 0-100, issues:str). 100 on dry-run."""
    if cfg["dry_run"]:
        return 100, ""
    lang = LOCALE_NAMES.get(locale, locale)
    system = (
        "You are a professional translation quality evaluator using the MQM/GEMBA method. "
        f"Score the {lang} translation of the English source from 0 to 100 "
        "(100=flawless professional; 90-99=publishable, minor nits; 75-89=good, light edit; "
        "60-74=understandable but needs edits; <60=serious errors). Judge adequacy, fluency, "
        "terminology, and that code blocks, numbers, URLs, and brand terms are intact. "
        "Reply as strict JSON only: {\"score\": <int>, \"issues\": \"<=25 words\"}."
    )
    user = f"SOURCE (English):\n{src_text}\n\nTRANSLATION ({lang}):\n{translated}"
    # Try up to twice: judge models sometimes wrap the JSON in prose/fences, so
    # we extract the first {...} object rather than parsing the whole reply.
    last_err = None
    for attempt in range(2):
        try:
            raw = call_model(system, user, _judge_cfg(cfg), temperature=0).strip()
            d = _extract_json_obj(raw)
            score = int(d.get("score", 0))
            return max(0, min(100, score)), str(d.get("issues", ""))[:200]
        except (ValueError, RuntimeError, json.JSONDecodeError, KeyError, TypeError) as e:
            last_err = e
    return 0, f"judge error: {last_err}"


def _extract_json_obj(text):
    """Parse a JSON object from a model reply that may include code fences or
    trailing commentary. Falls back to the first {...} block."""
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


def produce_markdown(src_text, locale, cfg, glossary_terms):
    """Translate + score a markdown file. If the score is below threshold, make
    one higher-temperature quality retry and keep whichever scores higher.
    Returns (text, score, issues)."""
    text = translate_markdown(src_text, locale, cfg, glossary_terms)
    score, issues = judge_translation(src_text, text, locale, cfg)
    if (not cfg["dry_run"]) and score < cfg["quality_threshold"]:
        try:
            alt = translate_markdown(src_text, locale, cfg, glossary_terms, quality_retry=True)
            a_score, a_issues = judge_translation(src_text, alt, locale, cfg)
            if a_score > score:
                text, score, issues = alt, a_score, a_issues
        except (ValueError, RuntimeError):
            pass  # keep the first (structurally valid) translation
    return text, score, issues


def judge_id_of(cfg):
    """The judge model currently in effect (falls back to the translator model)."""
    return cfg.get("judge_model") or cfg["model"]


def translation_is_current(entry, src_hash, prompt_version, cfg, out_path):
    """True when the existing translation still matches the source, prompt, and
    translator model (i.e. it does NOT need re-translating). Judge model is checked
    separately, since a judge change only needs a re-score, not a re-translation."""
    return (
        entry.get("source_sha256") == src_hash
        and entry.get("prompt_version") == prompt_version
        and entry.get("model") == cfg["model"]
        and out_path.exists()
    )


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
    # Flag so the website / consumers can tell this metadata is machine-translated.
    out["auto_translated"] = True
    return out


# ---------------------------------------------------------------------------
# Manifest / staleness
# ---------------------------------------------------------------------------
def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Per-locale record of translation provenance + accuracy score for every file.
ACCURACY_FILE = "translation_accuracy.json"


def load_manifest(locale):
    path = TRANSLATIONS_ROOT / locale / ACCURACY_FILE
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"locale": locale, "files": {}}


def save_manifest(locale, manifest):
    path = TRANSLATIONS_ROOT / locale / ACCURACY_FILE
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
        # Output tree mirrors playbooks/ WITHOUT the extra "playbooks" layer:
        # auto-translations/<locale>/<cat>/<id>/<file>
        out_path = TRANSLATIONS_ROOT / locale / cat / playbook_id / fname
        judge_id = judge_id_of(cfg)

        if translation_is_current(entry, src_hash, prompt_version, cfg, out_path) and not cfg["force"]:
            if entry.get("judge_model") == judge_id:
                print(f"  [skip] {rel} (up to date)", flush=True)
                continue
            # Translation is still valid but the judge model changed: re-score the
            # existing translation (no re-translation needed).
            score, issues = judge_translation(src_text, DISCLAIMER_BLOCK_RE.sub("", out_path.read_text(encoding="utf-8")), locale, cfg)
            entry.update(quality_score=score, quality_issues=issues, judge_model=judge_id)
            manifest["files"][rel] = entry
            changed += 1
            print(f"  [rescore] {rel}  (score {score}, judge {judge_id})", flush=True)
            continue

        try:
            translated, score, issues = produce_markdown(src_text, locale, cfg, glossary_terms)
        except (ValueError, RuntimeError) as e:
            print(f"  [FAIL] {rel}: {e}", flush=True)
            failures.append((rel, str(e)))
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Prepend the machine-translation disclaimer (after scoring, so it never
        # affects the quality score). Not applied to shared dependency files.
        out_path.write_text(ensure_disclaimer(translated, locale), encoding="utf-8")
        manifest["files"][rel] = {
            "source_sha256": src_hash,
            "prompt_version": prompt_version,
            "model": cfg["model"],
            "judge_model": cfg.get("judge_model") or cfg["model"],
            "quality_score": score,
            "quality_issues": issues,
        }
        changed += 1
        print(f"  [ok]   {rel}  (score {score})", flush=True)

    # Metadata (title/description from playbook.json)
    pj = pb_dir / "playbook.json"
    if pj.exists():
        rel = f"playbooks/{cat}/{playbook_id}/playbook.json"
        src_text = pj.read_text(encoding="utf-8")
        src_hash = sha256(src_text)
        entry = manifest["files"].get(rel, {})
        # Mirror the source layout: translated title/description go into a
        # playbook.json inside the playbook's own folder (not a separate metadata/).
        out_path = TRANSLATIONS_ROOT / locale / cat / playbook_id / "playbook.json"
        judge_id = judge_id_of(cfg)
        if translation_is_current(entry, src_hash, prompt_version, cfg, out_path) and not cfg["force"] and entry.get("judge_model") == judge_id:
            print(f"  [skip] {rel} metadata (up to date)", flush=True)
        elif translation_is_current(entry, src_hash, prompt_version, cfg, out_path) and not cfg["force"]:
            # Translation still valid but the judge model changed: re-score only.
            try:
                meta_src = json.loads(src_text)
                meta_out = json.loads(out_path.read_text(encoding="utf-8"))
                src_join = "\n".join(str(meta_src.get(f, "")) for f in ("title", "description"))
                tgt_join = "\n".join(str(meta_out.get(f, "")) for f in ("title", "description"))
                score, issues = judge_translation(src_join, tgt_join, locale, cfg)
                entry.update(quality_score=score, quality_issues=issues, judge_model=judge_id)
                manifest["files"][rel] = entry
                changed += 1
                print(f"  [rescore] {rel} (title/description)  (score {score}, judge {judge_id})", flush=True)
            except (RuntimeError, ValueError, json.JSONDecodeError) as e:
                print(f"  [FAIL] {rel} metadata rescore: {e}", flush=True)
                failures.append((rel, str(e)))
        else:
            try:
                meta_out = translate_playbook_json(pj, locale, cfg, glossary_terms)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(json.dumps(meta_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                # Score the user-visible title + description.
                meta_src = json.loads(src_text)
                src_join = "\n".join(str(meta_src.get(f, "")) for f in ("title", "description"))
                tgt_join = "\n".join(str(meta_out.get(f, "")) for f in ("title", "description"))
                score, issues = judge_translation(src_join, tgt_join, locale, cfg)
                manifest["files"][rel] = {
                    "source_sha256": src_hash,
                    "prompt_version": prompt_version,
                    "model": cfg["model"],
                    "judge_model": cfg.get("judge_model") or cfg["model"],
                    "quality_score": score,
                    "quality_issues": issues,
                }
                changed += 1
                print(f"  [ok]   {rel} (title/description)  (score {score})", flush=True)
            except (RuntimeError,) as e:
                print(f"  [FAIL] {rel} metadata: {e}", flush=True)
                failures.append((rel, str(e)))

    save_manifest(locale, manifest)
    return changed, failures


def process_dependencies(locale, cfg, glossary_terms, prompt_version):
    """Translate the shared dependency markdown files (playbooks/dependencies/*.md)
    used by @require/@setup dropdowns, into translations/<locale>/playbooks/dependencies/."""
    print(f"\n=== dependencies -> {locale} ===", flush=True)
    manifest = load_manifest(locale)
    changed = 0
    failures = []

    for src in sorted(DEPENDENCIES_DIR.glob("*.md")):
        rel = f"playbooks/dependencies/{src.name}"
        src_text = src.read_text(encoding="utf-8")
        src_hash = sha256(src_text)
        entry = manifest["files"].get(rel, {})
        out_path = TRANSLATIONS_ROOT / locale / "dependencies" / src.name
        judge_id = judge_id_of(cfg)

        if translation_is_current(entry, src_hash, prompt_version, cfg, out_path) and not cfg["force"]:
            if entry.get("judge_model") == judge_id:
                print(f"  [skip] {rel} (up to date)", flush=True)
                continue
            # Translation still valid but the judge model changed: re-score only.
            score, issues = judge_translation(src_text, DISCLAIMER_BLOCK_RE.sub("", out_path.read_text(encoding="utf-8")), locale, cfg)
            entry.update(quality_score=score, quality_issues=issues, judge_model=judge_id)
            manifest["files"][rel] = entry
            changed += 1
            print(f"  [rescore] {rel}  (score {score}, judge {judge_id})", flush=True)
            continue

        try:
            translated, score, issues = produce_markdown(src_text, locale, cfg, glossary_terms)
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
            "judge_model": cfg.get("judge_model") or cfg["model"],
            "quality_score": score,
            "quality_issues": issues,
        }
        changed += 1
        print(f"  [ok]   {rel}  (score {score})", flush=True)

    save_manifest(locale, manifest)
    return changed, failures


def apply_disclaimers(locales):
    """Insert/refresh the machine-translation disclaimer on existing translated
    README.md/platform.md files, and set auto_translated=true in each translated
    playbook.json - without re-translating. Idempotent; safe to re-run and to run
    after bumping the disclaimer version. Returns the number of files changed.

    Only touches auto-translations/ (TRANSLATIONS_ROOT). Human-authored
    localized-playbooks/ are intentionally never given the disclaimer - and since
    they take precedence at render time, a human-localized file is served without
    it."""
    if not TRANSLATIONS_ROOT.exists():
        print("No auto-translations/ tree found; nothing to do.", flush=True)
        return 0
    changed = 0
    for locale in locales:
        loc_dir = TRANSLATIONS_ROOT / locale
        if not loc_dir.is_dir():
            continue
        for fname in PROSE_FILES:
            for f in sorted(loc_dir.rglob(fname)):
                original = f.read_text(encoding="utf-8")
                updated = ensure_disclaimer(original, locale)
                if updated != original:
                    f.write_text(updated, encoding="utf-8")
                    changed += 1
        for pj in sorted(loc_dir.rglob("playbook.json")):
            data = json.loads(pj.read_text(encoding="utf-8"))
            if data.get("auto_translated") is not True:
                data["auto_translated"] = True
                pj.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                changed += 1
    print(f"\nDone. Disclaimer/flag applied: {changed} file(s) updated across {len(locales)} locale(s).", flush=True)
    return changed


def sync_github_only(locales):
    """Restore the verbatim English @github-only block in existing translations,
    dropping any stray prefix a model prepended to the opening marker. Brings
    files translated before these blocks were masked into the same state a fresh
    run now produces, without re-translating. Returns the number of files changed.

    A stray prefix is not cosmetic: the website strips from '<!--' to the end
    marker, so anything the model put ahead of the marker survives the strip and
    renders on the page (a lone '#' becomes an empty heading)."""
    if not TRANSLATIONS_ROOT.exists():
        print("No auto-translations/ tree found; nothing to do.", flush=True)
        return 0
    changed = 0
    for locale in locales:
        loc_dir = TRANSLATIONS_ROOT / locale
        if not loc_dir.is_dir():
            continue
        for fname in PROSE_FILES:
            for f in sorted(loc_dir.rglob(fname)):
                src = PLAYBOOKS_ROOT / f.relative_to(loc_dir)
                if not src.exists():
                    continue
                src_blocks = GITHUB_ONLY_RE.findall(src.read_text(encoding="utf-8"))
                original = f.read_text(encoding="utf-8")
                matches = list(GITHUB_ONLY_LINE_RE.finditer(original))
                if not matches:
                    continue
                if len(matches) != len(src_blocks):
                    print(f"  [warn] {f.relative_to(TRANSLATIONS_ROOT)}: "
                          f"{len(matches)} block(s) vs {len(src_blocks)} in source; skipped", flush=True)
                    continue
                parts, last = [], 0
                for m, block in zip(matches, src_blocks):
                    parts.append(original[last:m.start()])
                    parts.append(block)
                    last = m.end()
                parts.append(original[last:])
                updated = "".join(parts)
                if updated != original:
                    f.write_text(updated, encoding="utf-8")
                    changed += 1
    print(f"\nDone. GitHub-only blocks synced: {changed} file(s) updated across {len(locales)} locale(s).", flush=True)
    return changed


def write_quality_report():
    """Aggregate quality_score across all locale manifests into a single report
    at translations/_quality_report.json (+ .md) - the defensible accuracy record."""
    if not TRANSLATIONS_ROOT.exists():
        return
    per_locale = {}
    low = []
    for loc_dir in sorted(TRANSLATIONS_ROOT.iterdir()):
        man = loc_dir / ACCURACY_FILE
        if not man.is_dir() and man.exists():
            data = json.loads(man.read_text(encoding="utf-8"))
            scores = []
            for rel, e in data.get("files", {}).items():
                s = e.get("quality_score")
                if isinstance(s, int):
                    scores.append(s)
                    if s < 85:
                        low.append({"locale": loc_dir.name, "file": rel, "score": s,
                                    "issues": e.get("quality_issues", "")})
            if scores:
                per_locale[loc_dir.name] = {
                    "files_scored": len(scores),
                    "mean": round(sum(scores) / len(scores), 1),
                    "min": min(scores),
                    "judge_model": next(iter(data.get("files", {}).values()), {}).get("judge_model"),
                }
    report = {"per_locale": per_locale, "below_threshold": sorted(low, key=lambda x: x["score"])}
    (TRANSLATIONS_ROOT / "_quality_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Translation quality report",
             "",
             "Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.",
             "",
             "| Locale | Files | Mean | Min | Judge |",
             "|--------|-------|------|-----|-------|"]
    for loc, s in sorted(per_locale.items()):
        lines.append(f"| {loc} | {s['files_scored']} | {s['mean']} | {s['min']} | {s['judge_model']} |")
    if low:
        lines += ["", f"## Files below 85 ({len(low)})", "",
                   "| Locale | File | Score | Issues |", "|--------|------|-------|--------|"]
        for x in sorted(low, key=lambda x: x["score"]):
            lines.append(f"| {x['locale']} | {x['file']} | {x['score']} | {x['issues']} |")
    (TRANSLATIONS_ROOT / "_quality_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote translations/_quality_report.md ({len(per_locale)} locales)", flush=True)


def _paths_for_rel(locale, rel):
    """Map a manifest key (source path under playbooks/) to (source, output)."""
    src = REPO_ROOT / rel
    out = TRANSLATIONS_ROOT / locale / "/".join(rel.split("/")[1:])  # drop leading 'playbooks/'
    return src, out


def remediate(locales, cfg, glossary_terms, min_score):
    """Ongoing quality remediation (no human review). For each file recorded
    below `min_score`:
      - if the low score was a judge/parse error, just RE-SCORE the existing
        translation (the translation itself was fine);
      - otherwise RE-TRANSLATE with escalation (higher temperature + naturalness
        hint) and keep whichever version scores higher.
    Repeatable and safe to run after every generation pass."""
    total_fixed = 0
    for locale in locales:
        manifest = load_manifest(locale)
        changed = False
        for rel, entry in list(manifest["files"].items()):
            score = entry.get("quality_score")
            if not isinstance(score, int) or score >= min_score:
                continue
            src, out = _paths_for_rel(locale, rel)
            if not src.exists() or not out.exists():
                continue
            is_meta = rel.endswith("playbook.json")
            is_error = str(entry.get("quality_issues", "")).startswith("judge error")
            src_text = src.read_text(encoding="utf-8")
            try:
                if is_error:
                    # Translation is fine; only the score failed to parse. Re-score.
                    if is_meta:
                        ms, mo = json.loads(src_text), json.loads(out.read_text(encoding="utf-8"))
                        s = "\n".join(str(ms.get(f, "")) for f in ("title", "description"))
                        t = "\n".join(str(mo.get(f, "")) for f in ("title", "description"))
                    else:
                        s, t = src_text, out.read_text(encoding="utf-8")
                    ns, ni = judge_translation(s, t, locale, cfg)
                    entry["quality_score"], entry["quality_issues"] = ns, ni
                elif is_meta:
                    mo = translate_playbook_json(src, locale, cfg, glossary_terms)
                    ms = json.loads(src_text)
                    s = "\n".join(str(ms.get(f, "")) for f in ("title", "description"))
                    t = "\n".join(str(mo.get(f, "")) for f in ("title", "description"))
                    ns, ni = judge_translation(s, t, locale, cfg)
                    if ns > score:
                        out.write_text(json.dumps(mo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                        entry["quality_score"], entry["quality_issues"] = ns, ni
                else:
                    nt = translate_markdown(src_text, locale, cfg, glossary_terms, quality_retry=True)
                    ns, ni = judge_translation(src_text, nt, locale, cfg)
                    if ns > score:
                        out.write_text(nt, encoding="utf-8")
                        entry["quality_score"], entry["quality_issues"] = ns, ni
                changed = True
                if entry["quality_score"] >= min_score:
                    total_fixed += 1
                print(f"  [remediate] {locale} {rel}: {score} -> {entry['quality_score']}", flush=True)
            except (ValueError, RuntimeError) as e:
                print(f"  [FAIL] {locale} {rel}: {e}", flush=True)
        if changed:
            save_manifest(locale, manifest)
    print(f"\nRemediation done. {total_fixed} file(s) now >= {min_score}.", flush=True)


def main():
    ap = argparse.ArgumentParser(description="Translate a playbook (and/or shared dependencies) into target locales.")
    ap.add_argument("--playbook", help="Playbook id (folder name)")
    ap.add_argument("--all-playbooks", action="store_true", help="Translate every core + supplemental playbook")
    ap.add_argument("--dependencies", action="store_true", help="Translate the shared playbooks/dependencies/*.md files")
    ap.add_argument("--remediate", action="store_true", help="Re-score judge errors and re-translate sub-threshold files, then exit")
    ap.add_argument("--apply-disclaimers", action="store_true", help="Insert/refresh the machine-translation disclaimer on existing translated README/platform files and set auto_translated in playbook.json, without re-translating. Idempotent. Defaults to all present locales when --locales is omitted.")
    ap.add_argument("--sync-github-only", action="store_true", help="Restore the verbatim English @github-only block (which the website strips and never shows) in existing translations, without re-translating. Idempotent. Defaults to all present locales when --locales is omitted.")
    ap.add_argument("--min-score", type=int, default=None, help="Remediation threshold (default: LLM_QUALITY_THRESHOLD or 85)")
    ap.add_argument("--locales", help="Comma-separated locale codes, e.g. zh-CN,es-LA,fr-FR (required except for --apply-disclaimers)")
    ap.add_argument("--jobs", type=int, default=1, help="Parallel workers across locales (each locale owns its own manifest, so this is race-free)")
    ap.add_argument("--retries", type=int, default=2, help="After the main pass, automatically re-attempt files that failed the structural gate this many times (failures are usually stochastic). Set 0 to disable.")
    ap.add_argument("--force", action="store_true", help="Retranslate even if up to date")
    ap.add_argument("--dry-run", action="store_true", help="Mask/round-trip only; do not call the model")
    args = ap.parse_args()

    if not args.playbook and not args.all_playbooks and not args.dependencies and not args.remediate and not args.apply_disclaimers and not args.sync_github_only:
        print("ERROR: specify --playbook <id>, --all-playbooks, --dependencies, --remediate, --apply-disclaimers, and/or --sync-github-only.", file=sys.stderr)
        sys.exit(2)

    # These backfills need no model/secrets - handle them up front and exit.
    if args.apply_disclaimers or args.sync_github_only:
        if args.locales:
            apply_locales = [x.strip() for x in args.locales.split(",") if x.strip()]
        elif TRANSLATIONS_ROOT.exists():
            apply_locales = sorted(d.name for d in TRANSLATIONS_ROOT.iterdir() if d.is_dir())
        else:
            apply_locales = []
        if args.apply_disclaimers:
            apply_disclaimers(apply_locales)
        if args.sync_github_only:
            sync_github_only(apply_locales)
        return

    cat, pb_dir = (None, None)
    if args.playbook:
        cat, pb_dir = find_playbook_dir(args.playbook)
        if not pb_dir:
            print(f"ERROR: playbook '{args.playbook}' not found under playbooks/{{core,supplemental}}/", file=sys.stderr)
            sys.exit(2)

    extra_headers = {}
    raw_headers = os.environ.get("LLM_EXTRA_HEADERS", "")
    if raw_headers:
        try:
            extra_headers = json.loads(raw_headers)
        except json.JSONDecodeError:
            print("ERROR: LLM_EXTRA_HEADERS is not valid JSON.", file=sys.stderr)
            sys.exit(2)

    cfg = {
        "provider": os.environ.get("LLM_PROVIDER", "openai").lower(),
        "base_url": os.environ.get("LLM_BASE_URL", ""),
        "model": os.environ.get("LLM_MODEL", "dry-run-model" if args.dry_run else ""),
        "extra_headers": extra_headers,
        "max_tokens": int(os.environ.get("LLM_MAX_TOKENS", "8192")),
        # Independent judge for quality scoring; default to a stronger model when
        # set (e.g. Opus judging Sonnet) to reduce self-evaluation bias.
        "judge_model": os.environ.get("LLM_JUDGE_MODEL", "").strip() or None,
        "quality_threshold": int(os.environ.get("LLM_QUALITY_THRESHOLD", "85")),
        "force": args.force,
        "dry_run": args.dry_run,
    }
    if not args.dry_run and (not cfg["base_url"] or not cfg["model"]):
        print("ERROR: set LLM_BASE_URL and LLM_MODEL (or use --dry-run).", file=sys.stderr)
        sys.exit(2)

    glossary_terms, prompt_version = load_glossary()
    if not args.locales:
        print("ERROR: --locales is required for translation/remediation.", file=sys.stderr)
        sys.exit(2)
    locales = [x.strip() for x in args.locales.split(",") if x.strip()]

    if args.remediate:
        min_score = args.min_score if args.min_score is not None else cfg["quality_threshold"]
        remediate(locales, cfg, glossary_terms, min_score)
        write_quality_report()
        return

    # Build the list of (playbook_id, category, dir) to translate.
    targets = []
    if args.all_playbooks:
        for c in CATEGORIES:
            cdir = PLAYBOOKS_ROOT / c
            if cdir.is_dir():
                for d in sorted(cdir.iterdir()):
                    if d.is_dir():
                        targets.append((d.name, c, d))
    elif args.playbook:
        targets.append((args.playbook, cat, pb_dir))

    def work(locale):
        """Translate all requested content for ONE locale. A locale owns its own
        translation_accuracy.json, so running locales concurrently is race-free."""
        changed = 0
        failures = []
        if args.dependencies:
            c, f = process_dependencies(locale, cfg, glossary_terms, prompt_version)
            changed += c
            failures.extend((locale, rel, err) for rel, err in f)
        for (pid, pcat, pdir) in targets:
            c, f = process_locale(pid, pcat, pdir, locale, cfg, glossary_terms, prompt_version)
            changed += c
            failures.extend((locale, rel, err) for rel, err in f)
        return changed, failures

    jobs = max(1, args.jobs)

    def run_round(locs):
        """Run work() for the given locales, in parallel when possible."""
        if jobs > 1 and len(locs) > 1:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=jobs) as ex:
                return list(ex.map(work, locs))
        return [work(loc) for loc in locs]

    print(f"Running {len(locales)} locales with {jobs} parallel worker(s)...", flush=True)
    results = run_round(locales)
    total_changed = sum(r[0] for r in results)
    all_failures = [x for r in results for x in r[1]]

    # Structural-gate failures (placeholder mismatch / span-count) are usually
    # stochastic - a fresh attempt on the same file almost always succeeds. Retry
    # only the locales that still have failures; already-written files are "up to
    # date" and skip, so each round re-attempts just the failures (no wasted work).
    retries = max(0, args.retries)
    attempt = 0
    while all_failures and attempt < retries:
        attempt += 1
        failed_locales = sorted({loc for (loc, _rel, _err) in all_failures})
        print(
            f"\nRetry {attempt}/{retries}: re-attempting {len(all_failures)} failed "
            f"file(s) across {len(failed_locales)} locale(s)...",
            flush=True,
        )
        round_results = run_round(failed_locales)
        total_changed += sum(r[0] for r in round_results)
        all_failures = [x for r in round_results for x in r[1]]

    print(f"\nDone. {total_changed} file(s) written.", flush=True)
    write_quality_report()
    if all_failures:
        print(f"{len(all_failures)} file(s) FAILED the structural gate after {retries} retr(y/ies):", flush=True)
        for locale, rel, err in all_failures:
            print(f"  - [{locale}] {rel}: {err}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
