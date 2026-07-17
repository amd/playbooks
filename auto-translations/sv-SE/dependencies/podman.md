<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman är programvara för containerisering i Linux.


**Steg 1**: Installera Podman-kärnan och det fristående Compose V2-tolkningsplugin.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Steg 2**: Verifiera Podman och Compose

```bash
podman --version
podman-compose --version
```

**Steg 3**: Aktivera den systemövergripande Podman API-socketen så att Compose-pluginet kan kommunicera med container-runtimen.

```bash
sudo systemctl enable --now podman.socket
```
**Steg 4**: Kör en tillfällig testcontainer för att verifiera att motorn kan hämta och köra images.

```bash
sudo podman run --rm docker.io/library/hello-world
```