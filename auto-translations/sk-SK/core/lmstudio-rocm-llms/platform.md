<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Tento dokument popisuje očakávané konfigurácie platformy pre spustenie tohto playbooku.

## Windows

### Inštalácia LM Studio

LM Studio by mal byť vopred nainštalovaný:

| Komponent | Verzia | Umiestnenie |
|-----------|---------|----------|
| **LM Studio (Modely + Rôzne)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Vyrovnávacia pamäť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stiahnutie modelov

Nasledujúce modely by už mali byť prítomné v adresári modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Zariadenie | Typ modelu | Kvantizácia | Veľkosť (GB) | Umiestnenie |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Inštalácia LM Studio

Ďalšie podrobnosti nájdete v [lmstudio.md](../../dependencies/lmstudio.md).

### Stiahnutie modelov

Rovnaké ako v systéme Windows.