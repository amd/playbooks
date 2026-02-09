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

Displays a green checkmark with "Already pre-installed on your AMD Halo Developer Platform!" that expands to show manual installation instructions.

**System setup** — Use `@setup` for configuration steps users need to perform:

```markdown
<!-- @setup:memory_config -->
```

Content displays directly since these are required steps, not optional reference info.

### Writing Tips

- List prerequisites upfront. Don't surprise users mid-playbook
- Include expected output so users know what success looks like
- Keep code blocks copy-friendly (avoid `$` or `>` prompts)

### Testing Tags

Use `@test` tags to make existing code blocks testable. These tags **wrap your existing code** and are picked up by CI to run automated tests. The HTML comment tags themselves are invisible to website visitors, but the wrapped code remains visible by default. Add `hidden=true` to hide the code block from the website if needed (e.g., for test-only setup commands).

**Basic syntax — wrap existing code blocks:**

```markdown
<!-- @test:id=install-deps platform=all timeout=300 -->
```bash
pip install transformers accelerate
```
<!-- @test:end -->
```

The test tags wrap the code block that users see. No duplication needed — the same code that appears in the playbook is what gets tested.

**Test attributes:**

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `id` | Yes | — | Unique identifier for the test (use kebab-case) |
| `platform` | No | `all` | Target platform: `windows`, `linux`, or `all` |
| `timeout` | No | `300` | Maximum execution time in seconds |
| `continue_on_error` | No | `false` | If `true`, test failure won't fail the CI job |
| `depends_on` | No | — | Comma-separated list of test IDs that must pass first |
| `hidden` | No | `false` | If `true`, hides the code block from the website (useful for test-only setup) |

**Supported languages:**

| Language tag | Execution |
|--------------|-----------|
| `bash`, `sh`, `shell` | PowerShell on Windows, Bash on Linux |
| `cmd`, `batch` | Windows CMD |
| `powershell`, `pwsh`, `ps1` | PowerShell |
| `python` | Python interpreter |

**Example: Chaining tests with dependencies**

Use `depends_on` to create test chains where later tests only run if their dependencies pass:

```markdown
### Create Virtual Environment

<!-- @test:id=create-venv platform=windows timeout=60 -->
```cmd
python -m venv myenv
myenv\Scripts\activate.bat
```
<!-- @test:end -->

### Install Dependencies

<!-- @test:id=install-deps platform=all timeout=300 depends_on=create-venv -->
```bash
pip install transformers torch
```
<!-- @test:end -->

### Run the Script

<!-- @test:id=run-script platform=all timeout=60 depends_on=install-deps -->
```bash
python run_model.py --help
```
<!-- @test:end -->
```

In this example:
- `install-deps` only runs if `create-venv` passes
- `run-script` only runs if `install-deps` passes
- If `create-venv` fails, both `install-deps` and `run-script` are skipped

**Example: Platform-specific tests**

Combine with `@os` tags for platform-specific instructions:

```markdown
<!-- @os:windows -->
<!-- @test:id=setup platform=windows timeout=120 -->
```cmd
pip install torch
python -c "import torch; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=setup platform=linux timeout=120 -->
```bash
pip3 install torch
python3 -c "import torch; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->
```

**Example: Verification tests (not shown to users)**

For tests that verify things but shouldn't appear in the playbook, place them after visible content:

```markdown
| [run_llm.py](assets/run_llm.py) | Basic LLM script |

<!-- @test:id=verify-scripts platform=all timeout=30 -->
```python
import os, sys
missing = [f for f in ['run_llm.py'] if not os.path.exists(f)]
if missing:
    sys.exit(1)
```
<!-- @test:end -->

Both scripts support...
```

**Best practices:**

1. **Wrap, don't duplicate**: Put test tags around existing code blocks instead of writing separate test code
2. **Use dependency chains**: Use `depends_on` to skip downstream tests when prerequisites fail
3. **Keep tests fast**: Use appropriate timeouts; most tests should complete in under 60 seconds
4. **Handle missing hardware**: CI machines may not have GPUs; tests should handle this gracefully
5. **Test the happy path**: Focus on verifying instructions work, not edge cases

**Running tests locally:**

```bash
python .github/scripts/run_playbook_tests.py --playbook your-playbook-id --platform windows
```

**CI behavior:**

- Tests run automatically on PRs that modify playbook files
- Tests run on self-hosted runners tagged with `Windows` and `halo`
- Tests are sorted by dependencies and run in order
- If a test fails, dependent tests are automatically skipped
- Test results are uploaded as artifacts for debugging

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
