<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Windows

### Instalace LM Studio

LM Studio by mělo být předinstalováno:

| Komponenta | Verze | Umístění |
|-----------|---------|----------|
| **LM Studio (Modely + Různé)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Mezipaměť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stažení modelů

Následující modely by již měly být přítomny v adresáři modelů LM Studio (`C:\Users\...\.lmstudio\models`):

| Zařízení | Typ modelu | Kvantizace | Velikost (GB) | Umístění |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalace LM Studio

Další podrobnosti naleznete v [lmstudio.md](../../dependencies/lmstudio.md).

### Stažení modelů

Stejné jako v systému Windows.