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

The following models are tested and optimized for your platform:

| Model | Parameters | Size | Download Location |
|-------|------------|------|-------------------|
| **google/gemma-3n-E4B-it** | 8B | ~16GB | Pre-installed on AMD Halo Developer Platform |

Models will be automatically downloaded to the Hugging Face cache directory:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Ensure at least **20GB free space** for model storage.

## Network Requirements

Initial setup requires internet access to download models from Hugging Face. After download, the playbook can run offline.

- First-time model downloads may take **5-10 minutes** depending on model size and connection speed
- Models are cached locally and don't need to be re-downloaded