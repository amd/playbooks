<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávanou konfiguraci platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky

### Windows/Linux
Lemonade by mělo být předem nainstalováno [odsud](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontendová webová aplikace)
- **Lemonade Server** (backendový server modelů)

> Tento playbook spouští **Lemonade** (Lemonade server/aplikaci) **nativně**. **Open WebUI** běží jako **kontejner** na Linuxu (pomocí Podman) a jako **Python balíček** na Windows. Balíček `open-webui` z PyPI podporuje pouze Python ≤ 3.12, takže kontejner na Linuxu umožňuje vyhnout se nutnosti spravovat starší verze Pythonu.  

## Modely (v Lemonade)

Modely by měly být stahovány přímo v **aplikaci Lemonade** (pomocí vestavěného Model Manageru) nebo pomocí příkazů pro správu modelů v Lemonade (`lemonade pull <model_name>`). Tento playbook předpokládá, že níže doporučené modely jsou stažené a zobrazují se v koncovém bodu seznamu modelů.

Kontrola dostupnosti modelů:
- Otevřete: `http://localhost:13305/api/v1/models`
- Stažené modely budou uvedeny pod `"data"`.

### Doporučené modely

| Schopnost | ID modelu | Poznámky |
|---|----|-----|
| LLM (Text na vstupu → Text na výstupu) | `Qwen3-4B-Hybrid` (nebo podobný) | Libovolný LLM model z Lemonade pro chat, doplňování textu, kódování nebo uvažování |
| VLM (Obrázek → Text) | `Qwen3.5-4B-GGUF` (nebo jakýkoli model v kategorii **Vision**) | Libovolný multimodální model se schopností zpracování obrázků, který dokáže přijímat obrázky jako součást svého vstupu |
| Generování obrázků (Text → Obrázek) | `SDXL-Turbo` (nebo jakýkoli model v kategorii **Image**) | Libovolný model Stable Diffusion, který generuje obrázky na základě textové výzvy |
| Zvuk (Řeč → Text) | `Whisper-Large-v3` (nebo jakýkoli model v kategorii **Audio**) | Libovolný ASR model, který převádí zvuk na text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Používané porty

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Pokud jsou tyto porty ve vašem systému již používány, změňte je při spouštění serveru(ů).