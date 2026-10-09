<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Asenna [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) ja käynnistä se. Tarkista, että sen moottori on käynnissä:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Asenna [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) ja lisää sitten käyttäjäsi `docker`-ryhmään, jotta `docker` toimii ilman `sudo`-komentoa (kirjaudu ulos ja takaisin sisään tämän jälkeen). Tarkista, että moottori on käynnissä:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->