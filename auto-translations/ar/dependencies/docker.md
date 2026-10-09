<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
ثبّت [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) وشغّله. تحقق من أن محركه يعمل:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
ثبّت [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)، ثم أضف مستخدمك إلى مجموعة `docker` حتى يعمل أمر `docker` بدون الحاجة إلى `sudo` (سجّل الخروج ثم الدخول مجددًا بعد ذلك). تحقق من أن المحرك يعمل:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->