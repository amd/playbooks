<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration — Windows Ryzen AI Halo (Project Zenith)

This document describes the preinstalled software and platform assumptions for this playbook. It applies only to the **Windows** image for the Ryzen AI Halo, which ships with Microsoft Project Zenith.

## AMD AI Stack

| Software | Version | Purpose |
|----------|---------|---------|
| Lemonade Server | Latest release | Local LLM server with OpenAI-compatible API. Installed for all users. Does not start at logon. No models are preinstalled. |
| ComfyUI Desktop | Latest release | Node-graph image and diffusion workflows. Bundles its own Python and ROCm runtime. |
| PyTorch (ROCm) | torch, torchvision, torchaudio with `rocm-sdk-devel` 7.14.0 | GPU-accelerated PyTorch, installed offline into the system Python |

## Project Zenith Toolchain

| Software | Version | Notes |
|----------|---------|-------|
| Python | 3.14.7 | System Python; hosts the ROCm PyTorch stack |
| PowerShell | 7.6.8 | Default Terminal profile |
| Intelligent Terminal | Preview | Installed per-user at first logon |
| GitHub Copilot CLI | 1.0.94 | Machine-wide install; dedicated Terminal profile |
| GitHub Copilot (app) | Latest | Desktop shortcut removed; launch from Start menu |
| WSL with Ubuntu | 26.04.1 | Per-user copy created at first logon (~1.46 GB) |
| Node.js + NVM for Windows | 1.2.2 (nvm) | nvm is installed for the first user account only |
| uv | Latest | Python package and environment manager |
| PowerToys | 0.101 | Command Palette registered per user |
| .NET SDK | 10 | |
| Windows App CLI (`winapp`) | Latest | |
| Git, Visual Studio Code | Latest | |
| GitHub CLI, Azure CLI | Latest | |
| Oh My Posh, Coreutils for Windows | Latest | Registered into each user's PowerShell profile |
| OpenSSH Server | Inbox | Installed; `sshd` service disabled and stopped by default |

## Preconfigured Windows Settings

| Setting | Value |
|---------|-------|
| Long paths | Enabled machine-wide (`LongPathsEnabled = 1`) |
| File Explorer | Full path displayed in title bar |
| Appearance | Dark mode set for new users |
| Fonts | Cascadia Mono NF, Cascadia Mono NF Italic, Cascadia Code NF |
| Terminal default profile | PowerShell 7 |
| Taskbar pins | Windows Terminal, Visual Studio Code, AMD Ryzen AI Developer Center |

## Local Server Endpoint

| Property | Value |
|----------|-------|
| Base URL | `http://localhost:13305/v1` |
| Alternate path prefix | `http://localhost:13305/api/v1` |
| Authentication | None by default. Apps requiring a non-empty key accept any placeholder. |
| Health check | `http://localhost:13305/api/v1/health` |
| Model list | `http://localhost:13305/api/v1/models` |

## Models

No models are preinstalled on the image. They are downloaded on demand through Lemonade's Model Manager or CLI.

Recommended starting points for agentic work on this platform:

| Model | Type | Notes |
|-------|------|-------|
| Qwen3.8 27B | Dense | Stronger per-token reasoning; slower generation, as throughput is bandwidth-bound |
| Qwen3.6 35B MTP | Mixture-of-experts | Faster interactive response at comparable size; generally the better default for agent workflows |

### Default Model Storage

Models downloaded through Lemonade use the Hugging Face Hub specification:

| Platform | Default Path |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |

Set the `HF_HOME` environment variable to change the storage location.

## Hardware Requirements

| Hardware Target | Requirements |
|----------------|-------------|
| **Device** | AMD Ryzen AI Halo (Gorgon Halo), Windows image |
| **GPU** | AMD Radeon™ integrated graphics (RDNA 3.5) |
| **NPU** | AMD XDNA™ 2 NPU, used by Lemonade hybrid execution modes |
| **Memory** | 64 GB minimum; 128 GB+ recommended for larger models |

## Network Requirements

- Internet connection required for initial model downloads (1–25 GB depending on model)
- Internet connection required for cloud agent sign-in, if used
- No internet required for local inference once models are downloaded

## Known Platform Notes

- **Lemonade Server does not start at logon.** Its startup shortcut is removed from the image, so it must be launched manually before dependent apps can reach the endpoint.
- **nvm is installed for the first user account only.** Node.js is also installed machine-wide, so PATH precedence between the two may need adjusting.
- **Intelligent Terminal is installed per-user** at first logon rather than machine-wide.
- **Custom model endpoints in Intelligent Terminal require GitHub Copilot CLI or OpenCode** as the underlying agent. Other built-in agents do not support custom OpenAI-compatible providers.
