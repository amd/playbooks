<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Playbook Creation Guide
> [!IMPORTANT]
> We are **not currently accepting new playbook proposals** from the community at this stage. However, we welcome collaborations, idea exchanges, and contributions that help advance this space. If you encounter issues or have feedback that can help us identify and diagnose problems, please [open an issue](https://github.com/amd/playbooks/issues).

## Design Principles

**A playbook is not a setup guide.** Users should feel accomplished when they finish. They should feel they learned something meaningful, built something real, and can't wait to explore further.

### Core Guidelines

1. **Create a moment of success.** Users should *see something happen*: an image appears, a model responds, a server comes alive.
2. **Teach, don't just instruct.** Explain *why* things work, not just which buttons to click.
3. **Spark curiosity.** End with "Next Steps" that open doors to further exploration.
4. **Respect the reader.** Be concise, be clear, and trust them to follow along.

### Reference Example

See `playbooks/core/comfyui-image-gen/README.md` for a well-structured playbook that demonstrates these principles. See [Previewing](#previewing) to view it in the browser.

---

## Folder Structure

```text
playbooks/
├── core/                    # Essential playbooks for getting started
├── supplemental/            # Additional playbooks for specific use cases
├── backup/                  # Unpublished/draft playbooks
└── README.md                # This file
```

Each playbook lives in its own folder:

```text
playbook-name/
├── playbook.json            # Metadata (required)
├── README.md                # Content (required)
├── platform.md              # Platform configurations (required for core, optional for supplemental)
└── assets/                  # Images and files (optional)
```


### Assets

Reference images using relative paths:

```markdown
![Screenshot](assets/screenshot.png)
```

- Max 500 KB per file
- Formats: PNG, JPEG, GIF, WebP, SVG
- Include screenshots at key UI moments

---

## The `README.md` File

Write your playbook content in Markdown format. Images, tables, code, and other elements are supported.

**Recommended structure:**

| Section | Content |
|---------|---------|
| **Overview** | What is this tool? Why is it exciting? (2-3 sentences) |
| **What You'll Learn** | 3-5 concrete outcomes |
| **Getting Started** | First hands-on step—get users into the tool quickly |
| **Core Concepts** | Teach the mental model (tables and diagrams help) |
| **Main Activity** | Where users achieve the payoff moment |
| **Next Steps** | 3-5 paths forward with links to resources and official documentation |

### OS-Specific Content

Use HTML comments to mark platform-specific sections:

```markdown
<!-- @os:windows -->
Windows-only content
<!-- @os:end -->

<!-- @os:linux -->
Linux-only content
<!-- @os:end -->
```

Content outside `@os` tags is always shown. Keep blocks focused—only tag the parts that differ.

### Device-Specific Content

Use `@device` tags for instructions that apply to specific hardware. Supports comma-separated values to target multiple devices:

```markdown
<!-- @device:halo -->
STX Halo-only instructions
<!-- @device:end -->

<!-- @device:halo,stx -->
Instructions for both Halo and STX Point
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt -->
Instructions for discrete Radeon GPUs
<!-- @device:end -->
```

| Device ID | Hardware | Product Name |
|-----------|----------|--------------|
| `halo` | STX Halo | AMD Ryzen™ AI Max+ |
| `stx` | STX Point | AMD Ryzen™ AI 300 HX |
| `krk` | Krackan Point | AMD Ryzen™ AI 300 |
| `rx7900xt` | Radeon RX 7900 XT | AMD Radeon™ 7000 Series Graphics |
| `rx9070xt` | Radeon RX 9070 XT | AMD Radeon™ 9000 Series Graphics |

Content outside `@device` tags is always shown. Use `<!-- @device:all -->` to explicitly mark content for all devices. A device selector appears on the playbook page when `@device` tags are detected.

### Shared Content Tags

Use these tags to pull in shared content from `playbooks/dependencies/`. Both reference items defined in `registry.json`.

| Tag | Purpose | Display |
|-----|---------|---------|
| `@require` | Pre-installed software | Collapsible dropdown (optional info) |
| `@setup` | System configuration steps | Displayed directly (required steps) |

**Pre-installed software** — Use `@require` for software that comes pre-installed on the AMD Halo Developer Platform:

```markdown
<!-- @require:comfyui -->
<!-- @require:comfyui,pytorch -->   <!-- multiple dependencies in one dropdown -->
```

Displays a green checkmark with "Already pre-installed on your AMD Ryzen™ AI Halo Developer Platform!" that expands to show manual installation instructions.

**System setup** — Use `@setup` for configuration steps users need to perform:

```markdown
<!-- @setup:memory_config -->
```

Content displays directly since these are required steps, not optional reference info.

### Writing Tips

- List prerequisites upfront. Don't surprise users mid-playbook
- Include expected output so users know what success looks like
- Keep code blocks copy-friendly (avoid `$` or `>` prompts)
- Follow the [AMD Branding Guide](../AMD_BRANDING_GUIDE.md) for correct product naming and trademark usage

### AMD Product Branding

When referencing AMD products in your playbooks, follow the [AMD Branding Guide](../AMD_BRANDING_GUIDE.md) to ensure consistent and correct usage:

- **First mention**: Use the full product name with trademark symbol (™)
- **Subsequent mentions**: Use the approved shortened form
- **JSON files**: Use `\u2122` for trademark symbols instead of typing ™ directly

---

## The `platform.md` File

Documents pre-installed software, model paths, and platform-specific prerequisites. **Required for `core` playbooks**, since they assume dependencies are preinstalled on the system. Optional for `supplemental` playbooks.

See `playbooks/core/comfyui-image-gen/platform.md` for an example.

---

## Editing a Playbook

All playbook folders have already been created. To edit a playbook:

1. Navigate to the appropriate folder (e.g., `playbooks/core/lmstudio-rocm-llms/`)
2. Edit the `playbook.json` file to update metadata
3. Edit the `README.md` file to update content

> **Note:** Do not create new folders. All playbook folders are pre-created and managed centrally.

---

## The `playbook.json` File

```json
{
  "id": "my-playbook",
  "title": "My Playbook Title",
  "description": "Brief description for the card (100-150 chars)",
  "time": 45,
  "supported_platforms": { "halo": ["windows", "linux"] },
  "difficulty": "intermediate",
  "published": true,
  "tags": ["tag1", "tag2"]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Must match folder name |
| `title` | Yes | Display title |
| `description` | Yes | Card description (100–150 characters) |
| `time` | Yes | Completion time in minutes |
| `supported_platforms` | Yes | Device → OS map controlling which platforms/devices appear in the UI, e.g. `{ "halo": ["windows", "linux"] }` |
| `tested_platforms` | No | Device → OS map of CI-tested combinations, e.g. `{ "halo": ["windows", "linux"], "krk": ["linux"] }` |
| `required_platforms` | No | Subset of `tested_platforms` where CI failure blocks merges |
| `published` | Yes | Set `true` to show on website |
| `difficulty` | No | `"beginner"`, `"intermediate"`, or `"advanced"` |
| `isNew` | No | Shows "New" badge |
| `isFeatured` | No | Displays prominently at top |
| `tags` | No | Keywords for filtering |

---

## Previewing

First, install [Node.js 20.19.6](http://nodejs.org/pt/blog/release/v20.19.6) version 
```bash
cd website
npm install    # first time only
npm run dev
```

Visit `http://localhost:3000/playbooks/<playbook-id>` to preview your playbook.
