<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
VS Code can be installed from the **AMD Ryzen™ AI Developer Center**. Go to the **Updates** tab and install VS Code if it is not already present.
<!-- @os:end -->

<!-- @os:linux -->
VS Code can be installed from the **AMD Ryzen™ AI Developer Center**. Go to the **Manage** tab and install VS Code if it is not already present.
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,grgh,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. Download the Windows installation executable from: https://update.code.visualstudio.com/latest/win32-x64-user/stable.
2. Run the downloaded `VSCodeUserSetup-x64-<version>.exe` to install VS Code.

<!-- @os:end -->

<!-- @os:linux -->

1. Download the Debian installation package from: https://update.code.visualstudio.com/latest/linux-deb-x64/stable.
2. Install the downloaded `code_<version>_amd64.deb` package.

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
