# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Required Apps/Frameworks
### Windows

ComfyUI should be pre-installed using the AMD portable package:

| Component | Version | Location |
|-----------|---------|----------|
| **ComfyUI_windows_portable_amd.7z** | v0.9.2 | `C:\ProgramData\ComfyUI` |

Extract the portable package to `C:\ProgramData\ComfyUI` before running this playbook.

Models should be placed in `C:\ProgramData\ComfyUI\models\`.

---

### Linux

Clone ComfyUI from the official repository and install dependencies:

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
git checkout v0.9.2
pip install -r requirements.txt
```

App should be placed in `/usr/local/bin/ComfyUI/`. Models should be placed in `ComfyUI/models/`.

## Required Models

### Windows/Linux

The following models must be present in the ComfyUI models directory:

| Model Type | Filename | Size | Location | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |

---