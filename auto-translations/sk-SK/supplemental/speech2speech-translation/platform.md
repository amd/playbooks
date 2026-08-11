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

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na AMD Ryzen™ AI Halo Developer Platform. Pri všetkých ostatných zariadeniach musia používatelia manuálne nainštalovať PyTorch s podporou ROCm. Pozrite si príslušnú sekciu pre váš operačný systém:

### Windows

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 alebo novší    | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |

### Linux

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 alebo novší    | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |

## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Umiestnenie na stiahnutie |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3B | ~10GB | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |

Modely budú automaticky stiahnuté do adresára vyrovnávacej pamäte Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zabezpečte aspoň **20 GB voľného miesta** na ukladanie modelov.

## Sieťové požiadavky

Počiatočné nastavenie vyžaduje prístup na internet na stiahnutie modelov z Hugging Face. Po stiahnutí môže playbook fungovať v režime offline.

- Prvotné stiahnutie modelov môže trvať **5 – 10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne vo vyrovnávacej pamäti a nie je potrebné ich opätovne sťahovať