<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU illesztőprogram

Frissítse a legújabb AMD GPU illesztőprogramra a(z) [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) segítségével.

1. Nyissa meg az `AMD Software: Adrenalin Edition` alkalmazást a Start menüből vagy a rendszertálcáról.
2. Navigáljon a **Driver and Software** menüpontra, majd kattintson a **Manage Updates** gombra.
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
### AMD GPU illesztőprogram

Telepítse az AMD GPU illesztőprogramot (amdgpu) a Radeon Software for Linux (RSL) folyamat segítségével. Az Ön disztribúciójára vonatkozó utasításokért lásd a ROCm telepítést itt: [A kernel illesztőprogram telepítése](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Magához az illesztőprogramhoz lásd: [Linux® illesztőprogramok AMD Radeon™-hoz](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->