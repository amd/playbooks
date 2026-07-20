<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman este un software de containerizare pentru Linux.


**Pasul 1**: Instalați motorul de bază Podman și pluginul independent de parsare Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Pasul 2**: Verificați Podman și Compose

```bash
podman --version
podman-compose --version
```

**Pasul 3**: Activați soclul API Podman la nivel de sistem pentru ca pluginul Compose să poată comunica cu mediul de execuție al containerelor.

```bash
sudo systemctl enable --now podman.socket
```
**Pasul 4**: Rulați un container de test temporar pentru a verifica dacă motorul poate extrage și executa cu succes imagini.

```bash
sudo podman run --rm docker.io/library/hello-world
```