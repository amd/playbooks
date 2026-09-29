<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU 驅動程式

請使用 [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) 更新至最新的 AMD GPU 驅動程式。

1. 從您的開始功能表或系統匣開啟 `AMD Software: Adrenalin Edition`。
2. 導覽至 **Driver and Software**，點選 **Manage Updates**。
3. 若有可用的更新，請依照提示下載並安裝。

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU 驅動程式

請使用 Radeon Software for Linux (RSL) 流程安裝 AMD GPU 驅動程式 (amdgpu)。若需針對您所使用的發行版的安裝說明，請參閱 ROCm 安裝說明：[安裝核心驅動程式](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install)。

如需驅動程式本身，請參閱 [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->