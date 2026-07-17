<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum leírja a playbook futtatásához szükséges platform-konfigurációt.

## Szükséges alkalmazások/keretrendszerek

### Windows/Linux
A Lemonade-et előre telepíteni kell [innen](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend webalkalmazás)
- **Lemonade Server** (backend modellkiszolgáló)

> Ez a playbook a **Lemonade**-et (Lemonade szerver/alkalmazás) **natívan** futtatja. Az **Open WebUI** Linuxon **konténerként** fut (Podman segítségével), Windowson pedig **Python-csomagként**. Az `open-webui` PyPI-csomag csak Python ≤ 3.12 verziót támogat, ezért a Linux-konténer használatával elkerülhető a régebbi Python-verziók kezelése.

## Modellek (Lemonade-ben)

A modelleket a **Lemonade alkalmazáson** belül kell letölteni (a beépített Model Manager segítségével), vagy a Lemonade modellkezelési parancsaival (`lemonade pull <model_name>`). Ez a playbook feltételezi, hogy az alábbi ajánlott modellek le vannak töltve, és megjelennek a modellek listájának végpontján.

Modell elérhetőségének ellenőrzése:
- Nyisd meg: `http://localhost:13305/api/v1/models`
- A letöltött modellek a `"data"` alatt lesznek felsorolva.

### Ajánlott modellek

| Képesség | Modell azonosítója | Megjegyzések |
|---|----|-----|
| LLM (Szöveges bemenet → Szöveges kimenet) | `Qwen3-4B-Hybrid` (vagy hasonló) | Bármely Lemonade LLM-modell csevegéshez, szövegkiegészítéshez, kódoláshoz vagy következtetéshez |
| VLM (Kép → Szöveg) | `Qwen3.5-4B-GGUF` (vagy bármely modell a **Vision** kategóriából) | Bármely multimodális/látásképes modell, amely képeket is fogadhat bemenetként |
| Képgenerálás (Szöveg → Kép) | `SDXL-Turbo` (vagy bármely modell az **Image** kategóriából) | Bármely Stable Diffusion-modell, amely szöveges utasítás alapján képeket generál |
| Hang (Beszéd → Szöveg) | `Whisper-Large-v3` (vagy bármely modell az **Audio** kategóriából) | Bármely ASR-modell, amely hangot szöveggé alakít |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Használt portok

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Ha ezek a portok már foglaltak a rendszereden, módosítsd őket a szerver(ek) indításakor.