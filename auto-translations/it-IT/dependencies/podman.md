<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman è un software di containerizzazione per Linux.


**Passaggio 1**: installa il motore Podman principale e il plugin standalone per il parsing di Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Passaggio 2**: verifica Podman e Compose

```bash
podman --version
podman-compose --version
```

**Passaggio 3**: abilita il socket API di Podman a livello di sistema in modo che il plugin Compose possa comunicare con il runtime dei container.

```bash
sudo systemctl enable --now podman.socket
```
**Passaggio 4**: esegui un container di test temporaneo per verificare che il motore riesca a scaricare ed eseguire correttamente le immagini.

```bash
sudo podman run --rm docker.io/library/hello-world
```