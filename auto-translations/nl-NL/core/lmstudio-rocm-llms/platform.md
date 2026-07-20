<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Windows

### LM Studio-installatie

LM Studio moet vooraf zijn geïnstalleerd:

| Component | Versie | Locatie |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model downloaden

De volgende modellen moeten al aanwezig zijn in de LM Studio-modellenmap (`C:\Users\...\.lmstudio\models`):

| Apparaat | Modeltype | Kwantisering | Grootte (GB) | Locatie |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio-installatie

Zie [lmstudio.md](../../dependencies/lmstudio.md) voor meer details.

### Model downloaden

Hetzelfde als op Windows.