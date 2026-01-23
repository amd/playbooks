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

The following models should already be present in the LM Studio models directory (`C:\Users\...\.lmstudio\models\lmstudio-community`):

| Model Type | Quantization | Size | Location |
|------------|--------------|------|----------|
| OpenAI GPT-OSS 120B | `MXFP4` | 59 GB | `models\lmstudio-community` |
| OpenAI GPT-OSS 20B | `MXFP4` | 11.2 GB | `models\lmstudio-community` |
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Installation

Users are responsible for cloning and setting up LM Studio. See the playbook instructions for details.

### Model Download

Users are responsible for downloading the required models within their LM Studio installation.