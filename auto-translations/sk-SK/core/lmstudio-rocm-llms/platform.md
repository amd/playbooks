<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tohto playbooku.

## Windows

### Inštalácia LM Studio

LM Studio by mala byť predinštalovaná:

| Komponent | Verzia | Umiestnenie |
|-----------|---------|----------|
| **LM Studio (modely + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (vyrovnávacia pamäť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stiahnutie modelu

Nasledujúce modely by už mali byť prítomné v adresári modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Zariadenie | Typ modelu | Kvantizácia | Veľkosť (GB) | Umiestnenie |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Inštalácia LM Studio

Podrobnosti nájdete v [lmstudio.md](../../dependencies/lmstudio.md).

### Stiahnutie modelu

Rovnaké ako v systéme Windows.