<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguráció

Ez a dokumentum ismerteti a playbook futtatásához szükséges platformkonfigurációt.

## Szükséges alkalmazások/keretrendszerek

### Windows/Linux
A Lemonade-et előzetesen telepíteni kell [innen](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (frontend webalkalmazás)
- **Lemonade Server** (háttérben futó modellkiszolgáló)

> Ez a playbook **natívan** futtatja a **Lemonade**-et (Lemonade server/app). Az **Open WebUI** Linuxon **konténerként** fut (Podmanon keresztül), Windowson pedig **Python csomagként**. Az `open-webui` PyPI csomag csak Python ≤ 3.12 verziót támogat, így a Linux konténer megkíméli a felhasználót a régebbi Python-verziók kezelésétől.  

## Modellek (a Lemonade-ben)

A modelleket a **Lemonade alkalmazáson** belül (a beépített Model Manager segítségével) vagy a Lemonade modellkezelő parancsain keresztül (`lemonade pull <model_name>`) kell letölteni. Ez a playbook feltételezi, hogy az alábbi ajánlott modellek le vannak töltve, és megjelennek a modellek listázási végpontjában.

A modellek elérhetőségének ellenőrzése:
- Nyisd meg: `http://localhost:13305/api/v1/models`
- A letöltött modellek a `"data"` alatt lesznek felsorolva.

### Ajánlott modellek

| Képesség | Modellazonosító | Megjegyzések |
|---|----|-----|
| LLM (Szöveg bemenet → Szöveg kimenet) | `Qwen3-4B-Hybrid` (vagy hasonló) | Bármely Lemonade LLM modell csevegéshez, szövegkiegészítéshez, kódoláshoz vagy következtetéshez |
| VLM (Kép → Szöveg) | `Qwen3.5-4B-GGUF` (vagy bármely modell a **Vision** kategóriában) | Bármely multimodális/vizuális képességű modell, amely képeket is tud fogadni bemenetként |
| Képgenerálás (Szöveg → Kép) | `SDXL-Turbo` (vagy bármely modell az **Image** kategóriában) | Bármely Stable Diffusion modell, amely egy szöveges promptból képeket generál |
| Hang (Beszéd → Szöveg) | `Whisper-Large-v3` (vagy bármely modell az **Audio** kategóriában) | Bármely ASR modell, amely hangot alakít át szöveggé |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Használt portok

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Ha ezek a portok már használatban vannak a rendszereden, módosítsd őket a szerver(ek) indításakor.