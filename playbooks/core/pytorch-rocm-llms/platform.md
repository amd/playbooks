# Platform Configuration

## Operating System Support

- **Linux**: Full support with ROCm
- **Windows** : Full support with ROCm

## Pre-installed Software

The following software should be pre-configured on your STX Halo™:

### ROCm Stack
- ROCm 7.2
- PyTorch 2.9+ with ROCm support

### Python Environment
- Python 3.11 or newer
- pip package manager

## Environment Setup

## Model Storage

Models will be downloaded to the Hugging Face cache directory (typically `~/.cache/huggingface/hub/`). Ensure at least **50GB free space** for model storage.

## GPU Requirements

- **Minimum**: 16GB VRAM (for 7B models)
- **Recommended**: 24GB VRAM (for 13B-20B models)

## Verified Models

The following models are tested and optimized for STX Halo™.
If you are using AMD Halo Developer Platform, this model comes pre-installed.

- `openai/gpt-oss-20b` (20B parameters, ~40GB)

## Network Requirements

Initial setup requires internet access to download models from Hugging Face. After download, the playbook can run offline.

## Notes

- First-time model downloads may take 10-30 minutes depending on model size and connection speed
- Models are cached locally and don't need to be re-downloaded
- ROCm drivers must be properly installed and configured for iGPU acceleration
