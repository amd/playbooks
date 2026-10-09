<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Zainstaluj [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) i uruchom go. Sprawdź, czy jego silnik działa:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Zainstaluj [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), a następnie dodaj swojego użytkownika do grupy `docker`, aby `docker` działał bez `sudo` (następnie wyloguj się i zaloguj ponownie). Sprawdź, czy silnik działa:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->