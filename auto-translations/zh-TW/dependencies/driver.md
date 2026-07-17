<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

使用 [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) 更新至最新的 AMD GPU 驅動程式。

1. 從開始選單或系統匣開啟 `AMD Software: Adrenalin Edition`。
2. 前往 **Driver and Software**，點擊 **Manage Updates**。
3. 若有可用更新，請依照提示下載並安裝。

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

使用 Radeon Software for Linux (RSL) 流程安裝 AMD GPU Driver (amdgpu)。有關您的發行版的安裝說明，請參閱[安裝核心驅動程式](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)。

<!-- @device:end -->
<!-- @os:end -->