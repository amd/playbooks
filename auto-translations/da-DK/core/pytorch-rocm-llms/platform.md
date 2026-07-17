<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til at køre dette playbook.

## Forudsætninger

PyTorch med ROCm-understøttelse er forudinstalleret på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheder skal brugere manuelt installere PyTorch med ROCm-understøttelse. Se det relevante afsnit for dit operativsystem:

### Windows

| Komponent     | Version         | Noter                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 eller nyere    | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |

### Linux

| Komponent     | Version         | Noter                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 eller nyere    | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |

## Påkrævede modeller

Følgende modeller er testet og optimeret til din platform:

| Model | Parametre | Størrelse | Downloadplacering |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal manuelt installeres på alle andre enheder |

Modeller downloades automatisk til Hugging Face-cachedirektoriet:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Sørg for mindst **50 GB ledig plads** til modellagring.

## Netværkskrav

Den indledende opsætning kræver internetadgang for at downloade modeller fra Hugging Face. Efter download kan playbook køre offline.

- Første gangs modeldownloads kan tage **5-10 minutter** afhængigt af modelstørrelse og forbindelseshastighed
- Modeller gemmes lokalt i cache og behøver ikke downloades igen