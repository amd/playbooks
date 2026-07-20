<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU-stuurprogramma

Werk bij naar het nieuwste AMD GPU-stuurprogramma met behulp van [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Open `AMD Software: Adrenalin Edition` vanuit uw Startmenu of systeemvak.
2. Navigeer naar **Driver and Software** en klik op **Manage Updates**.
3. Als er een update beschikbaar is, volgt u de aanwijzingen om deze te downloaden en te installeren.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU-stuurprogramma

Installeer het AMD GPU-stuurprogramma (amdgpu) met behulp van de Radeon Software for Linux (RSL)-procedure. Raadpleeg voor instructies voor uw distributie [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->