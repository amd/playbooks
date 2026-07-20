# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spillboken.

## Forutsetninger

PyTorch med ROCm-støtte er forhåndsinstallert på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheter må brukere manuelt installere PyTorch med ROCm-støtte. Se relevant avsnitt for ditt operativsystem:

### Windows

| Komponent     | Versjon         | Merknader                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 eller nyere    | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

### Linux

| Komponent     | Versjon         | Merknader                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 eller nyere    | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

## Nødvendige modeller

Følgende modeller er testet og optimalisert for din plattform:

| Modell | Parametere | Størrelse | Nedlastingssted |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3 B | ~10 GB | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

Modeller lastes automatisk ned til Hugging Face-hurtigbufferkatalogen:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Sørg for minst **20 GB ledig plass** til modellagring.

## Nettverkskrav

Førstegangsoppsett krever internettilgang for å laste ned modeller fra Hugging Face. Etter nedlasting kan spillboken kjøres uten nett.

- Nedlasting av modeller for første gang kan ta **5–10 minutter**, avhengig av modellstørrelse og tilkoblingshastighet
- Modeller mellomlagres lokalt og trenger ikke lastes ned på nytt