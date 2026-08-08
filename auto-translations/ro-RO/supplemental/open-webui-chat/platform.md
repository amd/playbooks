<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Configurarea platformei

Acest document descrie configurarea platformei preconizată pentru rularea acestui playbook.

## Aplicații/framework-uri necesare

### Windows/Linux
Lemonade ar trebui să fie preinstalat de [aici](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (aplicație web frontend)
- **Lemonade Server** (server backend pentru modele)

> Acest playbook rulează **Lemonade** (Lemonade server/app) **nativ**. **Open WebUI** rulează ca un **container** pe Linux (prin Podman) și ca un **pachet Python** pe Windows. Pachetul PyPI `open-webui` este compatibil doar cu Python ≤ 3.12, astfel încât containerul Linux evită necesitatea gestionării unor versiuni mai vechi de Python.  

## Modele (în Lemonade)

Modelele ar trebui descărcate în interiorul **aplicației Lemonade** (folosind Model Manager-ul integrat) sau prin comenzile de gestionare a modelelor din Lemonade (`lemonade pull <model_name>`). Acest playbook presupune că modelele recomandate de mai jos sunt descărcate și apar în endpoint-ul cu lista de modele.

Verificați disponibilitatea modelelor:
- Deschideți: `http://localhost:13305/api/v1/models`
- Modelele descărcate vor fi listate sub `"data"`.

### Modele recomandate

| Capabilitate | ID model | Note |
|---|----|-----|
| LLM (Intrare text → Ieșire text) | `Qwen3-4B-Hybrid` (sau similar) | Orice model LLM din Lemonade pentru chat, completare de text, programare sau raționament |
| VLM (Imagine → Text) | `Qwen3.5-4B-GGUF` (sau orice model din categoria **Vision**) | Orice model multimodal/cu capabilități vizuale care poate prelua imagini ca parte din datele de intrare |
| Generare de imagini (Text → Imagine) | `SDXL-Turbo` (sau orice model din categoria **Image**) | Orice model Stable Diffusion care generează imagini pe baza unui prompt text |
| Audio (Vorbire → Text) | `Whisper-Large-v3` (sau orice model din categoria **Audio**) | Orice model ASR care convertește audio în text |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Porturi utilizate

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Dacă aceste porturi sunt deja utilizate pe sistemul dumneavoastră, schimbați-le la pornirea serverului(elor).