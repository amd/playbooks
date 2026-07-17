<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Visual Studio Code

<!-- @device:halo_box -->
<!-- @os:windows -->
VS Code สามารถติดตั้งได้จาก **AMD Ryzen™ AI Developer Center** ไปที่แท็บ **Updates** และติดตั้ง VS Code หากยังไม่ได้ติดตั้ง
<!-- @os:end -->

<!-- @os:linux -->
VS Code สามารถติดตั้งได้จาก **AMD Ryzen™ AI Developer Center** ไปที่แท็บ **Manage** และติดตั้ง VS Code หากยังไม่ได้ติดตั้ง
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->

1. ดาวน์โหลดไฟล์ติดตั้งสำหรับ Windows จาก: https://update.code.visualstudio.com/1.108.2/win32-x64-user/stable
2. คลิกที่ไฟล์ที่ดาวน์โหลด `VSCodeUserSetup-x64-1.108.2.exe` เพื่อติดตั้ง VS Code

<!-- @os:end -->

<!-- @os:linux -->

1. ดาวน์โหลดแพ็กเกจติดตั้ง Debian จาก: https://update.code.visualstudio.com/1.108.2/linux-deb-x64/stable
2. คลิกที่ไฟล์ที่ดาวน์โหลด `code_1.108.2-1769004815_amd64.deb` เพื่อติดตั้ง VS Code

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