<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman er containeriseringssoftware til Linux.


**Trin 1**: Installer den centrale Podman-motor og det selvstændige Compose V2-fortolkningsplugin.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Trin 2**: Verificer Podman og Compose

```bash
podman --version
podman-compose --version
```

**Trin 3**: Aktiver den systemdækkende Podman API-socket, så Compose-pluginnet kan kommunikere med container-runtimen.

```bash
sudo systemctl enable --now podman.socket
```
**Trin 4**: Kør en midlertidig testcontainer for at verificere, at motoren kan hente og udføre images.

```bash
sudo podman run --rm docker.io/library/hello-world
```