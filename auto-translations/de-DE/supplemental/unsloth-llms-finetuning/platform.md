<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Voraussetzungen

PyTorch mit ROCm-Unterstützung ist auf der AMD Ryzen™ AI Halo Developer Platform vorinstalliert. Für alle anderen Geräte müssen Benutzer PyTorch mit ROCm-Unterstützung manuell installieren. Bitte beachten Sie den entsprechenden Abschnitt für Ihr Betriebssystem:


### Windows

| Komponente     | Version         | Hinweise                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Vorinstalliert auf der AMD Ryzen AI Halo Developer Platform; muss auf allen anderen Geräten manuell installiert werden |


### Linux

| Komponente     | Version         | Hinweise                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Vorinstalliert auf der AMD Ryzen AI Halo Developer Platform; muss auf allen anderen Geräten manuell installiert werden |


## Erforderliche Modelle

Die folgenden Modelle sind für Ihre Plattform getestet und optimiert:

| Modell | Parameter | Größe | Download-Ort |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Download von HF

Modelle werden automatisch in das Hugging Face-Cache-Verzeichnis heruntergeladen: `~/.cache/huggingface/hub/`

Stellen Sie sicher, dass mindestens **20 GB freier Speicherplatz** für die Modellspeicherung vorhanden ist.

## Netzwerkanforderungen

Die Ersteinrichtung erfordert Internetzugang, um Modelle von Hugging Face herunterzuladen. Nach dem Download kann das Playbook offline ausgeführt werden.

- Der erstmalige Modell-Download kann je nach Modellgröße und Verbindungsgeschwindigkeit **5–10 Minuten** dauern
- Modelle werden lokal zwischengespeichert und müssen nicht erneut heruntergeladen werden