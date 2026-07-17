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

| Modeltype | Kvantisering | Størrelse | Placering |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Installation

Se lmstudio.md (i mappen dependencies) for flere detaljer.

### Modeldownload

Samme som på Windows.