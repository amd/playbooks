<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument opisuje očakávané konfigurácie platformy na spustenie tohto playbooku.

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na platforme AMD Ryzen™ AI Halo Developer Platform. Na všetkých ostatných zariadeniach musia používatelia manuálne nainštalovať PyTorch s podporou ROCm. Prosím, prečítajte si príslušnú časť pre váš operačný systém:

### Windows

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 alebo novší    | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalovaný manuálne |

### Linux

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 alebo novší    | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalovaný manuálne |

## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Miesto stiahnutia |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalovaný manuálne |

Modely sa automaticky stiahnu do adresára vyrovnávacej pamäte Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zabezpečte aspoň **50 GB voľného miesta** pre uloženie modelov.

## Sieťové požiadavky

Prvotné nastavenie vyžaduje pripojenie na internet na stiahnutie modelov z Hugging Face. Po stiahnutí môže playbook fungovať offline.

- Prvé stiahnutie modelov môže trvať **5 – 10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne v vyrovnávacej pamäti a nie je potrebné ich opätovne sťahovať