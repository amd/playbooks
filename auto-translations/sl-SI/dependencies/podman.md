<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je programska oprema za vsebniško virtualizacijo za Linux.

**1. korak**: Namestite jedro pogona Podman in samostojni vtičnik za razčlenjevanje Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**2. korak**: Preverite Podman in Compose

```bash
podman --version
podman-compose --version
```

**3. korak**: Omogočite sistemsko vtičnico Podman API, da bo vtičnik Compose lahko komuniciral z izvajalnim okoljem vsebnikov.

```bash
sudo systemctl enable --now podman.socket
```
**4. korak**: Zaženite začasni testni vsebnik, da preverite, ali pogon lahko uspešno prenese in izvede slike.

```bash
sudo podman run --rm docker.io/library/hello-world
```