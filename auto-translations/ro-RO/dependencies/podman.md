<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman este un software de containerizare pentru Linux.


**Pasul 1**: Instalați motorul de bază Podman și pluginul standalone de parsare Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Pasul 2**: Verificați Podman și Compose

```bash
podman --version
podman-compose --version
```

**Pasul 3**: Activați socket-ul API Podman la nivel de sistem, astfel încât pluginul Compose să poată comunica cu runtime-ul de containere.

```bash
sudo systemctl enable --now podman.socket
```
**Pasul 4**: Rulați un container de test temporar pentru a verifica că motorul poate extrage și executa imagini cu succes.

```bash
sudo podman run --rm docker.io/library/hello-world
```