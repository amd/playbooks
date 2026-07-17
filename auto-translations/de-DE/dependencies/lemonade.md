<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade installieren

<!-- @os:windows -->
Laden Sie den neuesten Installer von [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) herunter und führen Sie die `.msi`-Datei aus.

Nach der Installation:
- Die `lemonade` CLI wird automatisch zu Ihrem System-PATH hinzugefügt
- Der Lemonade-Server wird erwartet, automatisch im Hintergrund zu laufen

Sie können auch lautlos über die Befehlszeile installieren:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Für andere Distributionen oder zur Installation aus dem Quellcode, siehe die [vollständigen Installationsoptionen](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Lemonade-Installation überprüfen

Öffnen Sie ein Terminal und führen Sie aus:
```bash
lemonade --version
```

Sie sollten eine Ausgabe wie diese sehen:
```
lemonade version x.y.z
```

Wenn Sie eine Versionsnummer sehen, ist Lemonade korrekt installiert und einsatzbereit.

Zur schnellen Orientierung finden Sie hier häufig verwendete Lemonade CLI-Befehle:

| Befehl | Was er bewirkt |
| --- | --- |
| `lemonade --help` | Zeigt alle verfügbaren Befehle und Flags an. |
| `lemonade --version` | Gibt die installierte Lemonade-Version aus. |
| `lemonade status` | Bestätigt, ob der Lemonade-Server läuft und erreichbar ist. Die Standard-OpenAI-kompatible API-Basis-URL lautet `http://localhost:13305/api/v1`. |
| `lemonade list` | Listet die für Ihr Lemonade-Setup verfügbaren Modelle auf. |
| `lemonade pull <MODEL_NAME>` | Lädt ein Modell herunter, ohne es zu starten. |
| `lemonade run <MODEL_NAME>` | Lädt das Modell bei Bedarf herunter und startet es dann für Inferenz/Chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Startet ein llama.cpp-Modell mit dem ROCm-Backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Startet ein llama.cpp-Modell mit dem Vulkan-Backend. |
| `lemonade config` | Zeigt die aktuellen Lemonade-Konfigurationswerte an. |
| `lemonade config set llamacpp.backend=rocm` | Setzt das Standard-llama.cpp-Backend auf ROCm. |

Für die neuesten Lemonade-Serveroptionen oder zur Fehlerbehebung lesen Sie bitte die [offizielle Lemonade-Dokumentation](https://lemonade-server.ai/docs/lemonade-cli/).