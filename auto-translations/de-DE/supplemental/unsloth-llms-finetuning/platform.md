# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Voraussetzungen

PyTorch mit ROCm-Unterstützung ist auf der AMD Ryzen™ AI Halo Developer Platform vorinstalliert. Für alle anderen Geräte müssen Benutzer PyTorch mit ROCm-Unterstützung manuell installieren. Bitte beachten Sie den entsprechenden Abschnitt für Ihr Betriebssystem:


### Windows

| Komponente    | Version         | Hinweise                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Auf der AMD Ryzen AI Halo Developer Platform vorinstalliert; muss auf allen anderen Geräten manuell installiert werden |


### Linux

| Komponente    | Version         | Hinweise                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Auf der AMD Ryzen AI Halo Developer Platform vorinstalliert; muss auf allen anderen Geräten manuell installiert werden |


## Erforderliche Modelle

Die folgenden Modelle wurden getestet und für Ihre Plattform optimiert:

| Modell | Parameter | Größe | Download-Speicherort |
|--------|-----------|-------|----------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Von HF herunterladen

Modelle werden automatisch in das Hugging Face-Cache-Verzeichnis heruntergeladen: `~/.cache/huggingface/hub/`

Stellen Sie sicher, dass mindestens **20 GB freier Speicherplatz** für die Modellspeicherung vorhanden ist.

## Netzwerkanforderungen

Die Ersteinrichtung erfordert einen Internetzugang, um Modelle von Hugging Face herunterzuladen. Nach dem Download kann das Playbook offline ausgeführt werden.

- Erstmalige Modell-Downloads können je nach Modellgröße und Verbindungsgeschwindigkeit **5–10 Minuten** dauern
- Modelle werden lokal zwischengespeichert und müssen nicht erneut heruntergeladen werden