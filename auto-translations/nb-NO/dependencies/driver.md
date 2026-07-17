<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Oppdater til den nyeste AMD GPU-driveren ved hjelp av [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

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
### AMD GPU Driver

Installer AMD GPU-driveren (amdgpu) ved hjelp av Radeon Software for Linux (RSL)-flyten. For instruksjoner for din distribusjon, se [Installer kjernedriveren](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->