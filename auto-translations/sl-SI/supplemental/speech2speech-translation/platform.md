<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega vodnika.

## Predpogoji

PyTorch s podporo za ROCm je vnaprej nameščen na platformi AMD Ryzen™ AI Halo Developer Platform. Za vse ostale naprave morajo uporabniki PyTorch s podporo za ROCm namestiti ročno. Prosimo, glejte ustrezen razdelek za vaš operacijski sistem:

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

Modeli bodo samodejno preneseni v predpomnilniško mapo Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zagotovite vsaj **20 GB prostega prostora** za shranjevanje modelov.

## Omrežne zahteve

Začetna namestitev zahteva internetno povezavo za prenos modelov iz Hugging Face. Po prenosu lahko vodnik deluje brez povezave.

- Prvi prenos modelov lahko traja **5–10 minut**, odvisno od velikosti modela in hitrosti povezave
- Modeli se shranijo lokalno v predpomnilnik in jih ni treba znova prenašati