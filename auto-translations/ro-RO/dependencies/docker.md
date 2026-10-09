<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Instalați [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) și porniți-l. Verificați că motorul său rulează:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Instalați [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), apoi adăugați utilizatorul dvs. în grupul `docker` pentru ca `docker` să ruleze fără `sudo` (deconectați-vă și reconectați-vă ulterior). Verificați că motorul rulează:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->