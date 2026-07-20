<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je softvér na kontajnerizáciu pre Linux.


**Krok 1**: Nainštalujte jadro enginu Podman a samostatný doplnok na parsovanie Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Krok 2**: Overte Podman a Compose

```bash
podman --version
podman-compose --version
```

**Krok 3**: Povoľte systémový soket API pre Podman, aby doplnok Compose mohol komunikovať s runtime kontajnerov.

```bash
sudo systemctl enable --now podman.socket
```
**Krok 4**: Spustite dočasný testovací kontajner, aby ste overili, že engine dokáže úspešne stiahnuť a spustiť obrazy.

```bash
sudo podman run --rm docker.io/library/hello-world
```