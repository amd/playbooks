<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spilleboken.

## Forutsetninger

PyTorch med ROCm-støtte er forhåndsinstallert på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheter må brukere installere PyTorch med ROCm-støtte manuelt. Se relevant seksjon for ditt operativsystem:

### Windows

| Komponent     | Versjon         | Merknader                             |
|---------------|-----------------|---------------------------------------|
| **PyTorch**   | 2.9 eller nyere    | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

### Linux

| Komponent     | Versjon         | Merknader                             |
|---------------|-----------------|---------------------------------------|
| **PyTorch**   | 2.9 eller nyere    | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

## Nødvendige modeller

Følgende modeller er testet og optimalisert for din plattform:

| Modell | Parametere | Størrelse | Nedlastingssted |
|--------|------------|-----------|-----------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

Modeller lastes automatisk ned til Hugging Face sin hurtigbufferkatalog:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Sørg for minst **50 GB ledig plass** for modelllagring.

## Nettverkskrav

Første gangs oppsett krever internettilgang for å laste ned modeller fra Hugging Face. Etter nedlasting kan spilleboken kjøres uten nett.

- Første gangs nedlasting av modeller kan ta **5–10 minutter** avhengig av modellstørrelse og tilkoblingshastighet
- Modeller bufres lokalt og trenger ikke lastes ned på nytt