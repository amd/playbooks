<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Opdater til den nyeste AMD GPU driver ved hjælp af [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Åbn `AMD Software: Adrenalin Edition` fra din Startmenu eller systembakke.
2. Naviger til **Driver and Software**, klik på **Manage Updates**.
3. Hvis en opdatering er tilgængelig, følg vejledningen for at downloade og installere.

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

Installer AMD GPU Driver (amdgpu) ved hjælp af Radeon Software for Linux (RSL)-flowet. For instruktioner til din distribution, se [Installer kernedriver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->