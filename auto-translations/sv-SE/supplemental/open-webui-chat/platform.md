<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration

Det här dokumentet beskriver den förväntade plattformskonfigurationen för att köra den här spelboken.

## Nödvändiga appar/ramverk

### Windows/Linux
Lemonade bör vara förinstallerat från [här](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend-webbapp)
- **Lemonade Server** (backend-modellserver)

> Den här spelboken kör **Lemonade** (Lemonade server/app) **nativt**. **Open WebUI** körs som en **container** på Linux (via Podman) och som ett **Python-paket** på Windows. PyPI-paketet `open-webui` stöder endast Python ≤ 3.12, så Linux-containern undviker behovet av att hantera äldre Python-versioner.

## Modeller (i Lemonade)

Modeller bör laddas ned i **Lemonade-appen** (med den inbyggda modellhanteraren) eller via Lemonades modellhanteringskommandon (`lemonade pull <model_name>`). Den här spelboken förutsätter att de rekommenderade modellerna nedan är nedladdade och visas i modelllistans slutpunkt.

Kontrollera modelltillgänglighet:
- Öppna: `http://localhost:13305/api/v1/models`
- Nedladdade modeller listas under `"data"`.

### Rekommenderade modeller

| Kapabilitet | Modell-ID | Anteckningar |
|---|----|-----|
| LLM (Textinmatning → Textutmatning) | `Qwen3-4B-Hybrid` (eller liknande) | Valfri Lemonade LLM-modell för chatt, textkomplettering, kodning eller resonemang |
| VLM (Bild → Text) | `Qwen3.5-4B-GGUF` (eller valfri modell i kategorin **Vision**) | Valfri multimodal/synkapabel modell som kan ta emot bilder som en del av sin inmatning |
| Bildgenerering (Text → Bild) | `SDXL-Turbo` (eller valfri modell i kategorin **Image**) | Valfri Stable Diffusion-modell som genererar bilder från en textprompt |
| Ljud (Tal → Text) | `Whisper-Large-v3` (eller valfri modell i kategorin **Audio**) | Valfri ASR-modell som konverterar ljud till text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Portar som används

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Om dessa portar redan används på ditt system, ändra dem när du startar servern/servrarna.