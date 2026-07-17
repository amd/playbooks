<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman er containeriseringsprogramvare for Linux.


**Steg 1**: Installer den sentrale Podman-motoren og den frittstående Compose V2-tolkeplugin.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Steg 2**: Verifiser Podman og Compose

```bash
podman --version
podman-compose --version
```

**Steg 3**: Aktiver den systemomfattende Podman API-socketen slik at Compose-pluginen kan kommunisere med container-kjøretidsmiljøet.

```bash
sudo systemctl enable --now podman.socket
```
**Steg 4**: Kjør en midlertidig testcontainer for å verifisere at motoren kan hente og kjøre images.

```bash
sudo podman run --rm docker.io/library/hello-world
```