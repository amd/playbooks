<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Nainstalujte [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) a spusťte jej. Zkontrolujte, že jeho engine běží:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Nainstalujte [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) a poté přidejte svého uživatele do skupiny `docker`, aby `docker` fungoval bez `sudo` (poté se odhlaste a znovu přihlaste). Zkontrolujte, že engine běží:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->