<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installeer [Docker Desktop voor Windows](https://docs.docker.com/desktop/setup/install/windows-install/) en start het. Controleer of de engine actief is:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installeer [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) en voeg vervolgens je gebruiker toe aan de `docker`-groep, zodat `docker` kan worden uitgevoerd zonder `sudo` (log daarna uit en weer in). Controleer of de engine actief is:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->