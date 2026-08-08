<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwartete Plattformkonfiguration zur Ausführung dieses Playbooks.

## Erforderliche Apps/Frameworks

### Windows/Linux
Lemonade sollte bereits von [hier](https://lemonade-server.ai/install_options.html) vorinstalliert sein. 

- **Open WebUI** (Frontend-Webanwendung)
- **Lemonade Server** (Backend-Modellserver)

> Dieses Playbook führt **Lemonade** (Lemonade Server/App) **nativ** aus. **Open WebUI** läuft unter Linux als **Container** (über Podman) und unter Windows als **Python-Paket**. Das PyPI-Paket `open-webui` unterstützt nur Python ≤ 3.12, sodass der Linux-Container die Verwaltung älterer Python-Versionen überflüssig macht.  

## Modelle (in Lemonade)

Modelle sollten innerhalb der **Lemonade-App** (über den integrierten Model Manager) oder über Lemonades Modellverwaltungsbefehle (`lemonade pull <model_name>`) heruntergeladen werden. Dieses Playbook geht davon aus, dass die unten empfohlenen Modelle heruntergeladen wurden und im Endpunkt der Modellliste erscheinen.

Modellverfügbarkeit prüfen:
- Öffnen: `http://localhost:13305/api/v1/models`
- Heruntergeladene Modelle werden unter `"data"` aufgelistet.

### Empfohlene Modelle

| Fähigkeit | Modell-ID | Hinweise |
|---|----|-----|
| LLM (Texteingabe → Textausgabe) | `Qwen3-4B-Hybrid` (oder ähnlich) | Beliebiges Lemonade-LLM-Modell für Chat, Textvervollständigung, Coding oder Reasoning |
| VLM (Bild → Text) | `Qwen3.5-4B-GGUF` (oder ein beliebiges Modell in der Kategorie **Vision**) | Beliebiges multimodales/visionsfähiges Modell, das Bilder als Teil seiner Eingabe verarbeiten kann |
| Bildgenerierung (Text → Bild) | `SDXL-Turbo` (oder ein beliebiges Modell in der Kategorie **Image**) | Beliebiges Stable-Diffusion-Modell, das Bilder zu einer Texteingabe generiert |
| Audio (Sprache → Text) | `Whisper-Large-v3` (oder ein beliebiges Modell in der Kategorie **Audio**) | Beliebiges ASR-Modell, das Audio in Text umwandelt |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Verwendete Ports

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Falls diese Ports auf Ihrem System bereits verwendet werden, ändern Sie diese beim Starten des/der Servers.