<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU-drivrutin

Uppdatera till den senaste AMD GPU-drivrutinen med [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Öppna `AMD Software: Adrenalin Edition` från Start-menyn eller systemfältet.
2. Navigera till **Driver and Software**, klicka på **Manage Updates**.
3. Om en uppdatering är tillgänglig, följ anvisningarna för att hämta och installera den.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU-drivrutin

Installera AMD GPU-drivrutinen (amdgpu) med flödet för Radeon Software for Linux (RSL). För instruktioner för din distribution, se ROCm-installationen på: [Installera kärndrivrutinen](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

För själva drivrutinen, se [Linux®-drivrutiner för AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->