# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne playbooken.

## Forutsetninger

PyTorch med ROCm-støtte er forhåndsinstallert på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheter må brukere manuelt installere PyTorch med ROCm-støtte. Se den relevante delen for operativsystemet ditt:


### Windows

| Komponent     | Versjon         | Merknader                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |


### Linux

| Komponent     | Versjon         | Merknader                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |


## Nødvendige modeller

Følgende modeller er testet og optimalisert for plattformen din:

| Modell | Parametre | Størrelse | Nedlastingssted |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Last ned fra HF

Modeller vil automatisk bli lastet ned til Hugging Face-hurtigbufferkatalogen: `~/.cache/huggingface/hub/`

Sørg for at det er minst **20 GB ledig lagringsplass** for modellagring.

## Nettverkskrav

Førstegangs oppsett krever internettilgang for å laste ned modeller fra Hugging Face. Etter nedlasting kan playbooken kjøres uten nett.

- Første gangs nedlasting av modeller kan ta **5–10 minutter** avhengig av modellstørrelse og tilkoblingshastighet
- Modeller lagres i hurtigbuffer lokalt og trenger ikke å lastes ned på nytt