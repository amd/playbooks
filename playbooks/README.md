# Playbook Creation Guide

This folder contains all STX Halo™ playbooks—step-by-step guides for AI development tasks.

## Folder Structure

```text
playbooks/
├── core/                    # Essential playbooks for getting started
├── supplemental/            # Additional playbooks for specific use cases
├── backup/                  # Unpublished/draft playbooks
└── README.md                # This file
```

Each playbook lives in its own folder with two required files:

```text
playbook-name/
├── playbook.json            # Metadata (required)
├── README.md                # Content (required)
└── assets/                  # Images and files (optional)
    └── screenshot.png
```

---

## The `assets/` Folder

Playbooks can include an optional `assets/` folder for images and other files referenced in the README.

### Usage

Reference assets in your README using relative paths:

```markdown
![Screenshot](assets/screenshot.png)
```

### Requirements

- **Maximum file size**: 500 KB per asset
- **Supported formats**: PNG, JPEG, GIF, WebP, SVG
- Use descriptive filenames (e.g., `step1-output.png` instead of `image1.png`)

---

## Editing a Playbook

All playbook folders have already been created. To edit a playbook:

1. Navigate to the appropriate folder (e.g., `playbooks/core/lmstudio-rocm-llms/`)
2. Edit the `playbook.json` file to update metadata
3. Edit the `README.md` file to update content

> **Note:** Do not create new folders. All playbook folders are pre-created and managed centrally.

---

## The `playbook.json` File

This file contains all metadata for your playbook:

```json
{
  "id": "my-playbook",
  "title": "My Playbook Title",
  "description": "A brief description shown on the playbook card",
  "time": 45,
  "platforms": ["windows", "linux"],
  "difficulty": "intermediate",
  "isNew": false,
  "isFeatured": false,
  "published": true,
  "tags": ["tag1", "tag2", "tag3"]
}
```

### Required Fields

| Field         | Type    | Description                                                                 |
|---------------|---------|-----------------------------------------------------------------------------|
| `id`          | string  | Must match the folder name exactly                                          |
| `title`       | string  | Display title for the playbook                                              |
| `description` | string  | Short description for cards (aim for 100–150 characters)                    |
| `time`        | number  | Estimated completion time in minutes                                        |
| `platforms`   | array   | Supported platforms: `["windows"]`, `["linux"]`, or `["windows", "linux"]`  |
| `published`   | boolean | Set to `true` to show on the website                                        |

### Optional Fields

| Field        | Type    | Default | Description                                            |
|--------------|---------|---------|--------------------------------------------------------|
| `difficulty` | string  | —       | One of: `"beginner"`, `"intermediate"`, `"advanced"`   |
| `isNew`      | boolean | `false` | Shows a "New" badge on the playbook                    |
| `isFeatured` | boolean | `false` | Displays the playbook prominently at the top           |
| `tags`       | array   | `[]`    | Keywords for filtering and search                      |

---

## The `README.md` File

Write your playbook content in Markdown. The first `# Heading` becomes the page title.

**Example structure:**

    # My Playbook Title

    Introduction paragraph explaining what users will learn.

    ## Prerequisites

    - List required software
    - Previous knowledge needed
    - Hardware requirements

    ## Step 1: First Step

    Detailed instructions...

    ## Step 2: Second Step

    More instructions...

    ## Conclusion

    Summary and next steps.

---

## OS-Specific Content

When instructions differ between Windows and Linux, use special HTML comments to mark platform-specific sections. The website will filter content based on the user's selected platform.

### Syntax

Use these tags to wrap OS-specific content:

    <!-- @os:windows -->
    Content shown only on Windows
    <!-- @os:end -->

    <!-- @os:linux -->
    Content shown only on Linux
    <!-- @os:end -->

    <!-- @os:all -->
    Content shown on all platforms (useful inside a platform block)
    <!-- @os:end -->

### Example

Here's how to write installation instructions that differ by platform:

    ## Installation

    First, install the required dependencies:

    <!-- @os:windows -->
    Open PowerShell as Administrator and run:

    ```powershell
    winget install Python.Python.3.11
    ```
    <!-- @os:end -->

    <!-- @os:linux -->
    Use your package manager:

    ```bash
    sudo apt update && sudo apt install python3.11 python3.11-venv
    ```
    <!-- @os:end -->

    Now verify the installation:

    <!-- @os:windows -->
    ```powershell
    python --version
    ```
    <!-- @os:end -->

    <!-- @os:linux -->
    ```bash
    python3 --version
    ```
    <!-- @os:end -->

### How It Works

| View              | Behavior                                                              |
|-------------------|-----------------------------------------------------------------------|
| All Platforms     | Shows all content with labels like "> **Windows only:**" before each |
| Windows           | Shows only Windows blocks; hides Linux blocks                         |
| Linux             | Shows only Linux blocks; hides Windows blocks                         |

Content **outside** of `@os` tags is always shown regardless of platform selection.

### Best Practices

1. **Keep blocks focused**: Put only the differing content inside `@os` tags
2. **Maintain parallel structure**: If you have a Windows block, include a Linux equivalent
3. **Use for commands**: Most differences are in terminal commands, paths, and package managers
4. **Don't overuse**: If 90% of your content is the same, only tag the differences

---

## Categories

| Category                       | Purpose                                                  |
|--------------------------------|----------------------------------------------------------|
| `core/`                        | Essential playbooks for getting started                  |
| `supplemental/`                | Advanced or specialized playbooks for specific use cases |
| `backup/`                      | Unpublished or draft playbooks                           |

---

## Publishing Checklist

Before setting `"published": true`:

- [ ] `id` matches folder name
- [ ] Title is clear and descriptive
- [ ] Description fits on a card (100–150 characters)
- [ ] Time estimate is realistic
- [ ] Correct platforms are specified
- [ ] All steps have been tested on each listed platform
- [ ] OS-specific tags are properly closed with `<!-- @os:end -->`
- [ ] Code blocks have language hints (e.g., `python`, `bash`, `powershell`)
- [ ] Links are valid and use HTTPS
- [ ] No placeholder or TODO content remains

---

## Previewing Your Playbook

Before publishing, preview your playbook on the local development website to verify formatting and layout.

### Prerequisites

- [Node.js](https://nodejs.org/) v18 or higher installed

### Running the Preview Server

1. Open a terminal and navigate to the `website` folder:

   ```bash
   cd website
   ```

2. Install dependencies (first time only):

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Open your browser to [http://localhost:3000](http://localhost:3000)

### Viewing Your Playbook

- **All playbooks**: Visit `http://localhost:3000` and scroll to the playbooks section
- **Specific playbook**: Visit `http://localhost:3000/playbooks/<playbook-id>`
  - Example: `http://localhost:3000/playbooks/lmstudio-rocm-llms`

---

## Tips for Great Playbooks

1. **Start with the end goal**: Tell users what they'll accomplish
2. **List prerequisites upfront**: Don't surprise users mid-playbook
3. **Use numbered steps**: Makes it easy to follow along
4. **Include expected output**: Show what success looks like
5. **Add troubleshooting sections**: Anticipate common issues
6. **Keep code blocks copy-friendly**: Avoid prompts like `$` or `>` in commands
7. **Test on a fresh system**: Ensure all dependencies are documented
