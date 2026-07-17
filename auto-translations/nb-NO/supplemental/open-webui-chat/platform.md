<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver den forventede plattformkonfigurasjonen for å kjøre denne spilleboken.

## Nødvendige apper/rammeverk

### Windows/Linux
Lemonade bør være forhåndsinstallert fra [her](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend-nettapp)
- **Lemonade Server** (backend-modelltjener)

> Denne spilleboken kjører **Lemonade** (Lemonade-server/app) **innebygd**. **Open WebUI** kjører som en **container** på Linux (via Podman) og som en **Python-pakke** på Windows. `open-webui` PyPI-pakken støtter kun Python ≤ 3.12, så Linux-containeren unngår behovet for å håndtere eldre Python-versjoner.

## Modeller (i Lemonade)

Modeller bør lastes ned inne i **Lemonade-appen** (ved hjelp av den innebygde modellbehandleren) eller via Lemonades modellbehandlingskommandoer (`lemonade pull <model_name>`). Denne spilleboken forutsetter at de anbefalte modellene nedenfor er lastet ned og vises i modelllistens endepunkt.

Sjekk modelltilgjengelighet:
- Åpne: `http://localhost:13305/api/v1/models`
- Nedlastede modeller vil være oppført under `"data"`.

### Anbefalte modeller

| Funksjonalitet | Modell-ID | Merknader |
|---|----|-----|
| LLM (Tekstinndata → Tekstutdata) | `Qwen3-4B-Hybrid` (eller lignende) | Enhver Lemonade LLM-modell for chat, tekstfullføring, koding eller resonnering |
| VLM (Bilde → Tekst) | `Qwen3.5-4B-GGUF` (eller en hvilken som helst modell i kategorien **Vision**) | Enhver multimodal/visjonskapabel modell som kan ta bilder som del av inndataene |
| Bildegenerering (Tekst → Bilde) | `SDXL-Turbo` (eller en hvilken som helst modell i kategorien **Image**) | Enhver Stable Diffusion-modell som genererer bilder fra en tekstforespørsel |
| Lyd (Tale → Tekst) | `Whisper-Large-v3` (eller en hvilken som helst modell i kategorien **Audio**) | Enhver ASR-modell som konverterer lyd til tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Porter som brukes

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Hvis disse portene allerede er i bruk på systemet ditt, endre dem når du starter tjeneren(e).