<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy pre spustenie tohto playbooku.

## Windows

### Inštalácia LM Studio

LM Studio by mal byť vopred nainštalovaný:

| Komponent | Verzia | Umiestnenie |
|-----------|---------|----------|
| **LM Studio (Modely + Rôzne)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Vyrovnávacia pamäť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stiahnutie modelu

Nasledujúce modely by už mali byť prítomné v adresári modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Typ modelu | Kvantizácia | Veľkosť | Umiestnenie |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### Inštalácia LM Studio

Ďalšie podrobnosti nájdete v súbore lmstudio.md (v priečinku dependencies).

### Stiahnutie modelu

Rovnaké ako v systéme Windows.