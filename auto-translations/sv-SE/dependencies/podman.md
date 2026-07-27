<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman är containeriseringsmjukvara för Linux.


**Steg 1**: Installera huvudmotorn för Podman och det fristående tillägget för Compose V2-tolkning.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Steg 2**: Verifiera Podman och Compose

```bash
podman --version
podman-compose --version
```

**Steg 3**: Aktivera det systemomfattande API-uttaget för Podman så att Compose-tillägget kan kommunicera med containerkörningsmiljön.

```bash
sudo systemctl enable --now podman.socket
```
**Steg 4**: Kör en tillfällig testcontainer för att verifiera att motorn kan hämta och köra images korrekt.

```bash
sudo podman run --rm docker.io/library/hello-world
```