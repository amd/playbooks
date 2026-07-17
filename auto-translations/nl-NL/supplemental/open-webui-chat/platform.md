<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguratie voor het uitvoeren van dit playbook.

## Vereiste apps/frameworks

### Windows/Linux
Lemonade dient vooraf geïnstalleerd te zijn via [hier](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend webapplicatie)
- **Lemonade Server** (backend modelserver)

> Dit playbook voert **Lemonade** (Lemonade server/app) **native** uit. **Open WebUI** draait als een **container** op Linux (via Podman) en als een **Python-pakket** op Windows. Het `open-webui` PyPI-pakket ondersteunt alleen Python ≤ 3.12, waardoor de Linux-container het beheer van oudere Python-versies overbodig maakt.

## Modellen (in Lemonade)

Modellen dienen te worden gedownload binnen de **Lemonade-app** (via de ingebouwde Model Manager) of via de modelbeheercommando's van Lemonade (`lemonade pull <model_name>`). Dit playbook gaat ervan uit dat de onderstaande aanbevolen modellen zijn gedownload en worden weergegeven in het modellenlijst-eindpunt.

Controleer de beschikbaarheid van modellen:
- Open: `http://localhost:13305/api/v1/models`
- Gedownloade modellen worden vermeld onder `"data"`.

### Aanbevolen modellen

| Mogelijkheid | Model-ID | Opmerkingen |
|---|----|-----|
| LLM (Tekstinvoer → Tekstuitvoer) | `Qwen3-4B-Hybrid` (of vergelijkbaar) | Elk Lemonade LLM-model voor chat, tekstafronding, codering of redenering |
| VLM (Afbeelding → Tekst) | `Qwen3.5-4B-GGUF` (of een model in de categorie **Vision**) | Elk multimodaal/vision-geschikt model dat afbeeldingen als onderdeel van de invoer kan verwerken |
| Beeldgeneratie (Tekst → Afbeelding) | `SDXL-Turbo` (of een model in de categorie **Image**) | Elk Stable Diffusion-model dat afbeeldingen genereert op basis van een tekstprompt |
| Audio (Spraak → Tekst) | `Whisper-Large-v3` (of een model in de categorie **Audio**) | Elk ASR-model dat audio omzet naar tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Gebruikte poorten

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Als deze poorten al in gebruik zijn op uw systeem, wijzig ze dan bij het starten van de server(s).