<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávanou konfiguraci platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky

### Windows/Linux
Lemonade by mělo být předem nainstalováno odtud: [zde](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontendová webová aplikace)
- **Lemonade Server** (backendový modelový server)

> Tento playbook spouští **Lemonade** (server/aplikaci Lemonade) **nativně**. **Open WebUI** běží jako **kontejner** na Linuxu (přes Podman) a jako **balíček Python** na Windows. Balíček `open-webui` PyPI podporuje pouze Python ≤ 3.12, takže linuxový kontejner zabraňuje nutnosti spravovat starší verze Pythonu.

## Modely (v Lemonade)

Modely by měly být staženy v **aplikaci Lemonade** (pomocí vestavěného Správce modelů) nebo prostřednictvím příkazů pro správu modelů Lemonade (`lemonade pull <model_name>`). Tento playbook předpokládá, že níže doporučené modely jsou staženy a zobrazují se v koncovém bodu seznamu modelů.

Ověření dostupnosti modelů:
- Otevřete: `http://localhost:13305/api/v1/models`
- Stažené modely budou uvedeny pod `"data"`.

### Doporučené modely

| Schopnost | ID modelu | Poznámky |
|---|----|-----|
| LLM (textový vstup → textový výstup) | `Qwen3-4B-Hybrid` (nebo podobný) | Jakýkoli LLM model Lemonade pro chat, dokončování textu, kódování nebo uvažování |
| VLM (obrázek → text) | `Qwen3.5-4B-GGUF` (nebo jakýkoli model v kategorii **Vision**) | Jakýkoli multimodální/vizuálně schopný model, který může přijímat obrázky jako součást vstupu |
| Generování obrázků (text → obrázek) | `SDXL-Turbo` (nebo jakýkoli model v kategorii **Image**) | Jakýkoli model Stable Diffusion, který generuje obrázky na základě textového promptu |
| Zvuk (řeč → text) | `Whisper-Large-v3` (nebo jakýkoli model v kategorii **Audio**) | Jakýkoli ASR model, který převádí zvuk na text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Používané porty

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Pokud jsou tyto porty ve vašem systému již obsazeny, změňte je při spouštění serveru (serverů).