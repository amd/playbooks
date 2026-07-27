<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré kroky, príkazy, súbory na stiahnutie alebo dostupnosť produktov sa môžu vo vašom jazyku alebo regióne líšiť. Ak sa vám niečo zdá nesprávne, považujte pôvodný anglický playbook za zdroj pravdivých informácií.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tohto playbooku.

## Windows

### Inštalácia LM Studio

LM Studio by mala byť predinštalovaná:

| Komponent | Verzia | Umiestnenie |
|-----------|---------|----------|
| **LM Studio (Modely + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Vyrovnávacia pamäť)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Stiahnutie modelu

Nasledujúce modely by už mali byť prítomné v adresári modelov LM Studio (`C:\Users\...\.lmstudio\models`):

| Typ modelu | Kvantizácia | Veľkosť | Umiestnenie |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Inštalácia LM Studio

Podrobnosti nájdete v lmstudio.md (v priečinku dependencies).

### Stiahnutie modelu

Rovnako ako v systéme Windows.