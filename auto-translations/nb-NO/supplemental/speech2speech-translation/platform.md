<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne playbooken.

## Forutsetninger

PyTorch med ROCm-støtte er forhåndsinstallert på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheter må brukere manuelt installere PyTorch med ROCm-støtte. Se den relevante seksjonen for ditt operativsystem:

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
| **facebook/seamless-m4t-v2-large** | 2,3B | ~10GB | Forhåndsinstallert på AMD Ryzen AI Halo Developer Platform; må installeres manuelt på alle andre enheter |

Modeller vil bli lastet ned automatisk til Hugging Face-hurtigbufferkatalogen:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Sørg for minst **20GB ledig plass** for lagring av modeller.

## Nettverkskrav

Førstegangsoppsett krever internettilgang for å laste ned modeller fra Hugging Face. Etter nedlasting kan playbooken kjøres uten nett.

- Nedlasting av modeller for første gang kan ta **5-10 minutter** avhengig av modellstørrelse og tilkoblingshastighet
- Modeller lagres i hurtigbufferen lokalt og trenger ikke å lastes ned på nytt