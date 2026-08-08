<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver forventet plattformkonfigurasjon for å kjøre denne playbooken.

## Nødvendige apper/rammeverk

### Windows/Linux
Lemonade bør være forhåndsinstallert herfra [her](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontend-webapp)
- **Lemonade Server** (backend-modellserver)

> Denne playbooken kjører **Lemonade** (Lemonade server/app) **nativt**. **Open WebUI** kjører som en **container** på Linux (via Podman) og som en **Python-pakke** på Windows. `open-webui`-PyPI-pakken støtter kun Python ≤ 3.12, så Linux-containeren unngår behovet for å håndtere eldre Python-versjoner.  

## Modeller (i Lemonade)

Modeller bør lastes ned inne i **Lemonade-appen** (ved bruk av den innebygde Model Manager) eller via Lemonades kommandoer for modellhåndtering (`lemonade pull <model_name>`). Denne playbooken forutsetter at de anbefalte modellene nedenfor er lastet ned og vises i modellisteendepunktet.

Sjekk modelltilgjengelighet:
- Åpne: `http://localhost:13305/api/v1/models`
- Nedlastede modeller vil bli listet under `"data"`.

### Anbefalte modeller

| Kapabilitet | Modell-ID | Merknader |
|---|----|-----|
| LLM (tekstinndata → tekstutdata) | `Qwen3-4B-Hybrid` (eller lignende) | Enhver Lemonade LLM-modell for chat, tekstfullføring, koding eller resonnering |
| VLM (bilde → tekst) | `Qwen3.5-4B-GGUF` (eller enhver modell i **Vision**-kategorien) | Enhver multimodal/synskapabel modell som kan ta bilder som en del av inndataen sin |
| Bildegenerering (tekst → bilde) | `SDXL-Turbo` (eller enhver modell i **Image**-kategorien) | Enhver Stable Diffusion-modell som genererer bilder ut fra en tekstprompt |
| Lyd (tale → tekst) | `Whisper-Large-v3` (eller enhver modell i **Audio**-kategorien) | Enhver ASR-modell som konverterer lyd til tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Porter som brukes

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Hvis disse portene allerede er i bruk på systemet ditt, endre dem når du starter serveren(e).