<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
O VS Code pode ser instalado a partir do **AMD Ryzen™ AI Developer Center**. Aceda ao separador **Updates** e instale o VS Code caso ainda não esteja presente.
<!-- @os:end -->

<!-- @os:linux -->
O VS Code pode ser instalado a partir do **AMD Ryzen™ AI Developer Center**. Aceda ao separador **Manage** e instale o VS Code caso ainda não esteja presente.
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. Transfira o executável de instalação para Windows a partir de: https://update.code.visualstudio.com/1.108.2/win32-x64-user/stable.
2. Clique no ficheiro transferido `VSCodeUserSetup-x64-1.108.2.exe` para instalar o VS Code.

<!-- @os:end -->

<!-- @os:linux -->

1. Transfira o pacote de instalação Debian a partir de: https://update.code.visualstudio.com/1.108.2/linux-deb-x64/stable.
2. Clique no ficheiro transferido `code_1.108.2-1769004815_amd64.deb` para instalar o VS Code.

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