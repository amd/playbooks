<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivanu konfiguraciju platforme za pokretanje ovog playbook-a.

## Obavezne aplikacije/frameworkovi

### Windows/Linux
Lemonade treba biti unapred instaliran odavde [here](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (frontend veb aplikacija)
- **Lemonade Server** (bekend server modela)

> Ovaj playbook pokreće **Lemonade** (Lemonade server/aplikaciju) **nativno**. **Open WebUI** se pokreće kao **kontejner** na Linuxu (preko Podman-a) i kao **Python paket** na Windows-u. Paket `open-webui` sa PyPI podržava samo Python ≤ 3.12, tako da Linux kontejner izbegava potrebu za upravljanjem starijim verzijama Python-a.

## Modeli (u Lemonade)

Modeli treba da se preuzmu unutar **Lemonade aplikacije** (koristeći ugrađeni Model Manager) ili preko Lemonade komandi za upravljanje modelima (`lemonade pull <model_name>`). Ovaj playbook pretpostavlja da su preporučeni modeli ispod preuzeti i da se prikazuju u endpoint-u liste modela.

Provera dostupnosti modela:
- Otvorite: `http://localhost:13305/api/v1/models`
- Preuzeti modeli će biti navedeni pod `"data"`.

### Preporučeni modeli

| Mogućnost | ID modela | Napomene |
|---|----|-----|
| LLM (Tekstualni unos → Tekstualni izlaz) | `Qwen3-4B-Hybrid` (ili sličan) | Bilo koji Lemonade LLM model za ćaskanje, dovršavanje teksta, kodiranje ili rezonovanje |
| VLM (Slika → Tekst) | `Qwen3.5-4B-GGUF` (ili bilo koji model iz kategorije **Vision**) | Bilo koji multimodalni model sa podrškom za vizuelni sadržaj koji može da prihvati slike kao deo svog ulaza |
| Generisanje slika (Tekst → Slika) | `SDXL-Turbo` (ili bilo koji model iz kategorije **Image**) | Bilo koji Stable Diffusion model koji generiše slike na osnovu tekstualnog upita |
| Audio (Govor → Tekst) | `Whisper-Large-v3` (ili bilo koji model iz kategorije **Audio**) | Bilo koji ASR model koji pretvara audio u tekst |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Korišćeni portovi

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Ako su ovi portovi već u upotrebi na vašem sistemu, promenite ih prilikom pokretanja servera.