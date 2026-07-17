<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivanu konfiguraciju platforme za pokretanje ovog priručnika.

## Potrebne aplikacije/okviri

### Windows/Linux
Lemonade treba biti unapred instaliran odavde [ovde](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend veb aplikacija)
- **Lemonade Server** (pozadinski server modela)

> Ovaj priručnik pokreće **Lemonade** (Lemonade server/aplikacija) **nativno**. **Open WebUI** se pokreće kao **kontejner** na Linux-u (putem Podman-a) i kao **Python paket** na Windows-u. `open-webui` PyPI paket podržava samo Python ≤ 3.12, pa Linux kontejner izbegava potrebu za upravljanjem starijim verzijama Python-a.

## Modeli (u Lemonade)

Modeli treba da budu preuzeti unutar **Lemonade aplikacije** (koristeći ugrađeni Menadžer modela) ili putem Lemonade komandi za upravljanje modelima (`lemonade pull <model_name>`). Ovaj priručnik pretpostavlja da su preporučeni modeli navedeni ispod preuzeti i da se prikazuju na krajnjoj tački liste modela.

Proverite dostupnost modela:
- Otvorite: `http://localhost:13305/api/v1/models`
- Preuzeti modeli biće navedeni pod `"data"`.

### Preporučeni modeli

| Mogućnost | ID modela | Napomene |
|---|----|-----|
| LLM (Tekstualni ulaz → Tekstualni izlaz) | `Qwen3-4B-Hybrid` (ili sličan) | Bilo koji Lemonade LLM model za ćaskanje, dopunjavanje teksta, kodiranje ili zaključivanje |
| VLM (Slika → Tekst) | `Qwen3.5-4B-GGUF` (ili bilo koji model iz kategorije **Vision**) | Bilo koji multimodalni/vizuelno sposobni model koji može da prima slike kao deo ulaza |
| Generisanje slika (Tekst → Slika) | `SDXL-Turbo` (ili bilo koji model iz kategorije **Image**) | Bilo koji Stable Diffusion model koji generiše slike na osnovu tekstualnog upita |
| Audio (Govor → Tekst) | `Whisper-Large-v3` (ili bilo koji model iz kategorije **Audio**) | Bilo koji ASR model koji konvertuje audio u tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Korišćeni portovi

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Ako su ovi portovi već u upotrebi na vašem sistemu, promenite ih prilikom pokretanja servera.