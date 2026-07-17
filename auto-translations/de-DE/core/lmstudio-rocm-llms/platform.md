<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Windows

### LM Studio Installation

LM Studio sollte vorinstalliert sein:

| Komponente | Version | Speicherort |
|-----------|---------|----------|
| **LM Studio (Modelle + Sonstiges)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programm)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Modell-Download

Die folgenden Modelle sollten bereits im LM Studio-Modellverzeichnis vorhanden sein (`C:\Users\...\.lmstudio\models`):

| Gerät | Modelltyp | Quantisierung | Größe (GB) | Speicherort |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio Installation

Weitere Details finden Sie unter [lmstudio.md](../../dependencies/lmstudio.md).

### Modell-Download

Identisch mit Windows.