<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installer [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) og start det. Sjekk at motoren kjører:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installer [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), og legg deretter til brukeren din i `docker`-gruppen slik at `docker` kjører uten `sudo` (logg ut og inn igjen etterpå). Sjekk at motoren kjører:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->