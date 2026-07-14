<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Prerequisites

PyTorch with ROCm support is pre-installed on the AMD Ryzen™ AI Halo Developer Platform. For all other devices, users must manually install PyTorch with ROCm support. Please refer to the relevant section for your operating system:


### Windows

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Pre-installed on the AMD Ryzen AI Halo Developer Platform; must be manually installed on all other devices |


### Linux

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Pre-installed on the AMD Ryzen AI Halo Developer Platform; must be manually installed on all other devices |


## Required Models

The following models are tested and optimized for your platform:

| Model | Parameters | Size | Download Location |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Download from HF

Models will be automatically downloaded to the Hugging Face cache directory: `~/.cache/huggingface/hub/`

Ensure at least **20GB free space** for model storage.

## Network Requirements

Initial setup requires internet access to download models from Hugging Face. After download, the playbook can run offline.

- First-time model downloads may take **5-10 minutes** depending on model size and connection speed
- Models are cached locally and don't need to be re-downloaded