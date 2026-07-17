<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman ist eine Containerisierungssoftware für Linux.


**Schritt 1**: Installieren Sie die Podman-Kern-Engine und das eigenständige Compose V2-Parsing-Plugin.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Schritt 2**: Podman und Compose überprüfen

```bash
podman --version
podman-compose --version
```

**Schritt 3**: Aktivieren Sie den systemweiten Podman-API-Socket, damit das Compose-Plugin mit der Container-Laufzeitumgebung kommunizieren kann.

```bash
sudo systemctl enable --now podman.socket
```
**Schritt 4**: Führen Sie einen temporären Testcontainer aus, um zu überprüfen, ob die Engine Images erfolgreich abrufen und ausführen kann.

```bash
sudo podman run --rm docker.io/library/hello-world
```