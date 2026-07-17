<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je softvér na kontajnerizáciu pre Linux.


**Krok 1**: Nainštalujte jadro Podman engine a samostatný plugin Compose V2 na spracovanie.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Krok 2**: Overte Podman a Compose

```bash
podman --version
podman-compose --version
```

**Krok 3**: Povoľte systémový soket Podman API, aby mohol plugin Compose komunikovať s behom kontajnerov.

```bash
sudo systemctl enable --now podman.socket
```
**Krok 4**: Spustite dočasný testovací kontajner na overenie, že engine dokáže úspešne stiahnuť a spustiť obrazy.

```bash
sudo podman run --rm docker.io/library/hello-world
```