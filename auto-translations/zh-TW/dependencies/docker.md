<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
安裝 [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) 並啟動它。確認其引擎正在執行：

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
安裝 [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)，然後將您的使用者加入 `docker` 群組，讓 `docker` 不需使用 `sudo` 即可執行（完成後請登出再重新登入）。確認引擎正在執行：

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->