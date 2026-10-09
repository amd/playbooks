<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Telepítsd a [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) alkalmazást, és indítsd el. Ellenőrizd, hogy a motorja fut-e:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Telepítsd a [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) szolgáltatást, majd add hozzá a felhasználódat a `docker` csoporthoz, hogy a `docker` `sudo` nélkül is futtatható legyen (ezután jelentkezz ki, majd vissza). Ellenőrizd, hogy a motor fut-e:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->