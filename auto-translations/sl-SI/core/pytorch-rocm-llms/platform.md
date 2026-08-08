<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega vodnika (playbook).

## Predpogoji

PyTorch s podporo za ROCm je vnaprej nameščen na platformi AMD Ryzen™ AI Halo Developer Platform. Za vse ostale naprave morajo uporabniki ročno namestiti PyTorch s podporo za ROCm. Prosimo, oglejte si ustrezen razdelek za svoj operacijski sistem:

### Windows

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ali novejši    | Vnaprej nameščen na AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah je treba namestiti ročno |

### Linux

| Komponenta     | Različica         | Opombe                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ali novejši    | Vnaprej nameščen na AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah je treba namestiti ročno |

## Zahtevani modeli

Naslednji modeli so testirani in optimizirani za vašo platformo:

| Model | Parametri | Velikost | Mesto za prenos |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Vnaprej nameščen na AMD Ryzen AI Halo Developer Platform; na vseh ostalih napravah je treba namestiti ročno |

Modeli bodo samodejno preneseni v predpomnilniški imenik Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zagotovite vsaj **50 GB prostega prostora** za shranjevanje modelov.

## Zahteve glede omrežja

Začetna namestitev zahteva dostop do interneta za prenos modelov iz Hugging Face. Po prenosu lahko vodnik (playbook) deluje brez povezave.

- Prvi prenosi modelov lahko trajajo **5–10 minut**, odvisno od velikosti modela in hitrosti povezave
- Modeli se shranijo lokalno v predpomnilnik in jih ni treba ponovno prenašati