<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration

Detta dokument beskriver den förväntade plattformskonfigurationen för att köra denna playbook.

## Obligatoriska appar/ramverk

### Windows/Linux
Lemonade bör vara förinstallerat från [här](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (webbapp för frontend)
- **Lemonade Server** (backend-modellserver)

> Denna playbook kör **Lemonade** (Lemonade server/app) **nativt**. **Open WebUI** körs som en **container** på Linux (via Podman) och som ett **Python-paket** på Windows. PyPI-paketet `open-webui` stöder endast Python ≤ 3.12, så Linux-containern gör det möjligt att slippa hantera äldre Python-versioner.  

## Modeller (i Lemonade)

Modeller bör laddas ner inuti **Lemonade-appen** (med den inbyggda Model Manager) eller via Lemonades kommandon för modellhantering (`lemonade pull <model_name>`). Denna playbook förutsätter att nedanstående rekommenderade modeller är nedladdade och visas i modellernas liständpunkt.

Kontrollera modelltillgänglighet:
- Öppna: `http://localhost:13305/api/v1/models`
- Nedladdade modeller listas under `"data"`.

### Rekommenderade modeller

| Funktion | Modell-ID | Anteckningar |
|---|----|-----|
| LLM (Text in → Text ut) | `Qwen3-4B-Hybrid` (eller liknande) | Vilken Lemonade LLM-modell som helst för chatt, textkomplettering, kodning eller resonemang |
| VLM (Bild → Text) | `Qwen3.5-4B-GGUF` (eller valfri modell i kategorin **Vision**) | Vilken multimodal/synförmögen modell som helst som kan ta bilder som en del av sin indata |
| Bildgenerering (Text → Bild) | `SDXL-Turbo` (eller valfri modell i kategorin **Image**) | Vilken Stable Diffusion-modell som helst som genererar bilder utifrån en textprompt |
| Ljud (Tal → Text) | `Whisper-Large-v3` (eller valfri modell i kategorin **Audio**) | Vilken ASR-modell som helst som omvandlar ljud till text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Portar som används

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Om dessa portar redan används på ditt system, ändra dem när du startar servern/servrarna.