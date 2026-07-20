# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika (playbook).

## Predpogoji

PyTorch s podporo za ROCm je vnaprej nameščen na platformi AMD Ryzen™ AI Halo Developer Platform. Za vse druge naprave morajo uporabniki ročno namestiti PyTorch s podporo za ROCm. Prosimo, glejte ustrezen razdelek za vaš operacijski sistem:


### Windows

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh drugih napravah ga je treba namestiti ročno |


### Linux

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh drugih napravah ga je treba namestiti ročno |


## Zahtevani modeli

Naslednji modeli so testirani in optimizirani za vašo platformo:

| Model | Parametri | Velikost | Mesto prenosa |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Prenesite iz HF

Modeli bodo samodejno preneseni v predpomnilniško mapo Hugging Face: `~/.cache/huggingface/hub/`

Zagotovite vsaj **20 GB prostega prostora** za shranjevanje modelov.

## Zahteve za omrežje

Začetna nastavitev zahteva dostop do interneta za prenos modelov iz Hugging Face. Po prenosu lahko priročnik deluje brez povezave.

- Prvi prenosi modelov lahko trajajo **5–10 minut**, odvisno od velikosti modela in hitrosti povezave
- Modeli so shranjeni lokalno v predpomnilniku in jih ni treba znova prenašati