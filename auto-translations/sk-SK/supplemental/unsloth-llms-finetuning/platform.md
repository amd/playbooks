# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tohto playbooku.

## Predpoklady

PyTorch s podporou ROCm je predinštalovaný na platforme AMD Ryzen™ AI Halo Developer Platform. Pri všetkých ostatných zariadeniach musia používatelia nainštalovať PyTorch s podporou ROCm manuálne. Prosím, pozrite si príslušnú sekciu pre váš operačný systém:


### Windows

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebné ho nainštalovať manuálne |


### Linux

| Komponent     | Verzia         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Predinštalovaný na platforme AMD Ryzen AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebné ho nainštalovať manuálne |


## Požadované modely

Nasledujúce modely sú otestované a optimalizované pre vašu platformu:

| Model | Parametre | Veľkosť | Miesto stiahnutia |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Stiahnuť z HF

Modely budú automaticky stiahnuté do vyrovnávacej pamäte Hugging Face: `~/.cache/huggingface/hub/`

Zaistite aspoň **20 GB voľného miesta** na ukladanie modelov.

## Požiadavky na sieť

Počiatočné nastavenie vyžaduje internetové pripojenie na stiahnutie modelov z Hugging Face. Po stiahnutí môže playbook fungovať offline.

- Prvé stiahnutie modelov môže trvať **5 – 10 minút** v závislosti od veľkosti modelu a rýchlosti pripojenia
- Modely sú uložené lokálne v cache a nie je potrebné ich opätovne sťahovať