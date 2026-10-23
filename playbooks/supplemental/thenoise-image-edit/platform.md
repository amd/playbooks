<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Required Apps/Frameworks
### Windows/Linux

TheNoise should be installed from source using [uv](https://docs.astral.sh/uv/). The launcher scripts (`./thenoise.sh` on Linux, `thenoise.bat` on Windows) create a managed Python virtual environment, install the ROCm build of PyTorch for the GPU, and install TheNoise in editable mode. No other setup is required.

- [uv](https://docs.astral.sh/uv/) is the only system prerequisite.
- The ROCm torch build is chosen automatically from the GPU (`/sys/class/kfd` on Linux; best-effort from the GPU name on Windows, override with `$env:GFX_ARCH`).
- The clone root is the working directory for all `generate`, `edit`, and `serve` commands.

## Required Models

### Windows/Linux

The Flux.2 Klein 4B model is downloaded with the project's helper into
`./models/klein/`:

```bash
.venv/bin/python scripts/download.py --model klein
```

| Model Type | Filename | Location | Size | Download |
|------------|----------|----------|------|----------|
| Diffusion Model | `flux-2-klein-4b.safetensors` | `models/klein/split_files/diffusion_models/` | ~12 GB | [Link](https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/main/split_files/diffusion_models/flux-2-klein-4b.safetensors) |
| Text Encoder | `qwen_3_4b.safetensors` | `models/klein/split_files/text_encoders/` | ~7.5 GB | [Link](https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| VAE | `flux2-vae.safetensors` | `models/klein/split_files/vae/` | ~1 GB | [Link](https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/main/split_files/vae/flux2-vae.safetensors) |

The model is correctly placed if `scripts/download.py --model klein` completes
without error and the three files above exist under `./models/klein/`.

## Hardware Requirements

- An **AMD GPU** with ROCm support. Primary target: **Strix Halo** (gfx1151);
  also tested on gfx1150 / gfx1152 and ROCm-capable Radeon™ discrete GPUs.
- **RAM:** 32 GB minimum; 64 GB+ recommended. The 128 GB Strix Halo
  configuration runs everything comfortably.
- **Disk:** the model files above (roughly 21 GB total for Flux.2 Klein 4B) plus
  a few GB of headroom.
