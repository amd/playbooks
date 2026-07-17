<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ta dokument opisuje pričakovano konfiguracijo platforme za izvajanje tega priročnika.

## Zahtevane aplikacije/ogrodja

### Windows/Linux
Lemonade mora biti predhodno nameščen od [tukaj](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (spletna aplikacija za frontend)
- **Lemonade Server** (strežnik modelov za backend)

> Ta priročnik izvaja **Lemonade** (strežnik/aplikacija Lemonade) **izvorno**. **Open WebUI** se izvaja kot **vsebnik** na Linuxu (prek Podmana) in kot **paket Python** na Windowsih. Paket `open-webui` PyPI podpira samo Python ≤ 3.12, zato se z Linuxovim vsebnikom izognemo upravljanju starejših različic Pythona.

## Modeli (v Lemonade)

Modele je treba prenesti znotraj **aplikacije Lemonade** (z vgrajenim upravljalnikom modelov) ali prek ukazov za upravljanje modelov Lemonade (`lemonade pull <model_name>`). Ta priročnik predpostavlja, da so spodaj priporočeni modeli preneseni in se prikažejo na končni točki seznama modelov.

Preverite razpoložljivost modelov:
- Odprite: `http://localhost:13305/api/v1/models`
- Preneseni modeli bodo navedeni pod `"data"`.

### Priporočeni modeli

| Zmogljivost | ID modela | Opombe |
|---|----|-----|
| LLM (besedilni vhod → besedilni izhod) | `Qwen3-4B-Hybrid` (ali podoben) | Kateri koli model LLM Lemonade za klepet, dokončanje besedila, kodiranje ali sklepanje |
| VLM (slika → besedilo) | `Qwen3.5-4B-GGUF` (ali kateri koli model v kategoriji **Vision**) | Kateri koli multimodalni/vizualno zmogljiv model, ki lahko sprejema slike kot del vhoda |
| Generiranje slik (besedilo → slika) | `SDXL-Turbo` (ali kateri koli model v kategoriji **Image**) | Kateri koli model Stable Diffusion, ki generira slike iz besedilnega poziva |
| Zvok (govor → besedilo) | `Whisper-Large-v3` (ali kateri koli model v kategoriji **Audio**) | Kateri koli model ASR, ki pretvori zvok v besedilo |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Uporabljena vrata

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Če so ta vrata na vašem sistemu že zasedena, jih spremenite ob zagonu strežnika(-ov).