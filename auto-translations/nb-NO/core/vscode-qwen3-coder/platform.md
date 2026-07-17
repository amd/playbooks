<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spilleboken.

## Windows

### LM Studio-installasjon

LM Studio bør være forhåndsinstallert:

| Komponent | Versjon | Plassering |
|-----------|---------|----------|
| **LM Studio (Modeller + Div)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modellnedlasting

Følgende modeller bør allerede være til stede i LM Studio-modellkatalogen (`C:\Users\...\.lmstudio\models`):

| Modelltype | Kvantisering | Størrelse | Plassering |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio-installasjon

Se lmstudio.md (inne i avhengighetsmappen) for flere detaljer.

### Modellnedlasting

Samme som på Windows.