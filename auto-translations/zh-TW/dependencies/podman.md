<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman 是適用於 Linux 的容器化軟體。


**步驟 1**：安裝核心 Podman 引擎與獨立的 Compose V2 解析外掛程式。

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**步驟 2**：驗證 Podman 與 Compose

```bash
podman --version
podman-compose --version
```

**步驟 3**：啟用系統層級的 Podman API socket，讓 Compose 外掛程式能夠與容器執行環境通訊。

```bash
sudo systemctl enable --now podman.socket
```
**步驟 4**：執行一個暫時的測試容器，以驗證引擎能否成功提取並執行映像檔。

```bash
sudo podman run --rm docker.io/library/hello-world
```