<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Frissítsen a legújabb AMD GPU illesztőprogramra az [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) segítségével.

1. Nyissa meg az `AMD Software: Adrenalin Edition` alkalmazást a Start menüből vagy a rendszertálcáról.
2. Navigáljon a **Driver and Software** menüpontra, majd kattintson a **Manage Updates** lehetőségre.
3. Ha elérhető frissítés, kövesse az utasításokat a letöltéshez és telepítéshez.

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

Telepítse az AMD GPU illesztőprogramot (amdgpu) a Radeon Software for Linux (RSL) folyamat segítségével. Az egyes disztribúciókra vonatkozó utasításokért lásd: [A kernel illesztőprogram telepítése](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->