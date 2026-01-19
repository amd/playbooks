# Playbook Creation Guide


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

### Pre-installed Software Dropdowns

For software that comes pre-installed on the AMD Halo Developer Platform, use the `@preinstalled` tag to create a collapsible dropdown. This shows users that the software is already available while providing manual installation instructions if needed:

```markdown
<!-- @preinstalled -->
### Manual Installation

If you need to reinstall manually:

1. Download from [example.com](https://example.com)
2. Run the installer
3. Configure settings

./install.sh

<!-- @preinstalled:end -->
```

The dropdown displays with a green checkmark and the text "Already pre-installed on your AMD Halo Developer Platform!" When expanded, it shows a notice explaining the software is pre-configured, followed by your manual instructions.

> NOTE: This should only be used on **core** playbooks.

### Writing Tips

- List prerequisites upfront. Don't surprise users mid-playbook
- Include expected output so users know what success looks like
- Keep code blocks copy-friendly (avoid `$` or `>` prompts)

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
  "platforms": ["windows", "linux"],
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
| `platforms` | Yes | `["windows"]`, `["linux"]`, or `["windows", "linux"]` |
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
