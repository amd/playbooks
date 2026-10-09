<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
[Windows için Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) uygulamasını yükleyin ve başlatın. Motorunun çalıştığını kontrol edin:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
[Docker Engine](https://docs.docker.com/engine/install/ubuntu/) uygulamasını yükleyin, ardından kullanıcınızı `docker` grubuna ekleyerek `docker` komutunun `sudo` olmadan çalışmasını sağlayın (ardından oturumu kapatıp tekrar açın). Motorun çalıştığını kontrol edin:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->