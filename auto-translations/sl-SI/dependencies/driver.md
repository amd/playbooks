<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Gonilnik za AMD GPU

Posodobite na najnovejši gonilnik za AMD GPU s pomočjo [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

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
### Gonilnik za AMD GPU

Namestite gonilnik za AMD GPU (amdgpu) s pomočjo poteka Radeon Software for Linux (RSL). Za navodila za vašo distribucijo glejte namestitev ROCm na: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Za sam gonilnik glejte [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->