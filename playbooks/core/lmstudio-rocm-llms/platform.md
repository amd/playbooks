# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Windows

### LM Studio Installation

LM Studio should be pre-installed:

| Component | Version | Location |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.3.39 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.3.39 | `C:\Users\...\AppData\Local\Programs\LM Studio` |
| **LM Studio (Cache)** | v0.3.39 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model Download

The following models should already be present in the LM Studio models directory (`C:\Users\...\.lmstudio\models`):

| Model Type | Quantization | Size | Location |
|------------|--------------|------|----------|
| OpenAI GPT-OSS 120B | `MXFP4` | 59 GB | `models\ggml-org` |
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\ggml-org` |

---

## Linux

### LM Studio Installation

See lmstudio.md (inside dependencies folder) for more details.
### Model Download

Same as on Windows.