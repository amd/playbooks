<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Instale o [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) e inicie-o. Verifique se o motor está em execução:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Instale o [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) e, em seguida, adicione o seu utilizador ao grupo `docker` para que o `docker` seja executado sem `sudo` (termine a sessão e inicie-a novamente depois). Verifique se o motor está em execução:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->