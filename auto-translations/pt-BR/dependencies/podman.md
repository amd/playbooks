<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman é um software de containerização para Linux.


**Passo 1**: Instale o motor principal do Podman e o plugin de análise Compose V2 independente.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Passo 2**: Verifique o Podman e o Compose

```bash
podman --version
podman-compose --version
```

**Passo 3**: Habilite o socket da API do Podman em todo o sistema para que o plugin Compose possa se comunicar com o runtime de container.

```bash
sudo systemctl enable --now podman.socket
```
**Passo 4**: Execute um container de teste temporário para verificar se o motor consegue extrair e executar imagens com sucesso.

```bash
sudo podman run --rm docker.io/library/hello-world
```