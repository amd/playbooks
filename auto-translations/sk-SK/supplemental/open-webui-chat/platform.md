<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávanú konfiguráciu platformy na spustenie tejto príručky.

## Požadované aplikácie/frameworky

### Windows/Linux
Lemonade by mal byť predinštalovaný odtiaľto: [here](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontendová webová aplikácia)
- **Lemonade Server** (backendový model server)

> Táto príručka spúšťa **Lemonade** (Lemonade server/aplikácia) **natívne**. **Open WebUI** beží ako **kontajner** na Linuxe (cez Podman) a ako **Python balík** na Windows. Balík `open-webui` z PyPI podporuje iba Python ≤ 3.12, takže Linuxový kontajner umožňuje vyhnúť sa nutnosti spravovať staršie verzie Pythonu.  

## Modely (v Lemonade)

Modely by sa mali sťahovať v rámci **aplikácie Lemonade** (pomocou vstavaného Model Manager) alebo prostredníctvom príkazov na správu modelov v Lemonade (`lemonade pull <model_name>`). Táto príručka predpokladá, že nižšie odporúčané modely sú stiahnuté a zobrazujú sa v koncovom bode zoznamu modelov.

Kontrola dostupnosti modelov:
- Otvorte: `http://localhost:13305/api/v1/models`
- Stiahnuté modely budú uvedené v časti `"data"`.

### Odporúčané modely

| Schopnosť | ID modelu | Poznámky |
|---|----|-----|
| LLM (textový vstup → textový výstup) | `Qwen3-4B-Hybrid` (alebo podobný) | Akýkoľvek LLM model v Lemonade na chat, dopĺňanie textu, programovanie alebo uvažovanie |
| VLM (obrázok → text) | `Qwen3.5-4B-GGUF` (alebo akýkoľvek model v kategórii **Vision**) | Akýkoľvek multimodálny model schopný spracovať vizuálne vstupy ako súčasť vstupných dát |
| Generovanie obrázkov (text → obrázok) | `SDXL-Turbo` (alebo akýkoľvek model v kategórii **Image**) | Akýkoľvek model Stable Diffusion, ktorý generuje obrázky na základe textového zadania |
| Zvuk (reč → text) | `Whisper-Large-v3` (alebo akýkoľvek model v kategórii **Audio**) | Akýkoľvek ASR model, ktorý prevádza zvuk na text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Použité porty

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Ak sú tieto porty vo vašom systéme už použité, zmeňte ich pri spúšťaní servera(-ov).