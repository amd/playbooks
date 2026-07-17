<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Windows

### LM Studio Installatie

LM Studio dient vooraf geïnstalleerd te zijn:

| Component | Versie | Locatie |
|-----------|--------|---------|
| **LM Studio (Modellen + Overig)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programma)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model Downloaden

De volgende modellen dienen reeds aanwezig te zijn in de LM Studio modellenmap (`C:\Users\...\.lmstudio\models`):

| Modeltype | Kwantisering | Grootte | Locatie |
|-----------|--------------|---------|---------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Installatie

Zie lmstudio.md (in de map dependencies) voor meer details.

### Model Downloaden

Hetzelfde als op Windows.