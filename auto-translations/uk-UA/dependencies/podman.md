<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman — це програмне забезпечення для контейнеризації в Linux.


**Крок 1**: Встановіть основний рушій Podman та окремий плагін для аналізу Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Крок 2**: Перевірте Podman і Compose

```bash
podman --version
podman-compose --version
```

**Крок 3**: Увімкніть загальносистемний сокет API Podman, щоб плагін Compose міг взаємодіяти зі середовищем виконання контейнерів.

```bash
sudo systemctl enable --now podman.socket
```
**Крок 4**: Запустіть тимчасовий тестовий контейнер, щоб перевірити, чи рушій може успішно завантажувати та виконувати образи.

```bash
sudo podman run --rm docker.io/library/hello-world
```