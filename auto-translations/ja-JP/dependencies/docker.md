<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
[Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) をインストールして起動してください。エンジンが動作していることを確認します:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
[Docker Engine](https://docs.docker.com/engine/install/ubuntu/) をインストールし、ユーザーを `docker` グループに追加して `sudo` なしで `docker` を実行できるようにしてください(その後、一度ログアウトして再度ログインしてください)。エンジンが動作していることを確認します:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->