<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installation von Lemonade

<!-- @os:windows -->
Laden Sie das neueste Installationsprogramm von [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) herunter und führen Sie die `.msi`-Datei aus.

Nach der Installation:
- Die `lemonade`-CLI wird automatisch zu Ihrem System-PATH hinzugefügt
- Der Lemonade-Server wird erwartungsgemäß automatisch im Hintergrund ausgeführt

Sie können die Installation auch stillschweigend über die Befehlszeile durchführen:
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

Informationen zu anderen Distributionen oder zur Installation aus dem Quellcode finden Sie unter [vollständige Installationsoptionen](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Überprüfen der Lemonade-Installation

Öffnen Sie ein Terminal und führen Sie Folgendes aus:
```bash
lemonade --version
```

Sie sollten eine Ausgabe wie diese sehen:
```
lemonade version x.y.z
```

Wenn eine Versionsnummer angezeigt wird, ist Lemonade korrekt installiert und einsatzbereit.

Zur schnellen Referenz finden Sie hier gängige Lemonade-CLI-Befehle:

| Befehl | Was er bewirkt |
| --- | --- |
| `lemonade --help` | Zeigt alle verfügbaren Befehle und Flags an. |
| `lemonade --version` | Gibt die installierte Lemonade-Version aus. |
| `lemonade status` | Bestätigt, ob der Lemonade-Server läuft und erreichbar ist. Die standardmäßige OpenAI-kompatible API-Basis-URL ist `http://localhost:13305/api/v1`. |
| `lemonade list` | Listet die für Ihre Lemonade-Einrichtung verfügbaren Modelle auf. |
| `lemonade pull <MODEL_NAME>` | Lädt ein Modell herunter, ohne es zu starten. |
| `lemonade run <MODEL_NAME>` | Lädt das Modell bei Bedarf herunter und startet es anschließend für Inferenz/Chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Startet ein llama.cpp-Modell mit dem ROCm-Backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Startet ein llama.cpp-Modell mit dem Vulkan-Backend. |
| `lemonade config` | Zeigt die aktuellen Lemonade-Konfigurationswerte an. |
| `lemonade config set llamacpp.backend=rocm` | Legt ROCm als Standard-Backend für llama.cpp fest. |

Die neuesten Optionen für den Lemonade-Server oder Hinweise zur Fehlerbehebung finden Sie in der [offiziellen Lemonade-Dokumentation](https://lemonade-server.ai/docs/lemonade-cli/).