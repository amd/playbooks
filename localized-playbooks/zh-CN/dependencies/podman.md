<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman 是面向 Linux 的容器化软件。


**步骤 1**：安装 Podman 核心引擎以及独立的 Compose V2 解析插件。

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**步骤 2**：验证 Podman 和 Compose

```bash
podman --version
podman-compose --version
```

**步骤 3**：启用系统级 Podman API socket，使 Compose 插件能够与容器运行时通信。

```bash
sudo systemctl enable --now podman.socket
```
**步骤 4**：运行一个临时测试容器，验证引擎可以成功拉取并执行镜像。

```bash
sudo podman run --rm docker.io/library/hello-world
```
