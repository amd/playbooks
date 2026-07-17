<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Dette dokument beskriver de forventede platformskonfigurationer til at køre dette playbook.

## Windows

### LM Studio Installation

LM Studio skal være forudinstalleret:

| Komponent | Version | Placering |
|-----------|---------|----------|
| **LM Studio (Modeller + Diverse)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modeldownload

Følgende modeller skal allerede være til stede i LM Studio-modellernes mappe (`C:\Users\...\.lmstudio\models`):

| Enhed | Modeltype | Kvantisering | Størrelse (GB) | Placering |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio Installation

Se [lmstudio.md](../../dependencies/lmstudio.md) for flere detaljer.

### Modeldownload

Samme som på Windows.