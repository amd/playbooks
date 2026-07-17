<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwartete Plattformkonfiguration für die Ausführung dieses Playbooks.

## Erforderliche Apps/Frameworks

### Windows/Linux
Lemonade sollte vorab von [hier](https://lemonade-server.ai/install_options.html) installiert werden.

- **Open WebUI** (Frontend-Webanwendung)
- **Lemonade Server** (Backend-Modellserver)

> Dieses Playbook führt **Lemonade** (Lemonade Server/App) **nativ** aus. **Open WebUI** läuft als **Container** unter Linux (via Podman) und als **Python-Paket** unter Windows. Das `open-webui` PyPI-Paket unterstützt nur Python ≤ 3.12, weshalb der Linux-Container die Verwaltung älterer Python-Versionen überflüssig macht.

## Modelle (in Lemonade)

Modelle sollten innerhalb der **Lemonade-App** (über den integrierten Modell-Manager) oder über Lemonades Modellverwaltungsbefehle (`lemonade pull <model_name>`) heruntergeladen werden. Dieses Playbook setzt voraus, dass die unten empfohlenen Modelle heruntergeladen wurden und im Modelllistenendpunkt angezeigt werden.

Modellverfügbarkeit prüfen:
- Öffnen: `http://localhost:13305/api/v1/models`
- Heruntergeladene Modelle werden unter `"data"` aufgelistet.

### Empfohlene Modelle

| Fähigkeit | Modell-ID | Hinweise |
|---|----|-----|
| LLM (Texteingabe → Textausgabe) | `Qwen3-4B-Hybrid` (oder ähnlich) | Beliebiges Lemonade-LLM-Modell für Chat, Textvervollständigung, Programmierung oder Reasoning |
| VLM (Bild → Text) | `Qwen3.5-4B-GGUF` (oder ein beliebiges Modell der Kategorie **Vision**) | Beliebiges multimodales/visionsfähiges Modell, das Bilder als Teil der Eingabe verarbeiten kann |
| Bildgenerierung (Text → Bild) | `SDXL-Turbo` (oder ein beliebiges Modell der Kategorie **Image**) | Beliebiges Stable-Diffusion-Modell, das Bilder aus einer Texteingabe generiert |
| Audio (Sprache → Text) | `Whisper-Large-v3` (oder ein beliebiges Modell der Kategorie **Audio**) | Beliebiges ASR-Modell, das Audio in Text umwandelt |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Verwendete Ports

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Falls diese Ports auf Ihrem System bereits belegt sind, ändern Sie sie beim Starten der Server.