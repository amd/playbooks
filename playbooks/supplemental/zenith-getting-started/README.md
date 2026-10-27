<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

Your **Ryzen™ AI Halo** arrives with Windows already set up for local AI development. The image ships AMD's AI stack — **Lemonade Server**, **ComfyUI**, and a **ROCm™-enabled PyTorch** — alongside **Microsoft Project Zenith**, a preconfigured Windows developer environment with a modern toolchain and agentic terminal apps.

This playbook is the tour. You'll find out what is already installed, what has been preconfigured for you, and — most importantly — how to point Zenith's AI tooling at a model running on your own hardware instead of the cloud.

That last part matters. **Intelligent Terminal and GitHub Copilot CLI both sign in to cloud services by default.** They also both accept a custom model endpoint, which is exactly what Lemonade provides. Wiring them together gives you an agentic coding environment that runs entirely on your own machine — private, offline-capable, and with no metered tokens.

## What You'll Learn

By the end of this playbook you will be able to:

* **Identify the AI software** that ships on your Ryzen AI Halo and know what each piece is for.
* **Recognise the Windows and toolchain settings** that have been preconfigured for you.
* **Start Lemonade Server**, download a model, and confirm its OpenAI-compatible endpoint is live.
* **Connect Intelligent Terminal** to your local Lemonade model.
* **Connect GitHub Copilot CLI** to the same local endpoint.
* **Choose between local and cloud models** depending on the task.

## Check for Software Updates

<!-- @require:software-update -->

## Setting the Memory Configuration

<!-- @require:memory-config -->

---

## Part 1 — What's On Your Machine

### The AMD AI stack

These are the components that make the Ryzen AI Halo a local AI machine. All three are preinstalled.

| Software | What it does | How to start it |
|----------|--------------|-----------------|
| **Lemonade Server** | Local LLM server with an OpenAI-compatible API. Runs models on your GPU and NPU, and is what lets other apps use local models. Models are downloaded separately — none ship with the image. | Start menu → **Lemonade Server** |
| **ComfyUI** | Node-graph application for image and diffusion models. Self-contained with its own runtime. | Desktop shortcut |
| **PyTorch with ROCm** | GPU-accelerated PyTorch, preinstalled into the system Python. Write Python that runs on the Radeon™ iGPU with no setup. | `python` in any terminal |

> [!NOTE]
> **Lemonade Server does not start automatically when you log in.** You need to launch it before any app can use a local model. Part 2 covers this.

Check that ROCm PyTorch can see your GPU:

<!-- @test:id=zenith-torch-check timeout=120 -->
```powershell
python -c "import torch; print('GPU available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"
```
<!-- @test:end -->

ROCm reports through the same API as CUDA, so `GPU available: True` means your Radeon iGPU is ready for PyTorch workloads.

### The Zenith developer toolchain

Project Zenith adds a modern Windows development environment. The headline additions:

| Tool | What it's for |
|------|---------------|
| **Intelligent Terminal** | Terminal with a built-in AI agent pane. Ask for a command in plain language instead of recalling syntax. Open the agent pane with `Ctrl+Shift+.` |
| **GitHub Copilot CLI** | Agentic coding in the terminal — plans multi-step work, edits files, runs commands with your approval. Has its own profile in the Terminal dropdown, or run `copilot`. |
| **WSL 2 with Ubuntu** | A full Linux environment for Linux-first ML tooling. Run `wsl` to enter. `wslc` creates and runs Linux containers. |
| **uv** | Fast Python package and environment manager. Use `uv venv` and `uv pip install` in place of pip. |
| **PowerShell 7** | The default shell, replacing the older Windows PowerShell 5. |
| **PowerToys** | Utilities including Command Palette (`Win+Alt+Space`) and FancyZones window tiling. |

Also included: Git, Visual Studio Code, Node.js with nvm, .NET SDK 10, GitHub CLI, Azure CLI, Windows App CLI (`winapp`), Oh My Posh, and Coreutils for Windows.

### Windows settings already configured for you

Zenith presets a number of Windows and shell settings that developers commonly change by hand. Nothing here is required reading — it's listed so you know what was deliberate rather than accidental.

| Setting | Configured as | Why it helps |
|---------|---------------|--------------|
| Default shell | PowerShell 7 | Modern shell features; the older PowerShell 5 is no longer the default |
| Long path support | Enabled | Deep dependency trees (common in ML projects) no longer hit the 260-character path limit |
| File Explorer | Full path shown in title bar | Easier to see where you are when working across many project folders |
| Appearance | Dark mode | Set as the default for new users |
| Terminal font | Cascadia Mono NF | Includes the glyphs that prompt themes and CLI tools expect |
| Prompt | Oh My Posh | Shows Git branch and Python environment in your prompt |
| `ls` behaviour | Coreutils | `ls`, `cat`, and `grep` behave as they do on Linux |
| Taskbar | Terminal, VS Code, AMD Ryzen AI Developer Center pinned | The tools you'll use most are one click away |

---

## Part 2 — Running a Local Model

Lemonade is the engine behind everything in Part 3. Start it first.

### Step 1 — Start Lemonade Server

Open **Lemonade Server** from the Start menu. It does not launch automatically at logon, so you'll need to do this after each reboot.

Confirm it's running:

<!-- @require:lemonade-ready -->

```powershell
curl.exe http://localhost:13305/api/v1/health
```

### Step 2 — Download a model

**No models ship with the image** — you choose and download what you need. Lemonade's Model Manager lists everything available; open the Lemonade web UI and browse, or pull one from the command line.

Two recommendations for agentic work on a Ryzen AI Halo:

| Model | Type | Why choose it |
|-------|------|---------------|
| **Qwen3.8 27B** | Dense | Every parameter is used for each token, which generally means stronger reasoning on hard problems. Slower to generate, since speed here is limited by memory bandwidth. |
| **Qwen3.6 35B MTP** | Mixture-of-experts | Only a fraction of its parameters activate per token, so it generates noticeably faster than a dense model of similar size while still being a large model. Usually the better default for interactive agent work. |

Both fit comfortably in the Ryzen AI Halo's unified memory. If you're unsure, start with the MoE model — the responsiveness matters more than raw capability for day-to-day coding, and you can always switch.

> [!TIP]
> This is where the Ryzen AI Halo's memory capacity pays off: you can keep large models resident locally rather than paying per token. Note that generation speed is governed by memory *bandwidth* rather than capacity, so a MoE model of a given size will feel faster than a dense one.

### Step 3 — Find your model ID

The agent tools need the model ID exactly as Lemonade reports it. List what's loaded:

<!-- @test:id=zenith-lemonade-models timeout=60 -->
```powershell
curl.exe http://localhost:13305/api/v1/models
```
<!-- @test:end -->

Note the `id` field for the model you downloaded. You'll paste it in the next part.

> [!TIP]
> Your Lemonade endpoint is `http://localhost:13305/v1`. No API key is needed, but some apps require the field to be non-empty — enter any placeholder text when asked.

---

## Part 3 — Connecting the Zenith Agent Tools

Both Intelligent Terminal and Copilot CLI are cloud-first out of the box. Here's how to point them at the model you just started.

> [!IMPORTANT]
> **You must sign in to GitHub before you can configure a local model.** Both tools below put custom provider configuration behind GitHub account authentication, so the sign-in step is unavoidable even though your end state is entirely local. A paid **Copilot subscription is not required** — a free GitHub account is enough — but the account sign-in itself cannot be skipped or deferred. Expect a browser authentication step before you reach any BYOM or custom-endpoint settings.

### Connecting Intelligent Terminal

Intelligent Terminal runs on top of an agent — either GitHub Copilot CLI or OpenCode. Custom model endpoints are supported through those agents, so pick one of them during first-run setup.

1. Open **Intelligent Terminal** from the Start menu. It's a separate app from the classic Windows Terminal.
2. On first run, choose **GitHub Copilot** or **OpenCode** as your agent and complete the setup prompts.
3. Open the agent's settings and find the **BYOM** (bring your own model) or **Custom endpoint or local model** section.
4. Select **Add New** and enter:
   - **Base URL:** `http://localhost:13305/v1`
   - **Model ID:** the `id` you noted in Part 2, Step 3
5. Save, then select your new provider from the model dropdown. Custom models appear with a `(BYOK)` suffix.
6. Press `Ctrl+Shift+.` to open the agent pane and ask it something.

Your prompts now go to the model running on your own GPU and NPU. Nothing leaves the machine.

> [!NOTE]
> Intelligent Terminal stores endpoint credentials in Windows Credential Manager rather than a settings file. To change a key later, remove the endpoint and add it again.

### Connecting GitHub Copilot CLI

Copilot CLI is already on your PATH and has a dedicated profile in the Terminal dropdown.

1. Open **Windows Terminal** and select the **GitHub Copilot** profile, or run `copilot` from any shell.
2. Complete the initial setup if you haven't already.
3. Configure a custom OpenAI-compatible provider pointing at `http://localhost:13305/v1` with your model ID.

Useful commands once you're in:

| Command | What it does |
|---------|--------------|
| `/plan` | Drafts an implementation plan before writing any code |
| `Shift+Tab` | Cycles agent modes, including autopilot |
| `/resume` | Picks up a previous session with its context |

### Choosing local or cloud

Both tools can switch between providers, which makes a two-tier workflow practical:

- **Local (Lemonade)** — day-to-day coding, refactoring, explaining code, iterating. Unlimited, private, works offline.
- **Cloud** — occasional problems where you want a frontier model's extra capability.

Most work fits comfortably in the first category, which is the point of having this much local compute.

---

## Where to Go Next

| If you want to… | Try this playbook |
|-----------------|-------------------|
| Learn Lemonade in depth — vision, speech, image generation, backends | **Getting Started with Lemonade** |
| Generate images with a node-based workflow | **ComfyUI Image Generation** |
| Use a local model inside VS Code | **VS Code with Qwen3 Coder** |
| Build agentic workflows on a local server | **OpenClaw with Lemonade Server** |
| Fine-tune a model on your own data | **Unsloth LLM Fine-tuning** |

## Troubleshooting

**The agent tool can't reach the model.** Lemonade doesn't start at logon — open it from the Start menu, then re-check `http://localhost:13305/api/v1/health`.

**The model ID is rejected.** It must match Lemonade's reported `id` exactly. Re-run the `/api/v1/models` command and copy the value verbatim.

**`torch.cuda.is_available()` returns False.** Open **AMD Ryzen AI Developer Center** from the taskbar and install any pending updates, then reboot.

**Responses are slow with a large model.** Token generation is limited by memory bandwidth rather than capacity, so a larger model doesn't simply run slower in proportion to its size. Switch to a mixture-of-experts model such as Qwen3.6 35B MTP, which activates only a fraction of its parameters per token and generates considerably faster than a dense model of similar size.

**The model dropdown is empty.** No models ship with the image. Download one through Lemonade's Model Manager first — see Part 2, Step 2.

**`node -v` ignores `nvm use`.** Node.js is installed directly as well as through nvm, so the direct install can take precedence on PATH. Adjust your PATH order, or use nvm's shell integration.
