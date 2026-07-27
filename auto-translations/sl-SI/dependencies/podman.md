<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman je programska oprema za kontejnerizacijo za Linux.


**Korak 1**: Namestite osnovni pogon Podman in samostojni vtičnik za razčlenjevanje Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Korak 2**: Preverite Podman in Compose

```bash
podman --version
podman-compose --version
```

**Korak 3**: Omogočite sistemsko vtičnico API Podman, da lahko vtičnik Compose komunicira z izvajalnim okoljem vsebnikov.

```bash
sudo systemctl enable --now podman.socket
```
**Korak 4**: Zaženite začasni testni vsebnik, da preverite, ali lahko pogon uspešno prenese in izvede slike.

```bash
sudo podman run --rm docker.io/library/hello-world
```