<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van deze playbook.

## Windows

### LM Studio-installatie

LM Studio moet vooraf zijn geïnstalleerd:

| Component | Versie | Locatie |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model downloaden

De volgende modellen moeten al aanwezig zijn in de LM Studio-modellenmap (`C:\Users\...\.lmstudio\models`):

| Modeltype | Kwantisatie | Grootte | Locatie |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio-installatie

Zie lmstudio.md (in de map dependencies) voor meer details.

### Model downloaden

Hetzelfde als op Windows.