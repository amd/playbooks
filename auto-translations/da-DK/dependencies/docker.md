<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installer [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) og start det. Kontrollér, at dets engine kører:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installer [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), og tilføj derefter din bruger til gruppen `docker`, så `docker` kan køres uden `sudo` (log ud og ind igen bagefter). Kontrollér, at engine'en kører:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->