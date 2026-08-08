<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tejto príručky (playbook).

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na platforme AMD Ryzen™ AI Halo Developer Platform. Na všetkých ostatných zariadeniach musia používatelia nainštalovať PyTorch s podporou ROCm manuálne. Prosím, pozrite si príslušnú sekciu pre váš operačný systém:


### Windows

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalovaný manuálne |


### Linux

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalovaný manuálne |


## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Miesto stiahnutia |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Stiahnuť z HF

Modely budú automaticky stiahnuté do vyrovnávacej pamäte Hugging Face: `~/.cache/huggingface/hub/`

Zabezpečte aspoň **20 GB voľného miesta** na ukladanie modelov.

## Sieťové požiadavky

Počiatočné nastavenie vyžaduje prístup na internet na stiahnutie modelov z Hugging Face. Po stiahnutí môže príručka (playbook) fungovať offline.

- Prvotné sťahovanie modelov môže trvať **5 – 10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne vo vyrovnávacej pamäti a nie je potrebné ich opätovne sťahovať