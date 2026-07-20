<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna playbook.

## Windows

### LM Studio-installation

LM Studio bör vara förinstallerat:

| Komponent | Version | Plats |
|-----------|---------|----------|
| **LM Studio (Modeller + Diverse)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modellnedladdning

Följande modeller bör redan finnas i LM Studios modellkatalog (`C:\Users\...\.lmstudio\models`):

| Enhet | Modelltyp | Kvantisering | Storlek (GB) | Plats |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio-installation

Se [lmstudio.md](../../dependencies/lmstudio.md) för mer information.

### Modellnedladdning

Samma som på Windows.