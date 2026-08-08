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