# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til at køre dette playbook.

## Forudsætninger

PyTorch med ROCm-understøttelse er forudinstalleret på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheder skal brugere manuelt installere PyTorch med ROCm-understøttelse. Se det relevante afsnit for dit operativsystem:

### Windows

| Komponent     | Version         | Noter                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |


### Linux

| Komponent     | Version         | Noter                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |


## Påkrævede modeller

Følgende modeller er testet og optimeret til din platform:

| Model | Parametre | Størrelse | Downloadplacering |
|-------|-----------|-----------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Download fra HF

Modeller downloades automatisk til Hugging Face-cachmappen: `~/.cache/huggingface/hub/`

Sørg for mindst **20 GB ledig plads** til modellagring.

## Netværkskrav

Den indledende opsætning kræver internetadgang for at downloade modeller fra Hugging Face. Efter download kan playbook køre offline.

- Første gangs modeldownloads kan tage **5-10 minutter** afhængigt af modelstørrelse og forbindelseshastighed
- Modeller gemmes lokalt i cache og behøver ikke downloades igen