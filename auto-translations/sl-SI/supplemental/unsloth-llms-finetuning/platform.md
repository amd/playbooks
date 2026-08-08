<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega playbooka.

## Predpogoji

PyTorch s podporo ROCm je vnaprej nameščen na platformi AMD Ryzen™ AI Halo Developer Platform. Za vse ostale naprave morajo uporabniki ročno namestiti PyTorch s podporo ROCm. Prosimo, glejte ustrezen razdelek za vaš operacijski sistem:


### Windows

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah ga je treba namestiti ročno |


### Linux

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Vnaprej nameščen na platformi AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah ga je treba namestiti ročno |


## Zahtevani modeli

Naslednji modeli so testirani in optimizirani za vašo platformo:

| Model | Parametri | Velikost | Mesto prenosa |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Prenos iz HF

Modeli bodo samodejno preneseni v predpomnilniški imenik Hugging Face: `~/.cache/huggingface/hub/`

Zagotovite vsaj **20 GB prostega prostora** za shranjevanje modelov.

## Omrežne zahteve

Začetna namestitev zahteva internetno povezavo za prenos modelov iz Hugging Face. Po prenosu se playbook lahko izvaja brez povezave.

- Prvi prenos modelov lahko traja **5–10 minut**, odvisno od velikosti modela in hitrosti povezave
- Modeli so shranjeni lokalno v predpomnilniku in jih ni treba ponovno prenašati