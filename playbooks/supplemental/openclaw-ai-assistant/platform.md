# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Prerequisites

PyTorch with ROCm support will be pre-installed on your AMD Developer Platform. Please refer to the relevant section for your operating system:

## Windows

### ROCm

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **ROCm**   | 7.1.1 or newer    | Preinstalled, available in PATH   |


### LM Studio Installation

LM Studio should be pre-installed:

| Component | Version | Location |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Required Models

The following models should already be present in the LM Studio models directory (`C:\Users\...\.lmstudio\models`):

| Model Type | Quantization | Size | Location |
|------------|--------------|------|----------|
| Qwen3.5 unsloth/Qwen3.5-35B-A3B-GGUF 35B | `Q4_K_M` | 22 GB | `models\ggml-org` |

---

Ensure at least **30GB free space** for model storage.

## Network Requirements

Initial setup requires internet access to download models from Hugging Face. After download, the playbook can run offline.

- First-time model downloads may take **10-15 minutes** depending on model size and connection speed
- Models are cached locally and don't need to be re-downloaded