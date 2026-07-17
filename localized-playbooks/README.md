<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Localized Playbooks (Human-Authored)

This directory holds **human-authored** localized playbooks uploaded by
translation/regional teams (for example, the China team for Simplified Chinese).
Each `<locale>/` subtree uses the same `core/` `supplemental/` `dependencies/`
layout as the top-level [`playbooks/`](../playbooks/) folder.

Unlike [`auto-translations/`](../auto-translations/) - which are machine
translations that must match the English source byte-for-byte outside of prose -
files here are **authoritative, human-owned, and may intentionally diverge from
English**: different screenshots/assets, changed commands, different tools, or
steps that only make sense for that region. The auto-translation pipeline never
reads, writes, scores, or overwrites anything in this folder.

## Three ways this folder is used

### 1. Localized version of an existing playbook (same `id`)
Use the **same playbook id** (folder name) as the English one. For that locale,
these files take precedence over the auto translation and the English source,
**per file**:

resolution order per file → `localized-playbooks/<locale>/` → `auto-translations/<locale>/` → `playbooks/` (English)

You can override as little as one file, or the whole playbook. Because these are
human-authored, they are **allowed to diverge** from English - change commands,
swap tools, add region-specific notes, etc.

| English source | Localized (`zh-CN`) |
|----------------|---------------------|
| `playbooks/core/comfyui-image-gen/README.md` | `localized-playbooks/zh-CN/core/comfyui-image-gen/README.md` |
| `playbooks/core/comfyui-image-gen/platform.md` | `localized-playbooks/zh-CN/core/comfyui-image-gen/platform.md` |
| `playbooks/core/comfyui-image-gen/playbook.json` | `localized-playbooks/zh-CN/core/comfyui-image-gen/playbook.json` |
| `playbooks/core/comfyui-image-gen/assets/…` | `localized-playbooks/zh-CN/core/comfyui-image-gen/assets/…` |

### 2. China-only (region-only) playbooks with a NEW `id`
Playbooks that have **no English counterpart** live here as complete, standalone
playbooks under a **new id** that does not exist in `playbooks/`:

```text
localized-playbooks/zh-CN/core/<china-only-id>/
  README.md
  platform.md            (optional)
  playbook.json          (full metadata: id, title, description, platforms, ...)
  assets/                (its own screenshots/files)
```

These are independent content - not translations of anything - so there is no
English fallback, no auto-translation, and no accuracy score for them.

### 3. Assets are first-class here
Because localized/region playbooks use **their own screenshots and files**, put
them in that playbook's own `assets/` folder under `localized-playbooks/…`
(don't rely on the English `assets/`). Reference them with the usual relative
path (`assets/<name>.png`).

## Rules
- **Same id = the localized version of that English playbook; new id = a
  region-only playbook.** Pick deliberately.
- `playbook.json` for a same-id override may contain just `id` + translated
  `title`/`description`; for a new region-only playbook it should be a full,
  valid `playbook.json` (like an English one).
- These files are **not** required to keep code byte-identical to English (that
  rule is only for the machine `auto-translations/`). Human authors own the
  content and may change commands/tools.
- Everything here is **hand-maintained**; the automated pipeline will not touch
  it and will not flag it as stale.

## Publishing
How these (localized overrides and region-only playbooks) surface on the public
website is handled by the **website team**. This folder is only the content home
and source of truth for human-authored localized playbooks.

## Current locales
- `zh-CN` - Simplified Chinese (scaffold ready for uploads)
