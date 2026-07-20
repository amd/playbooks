# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za zagon te knjižice postopkov (playbook).

## Predpogoji

PyTorch s podporo za ROCm je vnaprej nameščen na platformi AMD Ryzen™ AI Halo Developer Platform. Za vse ostale naprave morajo uporabniki ročno namestiti PyTorch s podporo za ROCm. Prosimo, oglejte si ustrezen razdelek za svoj operacijski sistem:

### Windows

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ali novejši    | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah je treba namestiti ročno |

### Linux

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ali novejši    | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah je treba namestiti ročno |

## Zahtevani modeli

Naslednji modeli so testirani in optimizirani za vašo platformo:

| Model | Parametri | Velikost | Mesto prenosa |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah je treba namestiti ročno |

Modeli bodo samodejno preneseni v predpomnilniški imenik Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zagotovite vsaj **20 GB prostora** za shranjevanje modelov.

## Omrežne zahteve

Začetna namestitev zahteva dostop do interneta za prenos modelov iz Hugging Face. Po prenosu lahko knjižica postopkov deluje brez povezave.

- Prvi prenos modelov lahko traja **5–10 minut**, odvisno od velikosti modela in hitrosti povezave
- Modeli se shranijo lokalno v predpomnilnik in jih ni treba ponovno prenašati