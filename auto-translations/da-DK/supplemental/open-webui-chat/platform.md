<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver den forventede platformkonfiguration til at køre denne playbook.

## Påkrævede apps/frameworks

### Windows/Linux
Lemonade bør være forudinstalleret fra [her](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontend-webapp)
- **Lemonade Server** (backend-modelserver)

> Denne playbook kører **Lemonade** (Lemonade server/app) **nativt**. **Open WebUI** kører som en **container** på Linux (via Podman) og som en **Python-pakke** på Windows. `open-webui` PyPI-pakken understøtter kun Python ≤ 3.12, så Linux-containeren undgår at skulle håndtere ældre Python-versioner.  

## Modeller (i Lemonade)

Modeller bør downloades inde i **Lemonade-appen** (ved brug af den indbyggede Model Manager) eller via Lemonades kommandoer til modelhåndtering (`lemonade pull <model_name>`). Denne playbook antager, at nedenstående anbefalede modeller er downloadet og vises i modellisteendepunktet.

Kontroller modeltilgængelighed:
- Åbn: `http://localhost:13305/api/v1/models`
- Downloadede modeller vises under `"data"`.

### Anbefalede modeller

| Kapabilitet | Model-ID | Bemærkninger |
|---|----|-----|
| LLM (Tekstinput → Tekstoutput) | `Qwen3-4B-Hybrid` (eller lignende) | Enhver Lemonade LLM-model til chat, tekstfuldførelse, kodning eller ræsonnering |
| VLM (Billede → Tekst) | `Qwen3.5-4B-GGUF` (eller enhver model i kategorien **Vision**) | Enhver multimodal/synskapabel model, der kan tage billeder som en del af sit input |
| Billedgenerering (Tekst → Billede) | `SDXL-Turbo` (eller enhver model i kategorien **Image**) | Enhver Stable Diffusion-model, der genererer billeder ud fra en tekstprompt |
| Lyd (Tale → Tekst) | `Whisper-Large-v3` (eller enhver model i kategorien **Audio**) | Enhver ASR-model, der konverterer lyd til tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Anvendte porte

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Hvis disse porte allerede er i brug på dit system, skal du ændre dem, når du starter serveren/serverne.