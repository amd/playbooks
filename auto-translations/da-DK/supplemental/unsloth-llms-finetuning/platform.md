# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til afvikling af denne playbook.

## Forudsætninger

PyTorch med ROCm-understøttelse er forudinstalleret på AMD Ryzen™ AI Halo Developer Platform. På alle andre enheder skal brugere manuelt installere PyTorch med ROCm-understøttelse. Se venligst det relevante afsnit for dit operativsystem:


### Windows

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |


### Linux

| Komponent     | Version         | Bemærkninger                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Forudinstalleret på AMD Ryzen AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |


## Påkrævede modeller

Følgende modeller er testet og optimeret til din platform:

| Model | Parametre | Størrelse | Downloadsted |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Download fra HF

Modeller downloades automatisk til Hugging Face-cachemappen: `~/.cache/huggingface/hub/`

Sørg for at have mindst **20 GB ledig plads** til modellagring.

## Netværkskrav

Den indledende opsætning kræver internetadgang for at downloade modeller fra Hugging Face. Efter download kan playbooken køre offline.

- Førstegangsdownload af modeller kan tage **5-10 minutter** afhængigt af modellens størrelse og forbindelseshastighed
- Modeller caches lokalt og behøver ikke downloades igen