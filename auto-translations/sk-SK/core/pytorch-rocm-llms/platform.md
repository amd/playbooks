<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy pre spustenie tohto playbooku.

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na AMD Ryzen™ AI Halo Developer Platform. Pre všetky ostatné zariadenia musia používatelia nainštalovať PyTorch s podporou ROCm manuálne. Prosím, pozrite si príslušnú sekciu pre váš operačný systém:

### Windows

| Komponent     | Verzia          | Poznámky                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 alebo novší | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |

### Linux

| Komponent     | Verzia          | Poznámky                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 alebo novší | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |

## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Miesto stiahnutia |
|-------|-----------|---------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40 GB | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |

Modely sa automaticky stiahnu do adresára vyrovnávacej pamäte Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zabezpečte aspoň **50 GB voľného miesta** pre uloženie modelov.

## Sieťové požiadavky

Počiatočné nastavenie vyžaduje prístup na internet na stiahnutie modelov z Hugging Face. Po stiahnutí môže playbook fungovať offline.

- Prvotné sťahovanie modelov môže trvať **5 – 10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne vo vyrovnávacej pamäti a nie je potrebné ich opätovne sťahovať