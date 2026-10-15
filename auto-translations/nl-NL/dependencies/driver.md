<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Werk de nieuwste AMD GPU-driver bij met behulp van [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Open `AMD Software: Adrenalin Edition` vanuit uw Start menu of systeemvak.
2. Navigeer naar **Driver and Software** en klik op **Manage Updates**.
3. Als er een update beschikbaar is, volg dan de aanwijzingen om deze te downloaden en te installeren.

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

Installeer de AMD GPU Driver (amdgpu) via de Radeon Software for Linux (RSL)-flow. Raadpleeg voor instructies voor uw distributie de ROCm-installatie op: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Voor de driver zelf, zie [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->