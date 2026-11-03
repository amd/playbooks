<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU-driver

Oppdater til den nyeste AMD GPU-driveren ved å bruke [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Åpne `AMD Software: Adrenalin Edition` fra Start-menyen eller systemstatusfeltet.
2. Naviger til **Driver and Software**, klikk på **Manage Updates**.
3. Hvis en oppdatering er tilgjengelig, følg instruksjonene for å laste ned og installere.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU-driver

Installer AMD GPU-driveren (amdgpu) ved å bruke Radeon Software for Linux (RSL)-flyten. For instruksjoner for din distribusjon, se ROCm-installasjonen på: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

For selve driveren, se [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->