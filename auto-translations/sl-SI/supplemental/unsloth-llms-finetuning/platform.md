# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Predpogoji

PyTorch s podporo za ROCm je predhodno nameščen na platformi AMD Ryzen™ AI Halo Developer Platform. Za vse druge naprave morajo uporabniki ročno namestiti PyTorch s podporo za ROCm. Prosimo, glejte ustrezni razdelek za vaš operacijski sistem:

### Windows

| Komponenta    | Različica       | Opombe                            |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Predhodno nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh drugih napravah ga je treba namestiti ročno |


### Linux

| Komponenta    | Različica       | Opombe                            |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Predhodno nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh drugih napravah ga je treba namestiti ročno |


## Zahtevani modeli

Naslednji modeli so preizkušeni in optimizirani za vašo platformo:

| Model | Parametri | Velikost | Lokacija za prenos |
|-------|-----------|----------|--------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Prenos iz HF

Modeli bodo samodejno preneseni v imenik predpomnilnika Hugging Face: `~/.cache/huggingface/hub/`

Zagotovite vsaj **20 GB prostega prostora** za shranjevanje modelov.

## Omrežne zahteve

Začetna namestitev zahteva dostop do interneta za prenos modelov iz Hugging Face. Po prenosu lahko priročnik deluje brez povezave.

- Prvi prenosi modelov lahko trajajo **5–10 minut**, odvisno od velikosti modela in hitrosti povezave
- Modeli so predpomnjeni lokalno in jih ni treba znova prenašati