<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Voraussetzungen

PyTorch mit ROCm-Unterstützung ist auf der AMD Ryzen™ AI Halo Developer Platform vorinstalliert. Für alle anderen Geräte müssen Benutzer PyTorch mit ROCm-Unterstützung manuell installieren. Bitte beachten Sie den entsprechenden Abschnitt für Ihr Betriebssystem:

### Windows

| Komponente    | Version         | Hinweise                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 oder neuer  | Auf der AMD Ryzen AI Halo Developer Platform vorinstalliert; muss auf allen anderen Geräten manuell installiert werden |

### Linux

| Komponente    | Version         | Hinweise                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 oder neuer  | Auf der AMD Ryzen AI Halo Developer Platform vorinstalliert; muss auf allen anderen Geräten manuell installiert werden |

## Erforderliche Modelle

Die folgenden Modelle wurden getestet und für Ihre Plattform optimiert:

| Modell | Parameter | Größe | Download-Speicherort |
|--------|-----------|-------|----------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Auf der AMD Ryzen AI Halo Developer Platform vorinstalliert; muss auf allen anderen Geräten manuell installiert werden |

Modelle werden automatisch in das Hugging Face-Cache-Verzeichnis heruntergeladen:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Stellen Sie sicher, dass mindestens **50 GB freier Speicherplatz** für die Modellspeicherung vorhanden ist.

## Netzwerkanforderungen

Für die Ersteinrichtung ist ein Internetzugang erforderlich, um Modelle von Hugging Face herunterzuladen. Nach dem Download kann das Playbook offline ausgeführt werden.

- Erstmalige Modell-Downloads können je nach Modellgröße und Verbindungsgeschwindigkeit **5–10 Minuten** dauern
- Modelle werden lokal zwischengespeichert und müssen nicht erneut heruntergeladen werden