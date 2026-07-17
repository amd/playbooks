<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Posodobite na najnovejši AMD GPU gonilnik z uporabo [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Odprite `AMD Software: Adrenalin Edition` iz menija Start ali sistemske vrstice.
2. Pomaknite se na **Driver and Software**, kliknite **Manage Updates**.
3. Če je na voljo posodobitev, sledite pozivom za prenos in namestitev.

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

Namestite AMD GPU gonilnik (amdgpu) z uporabo toka Radeon Software for Linux (RSL). Za navodila za vašo distribucijo glejte [Namestitev jedrnega gonilnika](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->