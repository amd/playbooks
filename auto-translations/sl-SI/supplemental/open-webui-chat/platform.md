<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovano konfiguracijo platforme za izvajanje tega playbooka.

## Zahtevane aplikacije/ogrodja

### Windows/Linux
Lemonade mora biti vnaprej nameščen [od tukaj](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (spletna aplikacija za uporabniški vmesnik)
- **Lemonade Server** (zaledni strežnik za modele)

> Ta playbook izvaja **Lemonade** (Lemonade server/app) **nativno**. **Open WebUI** se na Linuxu izvaja kot **vsebnik** (prek Podman), na Windows pa kot **Python paket**. Paket `open-webui` na PyPI podpira le Python ≤ 3.12, zato se z Linux vsebnikom izognemo potrebi po upravljanju starejših različic Pythona.  

## Modeli (v Lemonade)

Modele je treba prenesti znotraj **aplikacije Lemonade** (z uporabo vgrajenega Model Managerja) ali prek ukazov za upravljanje modelov v Lemonade (`lemonade pull <model_name>`). Ta playbook predpostavlja, da so spodaj priporočeni modeli preneseni in prikazani na končni točki seznama modelov.

Preverjanje razpoložljivosti modelov:
- Odprite: `http://localhost:13305/api/v1/models`
- Preneseni modeli bodo navedeni pod `"data"`.

### Priporočeni modeli

| Zmogljivost | ID modela | Opombe |
|---|----|-----|
| LLM (vhod besedilo → izhod besedilo) | `Qwen3-4B-Hybrid` (ali podoben) | Kateri koli model LLM v Lemonade za klepet, dokončevanje besedila, kodiranje ali sklepanje |
| VLM (slika → besedilo) | `Qwen3.5-4B-GGUF` (ali kateri koli model v kategoriji **Vision**) | Kateri koli multimodalni model, ki podpira vid in lahko kot del vhoda sprejme slike |
| Generiranje slik (besedilo → slika) | `SDXL-Turbo` (ali kateri koli model v kategoriji **Image**) | Kateri koli model Stable Diffusion, ki generira slike na podlagi besedilnega poziva |
| Zvok (govor → besedilo) | `Whisper-Large-v3` (ali kateri koli model v kategoriji **Audio**) | Kateri koli model ASR, ki pretvarja zvok v besedilo |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Uporabljena vrata

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Če so ta vrata na vašem sistemu že v uporabi, jih ob zagonu strežnika(-ov) spremenite.