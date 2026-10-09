<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installera [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) och starta det. Kontrollera att dess motor körs:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installera [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), lägg sedan till din användare i gruppen `docker` så att `docker` kan köras utan `sudo` (logga ut och in igen efteråt). Kontrollera att motorn körs:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->