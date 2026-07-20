<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman is containerisatiesoftware voor Linux.


**Stap 1**: Installeer de kern-Podman-engine en de standalone Compose V2-parsingplugin.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Stap 2**: Controleer Podman en Compose

```bash
podman --version
podman-compose --version
```

**Stap 3**: Schakel de systeemwijde Podman API-socket in zodat de Compose-plugin kan communiceren met de containerruntime.

```bash
sudo systemctl enable --now podman.socket
```
**Stap 4**: Voer een tijdelijke testcontainer uit om te controleren of de engine images succesvol kan ophalen en uitvoeren.

```bash
sudo podman run --rm docker.io/library/hello-world
```