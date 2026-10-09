<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Instale o [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) e inicie-o. Verifique se o mecanismo (engine) está em execução:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Instale o [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) e, em seguida, adicione seu usuário ao grupo `docker` para que o `docker` seja executado sem `sudo` (faça logout e login novamente depois). Verifique se o mecanismo está em execução:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->