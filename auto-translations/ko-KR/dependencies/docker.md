<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
[Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)를 설치하고 실행하세요. 엔진이 실행 중인지 확인합니다:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
[Docker Engine](https://docs.docker.com/engine/install/ubuntu/)을 설치한 다음, `sudo` 없이 `docker`를 실행할 수 있도록 사용자를 `docker` 그룹에 추가하세요(이후 로그아웃했다가 다시 로그인해야 합니다). 엔진이 실행 중인지 확인합니다:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->