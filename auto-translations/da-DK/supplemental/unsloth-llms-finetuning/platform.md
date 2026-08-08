<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer for at køre denne playbook.

## Forudsætninger

PyTorch med ROCm-understøttelse er forudinstalleret på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheder skal brugere manuelt installere PyTorch med ROCm-understøttelse. Se venligst det relevante afsnit for dit operativsystem:


### Windows

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |


### Linux

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |


## Påkrævede modeller

Følgende modeller er testet og optimeret til din platform:

| Model | Parametre | Størrelse | Downloadsted |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Download fra HF

Modeller downloades automatisk til Hugging Face-cachemappen: `~/.cache/huggingface/hub/`

Sørg for mindst **20 GB ledig plads** til modellagring.

## Netværkskrav

Den indledende opsætning kræver internetadgang for at downloade modeller fra Hugging Face. Efter download kan playbooken køre offline.

- Første gang, modeller downloades, kan det tage **5-10 minutter** afhængigt af modelstørrelse og forbindelseshastighed
- Modeller caches lokalt og skal ikke downloades igen