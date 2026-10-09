<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installa [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) e avvialo. Verifica che il suo motore sia in esecuzione:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installa [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), quindi aggiungi il tuo utente al gruppo `docker` in modo che `docker` funzioni senza `sudo` (effettua il logout e poi il login di nuovo). Verifica che il motore sia in esecuzione:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->