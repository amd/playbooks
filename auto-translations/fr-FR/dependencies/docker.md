<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Installez [Docker Desktop pour Windows](https://docs.docker.com/desktop/setup/install/windows-install/) et démarrez-le. Vérifiez que son moteur fonctionne :

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Installez [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), puis ajoutez votre utilisateur au groupe `docker` afin que `docker` s'exécute sans `sudo` (déconnectez-vous puis reconnectez-vous ensuite). Vérifiez que le moteur fonctionne :

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->