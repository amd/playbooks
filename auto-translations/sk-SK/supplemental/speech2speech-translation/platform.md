# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tejto príručky (playbook).

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na platforme AMD Ryzen™ AI Halo Developer Platform. Pri všetkých ostatných zariadeniach musia používatelia PyTorch s podporou ROCm nainštalovať manuálne. Pozrite si príslušnú časť pre váš operačný systém:

### Windows

| Komponent     | Verzia          | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 alebo novší    | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebné nainštalovať manuálne |

### Linux

| Komponent     | Verzia          | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 alebo novší    | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebné nainštalovať manuálne |

## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Umiestnenie na stiahnutie |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3B | ~10GB | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebné nainštalovať manuálne |

Modely sa automaticky stiahnu do adresára vyrovnávacej pamäte (cache) Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zabezpečte aspoň **20 GB voľného miesta** na ukladanie modelov.

## Sieťové požiadavky

Počiatočné nastavenie vyžaduje prístup na internet na stiahnutie modelov z Hugging Face. Po stiahnutí môže príručka (playbook) fungovať offline.

- Prvé stiahnutie modelov môže trvať **5 – 10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne vo vyrovnávacej pamäti a nie je potrebné ich opätovne sťahovať