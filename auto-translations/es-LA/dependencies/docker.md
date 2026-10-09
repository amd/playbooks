<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Instala [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) e inícialo. Verifica que su motor esté en ejecución:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Instala [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) y luego agrega tu usuario al grupo `docker` para que `docker` se ejecute sin `sudo` (cierra sesión y vuelve a iniciarla después). Verifica que el motor esté en ejecución:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->