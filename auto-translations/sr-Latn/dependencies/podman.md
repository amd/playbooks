<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je softver za kontejnerizaciju za Linux.


**Korak 1**: Instalirajte osnovni Podman engine i samostalni Compose V2 plugin za parsiranje.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Korak 2**: Verifikujte Podman i Compose

```bash
podman --version
podman-compose --version
```

**Korak 3**: Omogućite sistemski Podman API socket kako bi Compose plugin mogao da komunicira sa runtime-om kontejnera.

```bash
sudo systemctl enable --now podman.socket
```
**Korak 4**: Pokrenite privremeni test kontejner da biste verifikovali da engine može uspešno da preuzme i izvrši slike.

```bash
sudo podman run --rm docker.io/library/hello-world
```