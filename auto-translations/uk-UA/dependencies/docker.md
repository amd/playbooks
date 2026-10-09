<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Встановіть [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) і запустіть його. Перевірте, що його рушій запущено:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Встановіть [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), потім додайте свого користувача до групи `docker`, щоб `docker` працював без `sudo` (після цього вийдіть із системи та увійдіть знову). Перевірте, що рушій запущено:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->