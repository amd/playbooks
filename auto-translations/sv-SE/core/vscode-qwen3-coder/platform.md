<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna playbook.

## Windows

### Installation av LM Studio

LM Studio ska vara förinstallerat:

| Komponent | Version | Plats |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modellnedladdning

Följande modeller bör redan finnas i LM Studios modellkatalog (`C:\Users\...\.lmstudio\models`):

| Modelltyp | Kvantisering | Storlek | Plats |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Installation av LM Studio

Se lmstudio.md (i mappen dependencies) för mer information.

### Modellnedladdning

Samma som på Windows.