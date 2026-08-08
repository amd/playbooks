<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguratie voor het uitvoeren van deze playbook.

## Vereiste apps/frameworks

### Windows/Linux
Lemonade moet vooraf zijn geïnstalleerd vanaf [hier](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontend webapp)
- **Lemonade Server** (backend modelserver)

> Deze playbook draait **Lemonade** (Lemonade server/app) **native**. **Open WebUI** draait als een **container** op Linux (via Podman) en als een **Python-package** op Windows. Het `open-webui` PyPI-package ondersteunt alleen Python ≤ 3.12, dus de Linux-container voorkomt dat oudere Python-versies beheerd moeten worden.  

## Modellen (in Lemonade)

Modellen moeten worden gedownload binnen de **Lemonade-app** (met behulp van de ingebouwde Model Manager) of via de modelbeheercommando's van Lemonade (`lemonade pull <model_name>`). Deze playbook gaat ervan uit dat de onderstaande aanbevolen modellen zijn gedownload en verschijnen in het models-lijst-endpoint.

Controleer de beschikbaarheid van modellen:
- Open: `http://localhost:13305/api/v1/models`
- Gedownloade modellen worden vermeld onder `"data"`.

### Aanbevolen modellen

| Mogelijkheid | Model-ID | Opmerkingen |
|---|----|-----|
| LLM (Tekstinvoer → Tekstuitvoer) | `Qwen3-4B-Hybrid` (of vergelijkbaar) | Elk Lemonade LLM-model voor chat, tekstaanvulling, codering of redeneren |
| VLM (Afbeelding → Tekst) | `Qwen3.5-4B-GGUF` (of elk model in de categorie **Vision**) | Elk multimodaal/visiongeschikt model dat afbeeldingen als onderdeel van de invoer kan verwerken |
| Beeldgeneratie (Tekst → Afbeelding) | `SDXL-Turbo` (of elk model in de categorie **Image**) | Elk Stable Diffusion-model dat afbeeldingen genereert op basis van een tekstprompt |
| Audio (Spraak → Tekst) | `Whisper-Large-v3` (of elk model in de categorie **Audio**) | Elk ASR-model dat audio omzet in tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Gebruikte poorten

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Als deze poorten al in gebruik zijn op uw systeem, wijzig ze dan bij het starten van de server(s).