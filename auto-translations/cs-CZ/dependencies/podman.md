<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je software pro kontejnerizaci pro Linux.


**Krok 1**: Nainstalujte základní engine Podman a samostatný plugin pro parsování Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Krok 2**: Ověřte Podman a Compose

```bash
podman --version
podman-compose --version
```

**Krok 3**: Povolte systémový socket Podman API, aby plugin Compose mohl komunikovat s runtime kontejnerů.

```bash
sudo systemctl enable --now podman.socket
```
**Krok 4**: Spusťte dočasný testovací kontejner pro ověření, že engine dokáže úspěšně stáhnout a spustit obrazy.

```bash
sudo podman run --rm docker.io/library/hello-world
```