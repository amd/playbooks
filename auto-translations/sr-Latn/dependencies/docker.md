<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Instalirajte [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) i pokrenite ga. Proverite da li je njegov engine pokrenut:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Instalirajte [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), a zatim dodajte svog korisnika u grupu `docker` kako bi `docker` radio bez `sudo` (nakon toga se odjavite i ponovo prijavite). Proverite da li je engine pokrenut:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->