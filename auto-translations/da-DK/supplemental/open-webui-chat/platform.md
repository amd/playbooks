<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformkonfiguration

Dette dokument beskriver den forventede platformkonfiguration til at køre dette playbook.

## Påkrævede apps/frameworks

### Windows/Linux
Lemonade skal være forudinstalleret fra [her](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend-webapplikation)
- **Lemonade Server** (backend-modelserver)

> Dette playbook kører **Lemonade** (Lemonade server/app) **native**. **Open WebUI** kører som en **container** på Linux (via Podman) og som en **Python-pakke** på Windows. `open-webui` PyPI-pakken understøtter kun Python ≤ 3.12, så Linux-containeren undgår behovet for at håndtere ældre Python-versioner.

## Modeller (i Lemonade)

Modeller skal downloades inde i **Lemonade-appen** (ved hjælp af den indbyggede Model Manager) eller via Lemonades modeladministrationskommandoer (`lemonade pull <model_name>`). Dette playbook forudsætter, at de anbefalede modeller nedenfor er downloadet og vises i modelliste-endpointet.

Kontrollér modeladgang:
- Åbn: `http://localhost:13305/api/v1/models`
- Downloadede modeller vil være oplistet under `"data"`.

### Anbefalede modeller

| Kapabilitet | Model-ID | Noter |
|---|----|-----|
| LLM (Tekstinput → Tekstoutput) | `Qwen3-4B-Hybrid` (eller lignende) | Enhver Lemonade LLM-model til chat, tekstfuldførelse, kodning eller ræsonnering |
| VLM (Billede → Tekst) | `Qwen3.5-4B-GGUF` (eller en hvilken som helst model i kategorien **Vision**) | Enhver multimodal/visionsdygtig model, der kan tage billeder som en del af sit input |
| Billedgenerering (Tekst → Billede) | `SDXL-Turbo` (eller en hvilken som helst model i kategorien **Image**) | Enhver Stable Diffusion-model, der genererer billeder ud fra en tekstprompt |
| Lyd (Tale → Tekst) | `Whisper-Large-v3` (eller en hvilken som helst model i kategorien **Audio**) | Enhver ASR-model, der konverterer lyd til tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Anvendte porte

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Hvis disse porte allerede er i brug på dit system, skal du ændre dem, når du starter serveren/serverne.