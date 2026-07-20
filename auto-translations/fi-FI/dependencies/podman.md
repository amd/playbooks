<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman on Linux-käyttöjärjestelmille tarkoitettu konttiohjelmisto.


**Vaihe 1**: Asenna Podman-ydinmoottori ja erillinen Compose V2 -jäsennyslaajennus.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Vaihe 2**: Tarkista Podman ja Compose

```bash
podman --version
podman-compose --version
```

**Vaihe 3**: Ota käyttöön koko järjestelmän laajuinen Podman API -pistoke, jotta Compose-laajennus voi kommunikoida konttiajoympäristön kanssa.

```bash
sudo systemctl enable --now podman.socket
```
**Vaihe 4**: Suorita väliaikainen testikontti varmistaaksesi, että moottori pystyy noutamaan ja suorittamaan levykuvia onnistuneesti.

```bash
sudo podman run --rm docker.io/library/hello-world
```