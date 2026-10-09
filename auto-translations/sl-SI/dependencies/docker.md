<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Namestite [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) in ga zaženite. Preverite, da njegov pogon deluje:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Namestite [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), nato dodajte svojega uporabnika v skupino `docker`, da `docker` deluje brez `sudo` (po tem se odjavite in ponovno prijavite). Preverite, da pogon deluje:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->