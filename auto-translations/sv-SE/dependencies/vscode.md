<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
VS Code kan installeras från **AMD Ryzen™ AI Developer Center**. Gå till fliken **Updates** och installera VS Code om det inte redan finns installerat.
<!-- @os:end -->

<!-- @os:linux -->
VS Code kan installeras från **AMD Ryzen™ AI Developer Center**. Gå till fliken **Manage** och installera VS Code om det inte redan finns installerat.
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. Ladda ner Windows-installationsfilen från: https://update.code.visualstudio.com/1.108.2/win32-x64-user/stable.
2. Klicka på den nedladdade filen `VSCodeUserSetup-x64-1.108.2.exe` för att installera VS Code.

<!-- @os:end -->

<!-- @os:linux -->

1. Ladda ner Debian-installationspaketet från: https://update.code.visualstudio.com/1.108.2/linux-deb-x64/stable.
2. Klicka på den nedladdade filen `code_1.108.2-1769004815_amd64.deb` för att installera VS Code.

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