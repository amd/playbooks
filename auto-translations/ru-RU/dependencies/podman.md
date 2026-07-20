<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman — это программное обеспечение для контейнеризации для Linux.


**Шаг 1**: Установите основной движок Podman и отдельный плагин для парсинга Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Шаг 2**: Проверьте Podman и Compose

```bash
podman --version
podman-compose --version
```

**Шаг 3**: Включите общесистемный сокет API Podman, чтобы плагин Compose мог взаимодействовать с средой выполнения контейнеров.

```bash
sudo systemctl enable --now podman.socket
```
**Шаг 4**: Запустите временный тестовый контейнер, чтобы убедиться, что движок может успешно загружать и запускать образы.

```bash
sudo podman run --rm docker.io/library/hello-world
```