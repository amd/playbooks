<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman è un software di containerizzazione per Linux.

**Passaggio 1**: Installa il motore Podman principale e il plugin di parsing Compose V2 standalone.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Passaggio 2**: Verifica Podman e Compose

```bash
podman --version
podman-compose --version
```

**Passaggio 3**: Abilita il socket API Podman a livello di sistema in modo che il plugin Compose possa comunicare con il runtime dei container.

```bash
sudo systemctl enable --now podman.socket
```
**Passaggio 4**: Esegui un container di test temporaneo per verificare che il motore possa estrarre ed eseguire immagini correttamente.

```bash
sudo podman run --rm docker.io/library/hello-world
```