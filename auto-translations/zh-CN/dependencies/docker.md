<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
安装 [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) 并启动它。检查其引擎是否正在运行：

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
安装 [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)，然后将您的用户添加到 `docker` 组，使 `docker` 无需 `sudo` 即可运行（之后请注销并重新登录）。检查引擎是否正在运行：

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->