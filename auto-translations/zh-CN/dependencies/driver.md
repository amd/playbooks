<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

使用 [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) 更新至最新的 AMD GPU 驱动程序。

1. 从开始菜单或系统托盘打开 `AMD Software: Adrenalin Edition`。
2. 导航至 **Driver and Software**，点击 **Manage Updates**。
3. 如果有可用更新，按照提示下载并安装。

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU Driver

使用 Radeon Software for Linux（RSL）流程安装 AMD GPU 驱动程序（amdgpu）。有关适用于您的发行版的说明，请参阅[安装内核驱动程序](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)。

<!-- @device:end -->
<!-- @os:end -->