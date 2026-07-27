<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
VS Code può essere installato dal **AMD Ryzen™ AI Developer Center**. Andare alla scheda **Updates** e installare VS Code se non è già presente.
<!-- @os:end -->

<!-- @os:linux -->
VS Code può essere installato dal **AMD Ryzen™ AI Developer Center**. Andare alla scheda **Manage** e installare VS Code se non è già presente.
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. Scaricare l'eseguibile di installazione per Windows da: https://update.code.visualstudio.com/1.108.2/win32-x64-user/stable.
2. Fare clic sul file scaricato `VSCodeUserSetup-x64-1.108.2.exe` per installare VS Code.

<!-- @os:end -->

<!-- @os:linux -->

1. Scaricare il pacchetto di installazione Debian da: https://update.code.visualstudio.com/1.108.2/linux-deb-x64/stable.
2. Fare clic sul file scaricato `code_1.108.2-1769004815_amd64.deb` per installare VS Code.

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