<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for kjøring av denne playbooken.

## Windows

### Installasjon av LM Studio

LM Studio skal være forhåndsinstallert:

| Komponent | Versjon | Plassering |
|-----------|---------|----------|
| **LM Studio (Modeller + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Buffer)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Nedlasting av modell

Følgende modeller skal allerede være tilstede i LM Studio-modellmappen (`C:\Users\...\.lmstudio\models`):

| Modelltype | Kvantisering | Størrelse | Plassering |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Installasjon av LM Studio

Se lmstudio.md (inne i dependencies-mappen) for flere detaljer.

### Nedlasting av modell

Samme som på Windows.