<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spillebok.

## Windows

### LM Studio-installasjon

LM Studio bør være forhåndsinstallert:

| Komponent | Versjon | Plassering |
|-----------|---------|----------|
| **LM Studio (Modeller + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Buffer)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modellnedlasting

Følgende modeller bør allerede være til stede i LM Studios modellkatalog (`C:\Users\...\.lmstudio\models`):

| Enhet | Modelltype | Kvantisering | Størrelse (GB) | Plassering |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio-installasjon

Se [lmstudio.md](../../dependencies/lmstudio.md) for flere detaljer.

### Modellnedlasting

Samme som på Windows.