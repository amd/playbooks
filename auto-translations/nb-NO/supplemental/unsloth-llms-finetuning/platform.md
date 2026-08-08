<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spillboken.

## Forutsetninger

PyTorch med ROCm-støtte er forhåndsinstallert på AMD Ryzen™ AI Halo Developer Platform. For alle andre enheter må brukere installere PyTorch med ROCm-støtte manuelt. Se det relevante avsnittet for operativsystemet ditt:


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

| Modell | Parametere | Størrelse | Nedlastingssted |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Last ned fra HF

Modeller lastes automatisk ned til Hugging Face-hurtigbufferkatalogen: `~/.cache/huggingface/hub/`

Sørg for at det er minst **20 GB ledig plass** til modellagring.

## Nettverkskrav

Førstegangsoppsett krever internettilgang for å laste ned modeller fra Hugging Face. Etter nedlasting kan spillboken kjøres frakoblet.

- Første gangs nedlasting av modeller kan ta **5–10 minutter**, avhengig av modellstørrelse og tilkoblingshastighet
- Modeller mellomlagres lokalt og trenger ikke lastes ned på nytt