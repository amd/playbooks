# Platform Configuration

## Operating System Support

- **Linux**: Full support with ROCm
- **Windows** : Full support with ROCm

## Pre-installed Software

The following software should be pre-configured on your STX Halo™:

### ROCm Stack
- ROCm 7.2
- PyTorch 2.8+ with ROCm support

### Python Environment
- Python 3.10 or newer
- pip package manager

## Environment Setup

### Creating a Python Virtual Environment

It is **strongly recommended** to create a Python virtual environment before installing dependencies. This isolates the playbook's packages from your system Python and prevents version conflicts.

**Steps:**

1. Create a virtual environment:
   ```bash
   python3 -m venv llm-env
   ```

2. Activate the virtual environment:
   ```bash
   source llm-env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
   pip install transformers accelerate sentencepiece protobuf
   ```

4. When finished, deactivate the environment:
   ```bash
   deactivate
   ```

> **Note**: Always activate the virtual environment (`source llm-env/bin/activate`) before running the playbook scripts.

## Model Storage

Models will be downloaded to the Hugging Face cache directory (typically `~/.cache/huggingface/hub/`). Ensure at least **50GB free space** for model storage.

## GPU Requirements

- **Minimum**: 16GB VRAM (for 7B models)
- **Recommended**: 24GB VRAM (for 13B-20B models)

## Verified Models

The following models are tested and optimized for STX Halo™:

- `mistralai/Mistral-7B-Instruct-v0.3` (7B parameters, ~14GB)
- `openai/gpt-oss-20b` (20B parameters, ~40GB)

## Network Requirements

Initial setup requires internet access to download models from Hugging Face. After download, the playbook can run offline.

## Notes

- First-time model downloads may take 10-30 minutes depending on model size and connection speed
- Models are cached locally and don't need to be re-downloaded
- ROCm drivers must be properly installed and configured for GPU acceleration
