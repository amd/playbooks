<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je kontejnerizační software pro Linux.

**Krok 1**: Nainstalujte základní jádro Podman a samostatný doplněk pro parsování Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Krok 2**: Ověřte Podman a Compose

```bash
podman --version
podman-compose --version
```

**Krok 3**: Povolte celosystémový soket API Podman, aby doplněk Compose mohl komunikovat s kontejnerovým runtime.

```bash
sudo systemctl enable --now podman.socket
```
**Krok 4**: Spusťte dočasný testovací kontejner a ověřte, že engine dokáže úspěšně stáhnout a spustit image.

```bash
sudo podman run --rm docker.io/library/hello-world
```