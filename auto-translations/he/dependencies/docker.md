<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
התקינו את [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) והפעילו אותו. ודאו שהמנוע שלו פועל:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
התקינו את [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), ולאחר מכן הוסיפו את המשתמש שלכם לקבוצת `docker` כדי ש-`docker` יפעל ללא `sudo` (התנתקו והתחברו מחדש לאחר מכן). ודאו שהמנוע פועל:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->