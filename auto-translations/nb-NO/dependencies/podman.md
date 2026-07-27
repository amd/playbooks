<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman er containeriseringsprogramvare for Linux.


**Trinn 1**: Installer selve Podman-motoren og det frittstående Compose V2-analyseringstillegget.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Trinn 2**: Bekreft Podman og Compose

```bash
podman --version
podman-compose --version
```

**Trinn 3**: Aktiver den systemomfattende Podman API-socketen slik at Compose-tillegget kan kommunisere med kjøretidsmiljøet for containere.

```bash
sudo systemctl enable --now podman.socket
```
**Trinn 4**: Kjør en midlertidig testcontainer for å bekrefte at motoren kan hente og kjøre images.

```bash
sudo podman run --rm docker.io/library/hello-world
```