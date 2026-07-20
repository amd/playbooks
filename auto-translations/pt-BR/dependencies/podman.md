<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman é um software de containerização para Linux.

**Etapa 1**: Instale o mecanismo principal do Podman e o plugin autônomo de análise do Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Etapa 2**: Verifique o Podman e o Compose

```bash
podman --version
podman-compose --version
```

**Etapa 3**: Habilite o soquete da API do Podman em nível de sistema para que o plugin Compose possa se comunicar com o runtime de contêiner.

```bash
sudo systemctl enable --now podman.socket
```
**Etapa 4**: Execute um contêiner de teste temporário para verificar se o mecanismo consegue baixar e executar imagens com sucesso.

```bash
sudo podman run --rm docker.io/library/hello-world
```