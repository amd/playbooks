<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU 驱动程序

使用 [`AMD Software: Adrenalin Edition™`](https://www.amd.com/zh-cn/products/software/adrenalin.html) 更新到最新的 AMD GPU 驱动程序。

1. 从开始菜单或系统托盘打开 `AMD Software: Adrenalin Edition`。
2. 导航到**驱动程序和软件**，点击**管理更新**。
3. 如果有可用的更新，请按照提示下载并安装。

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU 驱动程序

使用适用于 Linux 的 Radeon 软件（RSL）流程安装 AMD GPU 驱动程序（amdgpu）。有关适用于您所使用发行版的说明，请参阅[安装内核驱动程序](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)。

<!-- @device:end -->
<!-- @os:end -->
