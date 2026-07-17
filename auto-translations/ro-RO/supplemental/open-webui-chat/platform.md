<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei

Acest document descrie configurarea așteptată a platformei pentru rularea acestui playbook.

## Aplicații/Framework-uri Necesare

### Windows/Linux
Lemonade ar trebui să fie pre-instalat de [aici](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (aplicație web frontend)
- **Lemonade Server** (server backend pentru modele)

> Acest playbook rulează **Lemonade** (server/aplicație Lemonade) **nativ**. **Open WebUI** rulează ca un **container** pe Linux (prin Podman) și ca un **pachet Python** pe Windows. Pachetul PyPI `open-webui` suportă doar Python ≤ 3.12, astfel containerul Linux evită necesitatea gestionării versiunilor mai vechi de Python.

## Modele (în Lemonade)

Modelele ar trebui descărcate în **aplicația Lemonade** (folosind Managerul de Modele integrat) sau prin comenzile de gestionare a modelelor din Lemonade (`lemonade pull <model_name>`). Acest playbook presupune că modelele recomandate de mai jos sunt descărcate și apar în endpoint-ul listei de modele.

Verificați disponibilitatea modelelor:
- Deschideți: `http://localhost:13305/api/v1/models`
- Modelele descărcate vor fi listate sub `"data"`.

### Modele recomandate

| Capacitate | ID Model | Note |
|---|----|-----|
| LLM (Intrare text → Ieșire text) | `Qwen3-4B-Hybrid` (sau similar) | Orice model LLM din Lemonade pentru chat, completare text, programare sau raționament |
| VLM (Imagine → Text) | `Qwen3.5-4B-GGUF` (sau orice model din categoria **Vision**) | Orice model multimodal/cu capacitate vizuală care poate accepta imagini ca parte a intrării |
| Generare Imagini (Text → Imagine) | `SDXL-Turbo` (sau orice model din categoria **Image**) | Orice model Stable Diffusion care generează imagini pentru un prompt text |
| Audio (Vorbire → Text) | `Whisper-Large-v3` (sau orice model din categoria **Audio**) | Orice model ASR care convertește audio în text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Porturi utilizate

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Dacă aceste porturi sunt deja utilizate pe sistemul dumneavoastră, modificați-le la pornirea serverului (serverelor).