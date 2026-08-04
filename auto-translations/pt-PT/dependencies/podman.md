<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

O Podman é um software de containerização para Linux.


**Passo 1**: Instale o motor Podman principal e o plugin autónomo de análise Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Passo 2**: Verifique o Podman e o Compose

```bash
podman --version
podman-compose --version
```

**Passo 3**: Ative o socket da API Podman a nível do sistema para que o plugin Compose possa comunicar com o runtime de contentores.

```bash
sudo systemctl enable --now podman.socket
```
**Passo 4**: Execute um contentor de teste temporário para verificar se o motor consegue obter e executar imagens com sucesso.

```bash
sudo podman run --rm docker.io/library/hello-world
```