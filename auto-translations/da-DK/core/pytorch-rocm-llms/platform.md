<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til at køre denne playbook.

## Forudsætninger

PyTorch med ROCm-understøttelse er forudinstalleret på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheder skal brugerne manuelt installere PyTorch med ROCm-understøttelse. Se venligst det relevante afsnit for dit operativsystem:

### Windows

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 eller nyere    | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |

### Linux

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 eller nyere    | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |

## Påkrævede modeller

Følgende modeller er testet og optimeret til din platform:

| Model | Parametre | Størrelse | Downloadsted |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |

Modeller vil automatisk blive downloadet til Hugging Face-cachemappen:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Sørg for mindst **50 GB ledig plads** til modellagring.

## Netværkskrav

Den indledende opsætning kræver internetadgang for at downloade modeller fra Hugging Face. Efter download kan playbooken køre offline.

- Første gangs modeldownloads kan tage **5-10 minutter** afhængigt af modelstørrelse og forbindelseshastighed
- Modeller caches lokalt og skal ikke downloades igen