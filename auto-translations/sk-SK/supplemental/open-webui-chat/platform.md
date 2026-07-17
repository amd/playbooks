<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy

Tento dokument popisuje očakávanú konfiguráciu platformy pre spustenie tohto playbooku.

## Požadované aplikácie/frameworky

### Windows/Linux
Lemonade by mal byť vopred nainštalovaný odtiaľto [tu](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontendová webová aplikácia)
- **Lemonade Server** (backendový modelový server)

> Tento playbook spúšťa **Lemonade** (Lemonade server/aplikácia) **natívne**. **Open WebUI** beží ako **kontajner** na Linuxe (cez Podman) a ako **Python balík** na Windowse. Balík `open-webui` PyPI podporuje iba Python ≤ 3.12, takže linuxový kontajner sa vyhýba nutnosti spravovať staršie verzie Pythonu.

## Modely (v Lemonade)

Modely by mali byť stiahnuté v rámci **aplikácie Lemonade** (pomocou vstavaného správcu modelov) alebo prostredníctvom príkazov na správu modelov Lemonade (`lemonade pull <model_name>`). Tento playbook predpokladá, že nižšie odporúčané modely sú stiahnuté a zobrazujú sa v koncovom bode zoznamu modelov.

Skontrolujte dostupnosť modelov:
- Otvorte: `http://localhost:13305/api/v1/models`
- Stiahnuté modely budú uvedené pod `"data"`.

### Odporúčané modely

| Schopnosť | ID modelu | Poznámky |
|---|----|-----|
| LLM (Textový vstup → Textový výstup) | `Qwen3-4B-Hybrid` (alebo podobný) | Akýkoľvek LLM model Lemonade pre chat, dokončovanie textu, kódovanie alebo uvažovanie |
| VLM (Obrázok → Text) | `Qwen3.5-4B-GGUF` (alebo akýkoľvek model v kategórii **Vision**) | Akýkoľvek multimodálny/vizuálne schopný model, ktorý dokáže prijímať obrázky ako súčasť vstupu |
| Generovanie obrázkov (Text → Obrázok) | `SDXL-Turbo` (alebo akýkoľvek model v kategórii **Image**) | Akýkoľvek model Stable Diffusion, ktorý generuje obrázky na základe textovej výzvy |
| Zvuk (Reč → Text) | `Whisper-Large-v3` (alebo akýkoľvek model v kategórii **Audio**) | Akýkoľvek ASR model, ktorý konvertuje zvuk na text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Používané porty

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Ak sú tieto porty na vašom systéme už obsadené, zmeňte ich pri spúšťaní servera (serverov).