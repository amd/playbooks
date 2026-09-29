<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU illesztőprogram

Frissítsd a legújabb AMD GPU illesztőprogramra a [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) segítségével.

1. Nyisd meg az `AMD Software: Adrenalin Edition` alkalmazást a Start menüből vagy a rendszertálcáról.
2. Navigálj a **Driver and Software** menüpontra, majd kattints a **Manage Updates** gombra.
3. Ha van elérhető frissítés, kövesd az utasításokat a letöltéshez és telepítéshez.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU illesztőprogram

Telepítsd az AMD GPU illesztőprogramot (amdgpu) a Radeon Software for Linux (RSL) folyamat segítségével. A saját disztribúciódra vonatkozó utasításokért lásd a ROCm telepítést itt: [Kernel illesztőprogram telepítése](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Magához az illesztőprogramhoz lásd: [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->