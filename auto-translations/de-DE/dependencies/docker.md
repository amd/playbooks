<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installieren Sie [Docker Desktop für Windows](https://docs.docker.com/desktop/setup/install/windows-install/) und starten Sie es. Überprüfen Sie, ob die Engine läuft:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installieren Sie [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) und fügen Sie Ihren Benutzer dann zur Gruppe `docker` hinzu, damit `docker` ohne `sudo` ausgeführt werden kann (melden Sie sich anschließend ab und wieder an). Überprüfen Sie, ob die Engine läuft:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->