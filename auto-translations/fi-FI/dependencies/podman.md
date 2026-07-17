<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman on Linux-käyttöjärjestelmän kontainerointiohjelmisto.


**Vaihe 1**: Asenna Podman-ydinmoottori ja erillinen Compose V2 -jäsennysliitännäinen.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Vaihe 2**: Tarkista Podman ja Compose

```bash
podman --version
podman-compose --version
```

**Vaihe 3**: Ota käyttöön järjestelmänlaajuinen Podman API -pistorasia, jotta Compose-liitännäinen voi kommunikoida konttisuoritusympäristön kanssa.

```bash
sudo systemctl enable --now podman.socket
```
**Vaihe 4**: Käynnistä väliaikainen testikontaineri varmistaaksesi, että moottori pystyy onnistuneesti hakemaan ja suorittamaan kuvia.

```bash
sudo podman run --rm docker.io/library/hello-world
```