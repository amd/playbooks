<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Prerequisites

PyTorch with ROCm support will be pre-installed on your AMD Developer Platform. Please refer to the relevant section for your operating system:

### Windows

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 or newer    | Preinstalled, available in PATH   |

### Linux

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 or newer    | Preinstalled, available in PATH   |

## Required Models

The following models are tested and optimized for your platform. The playbook automatically selects one based on your device:

| Model | Parameters | Size | Platform | Download Location |
|-------|------------|------|----------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Strix Halo (halo, halo_box) | Pre-installed on AMD Halo Developer Platform |
| **Qwen/Qwen3.5-4B** | 4B | ~9GB | Strix Point (stx), Krackan (krk) | Hugging Face Hub |

> **Note:** gpt-oss-20b is too large for the smaller memory footprint of Strix Point and Krackan, so those platforms use the compact Qwen3.5-4B instead. Qwen3.5 requires `transformers>=5.2.0`.

Models will be automatically downloaded to the Hugging Face cache directory:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Ensure at least **50GB free space** for gpt-oss-20b, or **~15GB** for Qwen3.5-4B.

## Network Requirements

Initial setup requires internet access to download models from Hugging Face. After download, the playbook can run offline.

- First-time model downloads may take **5-10 minutes** depending on model size and connection speed
- Models are cached locally and don't need to be re-downloaded