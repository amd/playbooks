<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
VS Code można zainstalować z **AMD Ryzen™ AI Developer Center**. Przejdź do zakładki **Updates** i zainstaluj VS Code, jeśli nie jest jeszcze zainstalowany.
<!-- @os:end -->

<!-- @os:linux -->
VS Code można zainstalować z **AMD Ryzen™ AI Developer Center**. Przejdź do zakładki **Manage** i zainstaluj VS Code, jeśli nie jest jeszcze zainstalowany.
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. Pobierz instalator systemu Windows ze strony: https://update.code.visualstudio.com/1.108.2/win32-x64-user/stable.
2. Kliknij pobrany plik `VSCodeUserSetup-x64-1.108.2.exe`, aby zainstalować VS Code.

<!-- @os:end -->

<!-- @os:linux -->

1. Pobierz pakiet instalacyjny Debian ze strony: https://update.code.visualstudio.com/1.108.2/linux-deb-x64/stable.
2. Kliknij pobrany plik `code_1.108.2-1769004815_amd64.deb`, aby zainstalować VS Code.

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