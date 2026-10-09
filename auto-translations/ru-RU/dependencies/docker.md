<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Установите [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) и запустите его. Убедитесь, что его движок работает:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Установите [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), затем добавьте своего пользователя в группу `docker`, чтобы `docker` запускался без `sudo` (после этого выйдите из системы и войдите снова). Убедитесь, что движок работает:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->