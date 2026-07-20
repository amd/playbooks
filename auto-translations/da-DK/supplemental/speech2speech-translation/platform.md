# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer for at køre denne playbook.

## Forudsætninger

PyTorch med ROCm-understøttelse er forudinstalleret på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheder skal brugere manuelt installere PyTorch med ROCm-understøttelse. Se venligst det relevante afsnit for dit operativsystem:

### Windows

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 eller nyere    | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |

### Linux

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 eller nyere    | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |

## Påkrævede modeller

Følgende modeller er testet og optimeret til din platform:

| Model | Parametre | Størrelse | Downloadplacering |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |

Modeller vil automatisk blive downloadet til Hugging Face-cachemappen:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Sørg for mindst **20 GB ledig plads** til modellagring.

## Netværkskrav

Den indledende opsætning kræver internetadgang for at downloade modeller fra Hugging Face. Efter download kan playbooken køre offline.

- Første gangs modeldownloads kan tage **5-10 minutter** afhængigt af modelstørrelse og forbindelseshastighed
- Modeller caches lokalt og skal ikke downloades igen