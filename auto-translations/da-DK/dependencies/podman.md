<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman er containeriseringssoftware til Linux.


**Trin 1**: Installer kernemotoren Podman og standalone-plugin'et Compose V2 til parsing.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Trin 2**: Bekræft Podman og Compose

```bash
podman --version
podman-compose --version
```

**Trin 3**: Aktivér det systemdækkende Podman API-socket, så Compose-plugin'et kan kommunikere med container-runtime.

```bash
sudo systemctl enable --now podman.socket
```
**Trin 4**: Kør en midlertidig testcontainer for at bekræfte, at motoren kan hente og køre images med succes.

```bash
sudo podman run --rm docker.io/library/hello-world
```