<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Nainštalujte [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) a spustite ho. Skontrolujte, či beží jeho engine:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Nainštalujte [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) a potom pridajte svojho používateľa do skupiny `docker`, aby `docker` fungoval bez `sudo` (následne sa odhláste a znova prihláste). Skontrolujte, či engine beží:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->