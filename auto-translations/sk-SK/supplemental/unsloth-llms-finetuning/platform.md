# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy pre spustenie tohto playbooku.

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na AMD Ryzen™ AI Halo Developer Platform. Pre všetky ostatné zariadenia musia používatelia nainštalovať PyTorch s podporou ROCm manuálne. Prosím, pozrite si príslušnú sekciu pre váš operačný systém:


### Windows

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; musí byť manuálne nainštalovaný na všetkých ostatných zariadeniach |


### Linux

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Predinštalovaný na AMD Ryzen AI Halo Developer Platform; musí byť manuálne nainštalovaný na všetkých ostatných zariadeniach |


## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Miesto stiahnutia |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Stiahnuť z HF

Modely budú automaticky stiahnuté do adresára vyrovnávacej pamäte Hugging Face: `~/.cache/huggingface/hub/`

Zabezpečte aspoň **20 GB voľného miesta** pre uloženie modelov.

## Sieťové požiadavky

Počiatočné nastavenie vyžaduje prístup na internet na stiahnutie modelov z Hugging Face. Po stiahnutí môže playbook fungovať offline.

- Prvotné sťahovanie modelov môže trvať **5–10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne do vyrovnávacej pamäte a nie je potrebné ich opätovne sťahovať