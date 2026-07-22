<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Gonilnik za grafično kartico AMD

Posodobite na najnovejši gonilnik za grafično kartico AMD z uporabo [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Odprite `AMD Software: Adrenalin Edition` v meniju Start ali v sistemski vrstici.
2. Pojdite na **Driver and Software**, kliknite **Manage Updates**.
3. Če je posodobitev na voljo, sledite pozivom za prenos in namestitev.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Gonilnik za grafično kartico AMD

Namestite gonilnik za grafično kartico AMD (amdgpu) z uporabo poteka Radeon Software for Linux (RSL). Za navodila za vašo distribucijo glejte [Namestitev gonilnika jedra](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->