<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Windows

### LM Studio Installation

LM Studio should be pre-installed:

| Component | Version | Location |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model Download

The following models should already be present in the LM Studio models directory (`C:\Users\...\.lmstudio\models`):

| Device | Model Type | Quantization | Size | Location |
| ----- |------------|--------------|------|----------|
| halo_box / halo | OpenAI GPT-OSS 120B | `MXFP4` | 59 GB | `models\ggml-org` |
| stx / krk / rx7900xt / rx9070xt / r9700 | Qwen3.5 9B | `Q4_K_M` | 7 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Installation

See lmstudio.md (inside dependencies folder) for more details.

### Model Download

Same as on Windows.