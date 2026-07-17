<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Windows

### Namestitev LM Studio

LM Studio mora biti vnaprej nameščen:

| Komponenta | Različica | Lokacija |
|-----------|---------|----------|
| **LM Studio (modeli + razno)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (predpomnilnik)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Prenos modelov

Naslednji modeli morajo biti že prisotni v imeniku modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Naprava | Vrsta modela | Kvantizacija | Velikost (GB) | Lokacija |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Namestitev LM Studio

Za več podrobnosti glejte [lmstudio.md](../../dependencies/lmstudio.md).

### Prenos modelov

Enako kot v sistemu Windows.