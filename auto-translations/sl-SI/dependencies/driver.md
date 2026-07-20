<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Gonilnik AMD GPU

Posodobite na najnovejši gonilnik AMD GPU s pomočjo [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

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
### Gonilnik AMD GPU

Namestite gonilnik AMD GPU (amdgpu) s pomočjo poteka Radeon Software for Linux (RSL). Za navodila za svojo distribucijo glejte [Namestitev gonilnika jedra](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->