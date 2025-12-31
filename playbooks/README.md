# Playbook Creation Guide

This folder contains all STX Halo™ playbooks. But before we get into folder structures and metadata, let's talk about what makes a playbook *great*.

---

## The Soul of a Great Playbook

**A playbook is not a setup guide.** Users should feel accomplished when they finish—they've learned something meaningful, built something real, and can't wait to explore further.

### The Golden Rules

1. **Create a moment of success.** Every playbook should have a "wow" moment where the user *sees something happen*. An image appears. A model responds. A server comes alive. This is the emotional anchor of the experience.

2. **Teach, don't just instruct.** Explain *why* things work, not just *how* to click buttons. Users should leave understanding the system, not just having copy-pasted commands.

3. **Spark curiosity.** End with "Next Steps" that open doors. Where can they go from here? What else is possible? A great playbook is a launchpad, not a destination.

4. **Respect the reader.** Write like you're pair-programming with a smart colleague, not lecturing a child. Be concise, be clear, and trust them to follow along.

### Study the Best Example

Before writing your playbook, **read `playbooks/core/comfyui-image-gen/README.md`** end to end. Notice how it:

- Opens with an **Overview** that explains *what the tool is and why it matters*
- Lists **What You'll Learn** upfront so users know the journey ahead
- **Teaches concepts** (pipeline components, what each node does) not just clicks
- Gets to the **first image generation** quickly—the payoff moment
- Provides a **rich "Next Steps" section** with specific, actionable paths forward
- Uses images to show the UI, reducing confusion
- Maintains an enthusiastic but professional tone throughout

This is the bar. Match it.

---

## Anatomy of a Playbook

### The "What You'll Learn" Section

Immediately after your overview, tell users what they'll accomplish:

```markdown
## What You'll Learn

- How to load and run the Z Image Turbo template
- Understanding diffusion pipeline components
- Generating images and tuning generation parameters
- Saving and sharing workflows
```

This isn't just a table of contents—it's a promise. Users should look at this list and think, "Yes, I want to know all of that."

### The Teaching Moments

Don't just say "click this button." Explain the system:

> **Good:** "The KSampler node controls the core diffusion process. The `steps` parameter determines how many denoising iterations the model performs—turbo models are distilled to work with fewer steps (4–10), unlike traditional diffusion models that need 20–50."

> **Bad:** "Set steps to 6 and click Run."

Tables work well for parameter explanations:

| Parameter | What It Controls | Recommended Values |
|-----------|------------------|-------------------|
| **steps** | Number of denoising iterations | 4–10 |
| **cfg** | How closely to follow the prompt | 1.0–2.0 |

### The Payoff Moment

Every playbook needs a clear moment where the user achieves something tangible:

> "Your generated image appears in the **Save Image** node and is saved to the `output/` folder."

> "You should see `Server running on http://localhost:3000`. Open your browser and you'll see your chatbot interface ready for input."

This is the emotional core. Build toward it.

### The "Next Steps" Section

Never end abruptly. Always provide at least 3-4 concrete next steps:

```markdown
## Next Steps

- **Explore LoRA nodes**: Apply style adapters without retraining
- **Add negative prompts**: Guide the model away from unwanted features
- **Build custom workflows**: Chain generations, add upscaling, create variations
- **Browse community workflows**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples)
```

End with an inspiring closing line that captures the spirit of continued exploration:

> "ComfyUI's strength is experimentation: connect nodes differently, adjust parameters, and observe how each change affects the output. This hands-on exploration builds intuition for how diffusion models work."

---

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
├── platform.md              # Platform configurations (optional)
└── assets/                  # Images and files (optional)
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

**Include screenshots liberally.** A picture of the UI with annotations is worth a hundred words of description. Show users what they should see at key moments.

---

## The `platform.md` File

Playbooks may include an optional `platform.md` file that documents the expected platform configurations for that playbook. This file specifies:

- Pre-installed software versions and locations
- Required models and their file paths
- Any platform-specific prerequisites

### Purpose

The `platform.md` file serves as a reference for:

1. **System administrators** who need to pre-configure machines with the correct setup
2. **Users** who want to verify their environment matches the expected configuration
3. **Documentation** of exact versions and file locations used in testing

### Structure

A typical `platform.md` file includes sections for each supported platform (Windows, Linux) with:

- Installation paths and versions
- Required model files and their locations
- Any platform-specific notes

### Example

See `playbooks/core/comfyui-image-gen/platform.md` for a complete example showing:

- Windows portable installation location
- Required model files organized by type (text encoders, LoRAs, diffusion models, VAE)
- Linux user responsibilities

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

**Recommended structure (based on comfyui-image-gen):**

    ## Overview

    What is this tool/technology? Why does it matter? What makes it 
    exciting or powerful? Set the stage with 2-3 sentences that hook 
    the reader.

    ## What You'll Learn

    - Concrete skill or knowledge #1
    - Concrete skill or knowledge #2
    - Concrete skill or knowledge #3
    - The tangible outcome they'll achieve

    ## Getting Started (or similar)

    The first hands-on step. Get users into the tool as quickly 
    as possible.

    ## Core Concepts / Understanding [X]

    Teach the mental model. Tables and diagrams work well here.

    ## Doing The Thing

    The main activity—where users achieve the payoff moment.

    ## Customization / Parameters / Going Deeper

    How to modify and experiment. Give users agency.

    ## Next Steps

    3-5 concrete paths forward. Links to resources. An inspiring 
    closing line about continued exploration.

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

Before setting `"published": true`, verify both **style** and **technical** requirements:

### Style Requirements

- [ ] **Overview hooks the reader**—explains what the tool is and why it's exciting
- [ ] **"What You'll Learn" section exists** with 3-5 concrete outcomes
- [ ] **Concepts are explained**, not just steps listed
- [ ] **Clear payoff moment**—user sees something tangible happen
- [ ] **"Next Steps" section exists** with 3-5 paths forward
- [ ] **Images included** at key UI moments
- [ ] **Tone is engaging**—reads like a knowledgeable friend, not a manual

### Technical Requirements

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
- [ ] If applicable, `platform.md` documents required configurations and model files

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

## Writing Style Checklist

Before you start writing, internalize these principles:

### Do This

- [ ] **Lead with excitement.** Why is this technology interesting? What can users create?
- [ ] **Promise outcomes.** "What You'll Learn" should make users eager to continue
- [ ] **Explain the why.** Don't just give instructions—teach concepts
- [ ] **Create a payoff moment.** Users should *see something happen*
- [ ] **End with "Next Steps."** Open doors, don't close them
- [ ] **Use images generously.** Show the UI, show the output, reduce guesswork
- [ ] **Write like a knowledgeable friend.** Enthusiastic but not condescending

### Avoid This

- [ ] **"Click this, type that" syndrome.** Instructions without understanding
- [ ] **Ending abruptly.** "Run the command. Done." leaves users stranded
- [ ] **Wall-of-text explanations.** Use tables, code blocks, and formatting
- [ ] **Assuming setup is the goal.** Setup is a means to an end—the end is learning
- [ ] **Dry, manual-style writing.** Playbooks should feel exciting, not like documentation

---

## Technical Tips

1. **List prerequisites upfront**: Don't surprise users mid-playbook
2. **Use numbered steps**: Makes it easy to follow along
3. **Include expected output**: Show what success looks like
4. **Add troubleshooting sections**: Anticipate common issues
5. **Keep code blocks copy-friendly**: Avoid prompts like `$` or `>` in commands
6. **Test on a fresh system**: Ensure all dependencies are documented
