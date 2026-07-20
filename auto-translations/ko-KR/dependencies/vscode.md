<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
VS Code는 **AMD Ryzen™ AI Developer Center**에서 설치할 수 있습니다. **Updates** 탭으로 이동하여 VS Code가 아직 설치되어 있지 않다면 설치하십시오.
<!-- @os:end -->

<!-- @os:linux -->
VS Code는 **AMD Ryzen™ AI Developer Center**에서 설치할 수 있습니다. **Manage** 탭으로 이동하여 VS Code가 아직 설치되어 있지 않다면 설치하십시오.
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. 다음 위치에서 Windows 설치 실행 파일을 다운로드합니다: https://update.code.visualstudio.com/1.108.2/win32-x64-user/stable.
2. 다운로드한 파일 `VSCodeUserSetup-x64-1.108.2.exe`을 클릭하여 VS Code를 설치합니다.

<!-- @os:end -->

<!-- @os:linux -->

1. 다음 위치에서 Debian 설치 패키지를 다운로드합니다: https://update.code.visualstudio.com/1.108.2/linux-deb-x64/stable.
2. 다운로드한 파일 `code_1.108.2-1769004815_amd64.deb`을 클릭하여 VS Code를 설치합니다.

<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @test:id=vscode-cli-windows timeout=120 hidden=True -->
```powershell
code --version
winget list --id Microsoft.VisualStudioCode -e
```
<!-- @test:end -->

<!-- @test:id=vscode-update-windows timeout=600 hidden=True -->
```powershell
winget upgrade --id Microsoft.VisualStudioCode -e --accept-source-agreements --accept-package-agreements --silent
code --version
winget list --id Microsoft.VisualStudioCode -e
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=vscode-ms-repo-key-present-linux timeout=120 hidden=True -->
```bash
test -f /etc/apt/sources.list.d/vscode.list
test -f /etc/apt/keyrings/microsoft.gpg
code --version
```
<!-- @test:end -->

<!-- @test:id=vscode-update-linux timeout=600 hidden=True -->
```bash
sudo -n apt-get update -y
sudo -n apt-get install -y --only-upgrade code
code --version
```
<!-- @test:end -->
<!-- @os:end -->