<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je softver za kontejnerizaciju za Linux.


**Korak 1**: Instalirajte osnovni Podman mehanizam (engine) i samostalni Compose V2 dodatak za parsiranje.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Korak 2**: Proverite Podman i Compose

```bash
podman --version
podman-compose --version
```

**Korak 3**: Omogućite sistemski Podman API soket kako bi Compose dodatak mogao da komunicira sa kontejnerskim okruženjem za izvršavanje.

```bash
sudo systemctl enable --now podman.socket
```
**Korak 4**: Pokrenite privremeni testni kontejner da biste proverili da li mehanizam može uspešno da preuzme i izvrši slike.

```bash
sudo podman run --rm docker.io/library/hello-world
```