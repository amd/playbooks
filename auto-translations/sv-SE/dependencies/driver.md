<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Uppdatera till den senaste AMD GPU-drivrutinen med hjälp av [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Öppna `AMD Software: Adrenalin Edition` från din Startmeny eller systemfältet.
2. Navigera till **Driver and Software**, klicka på **Manage Updates**.
3. Om en uppdatering är tillgänglig, följ anvisningarna för att ladda ner och installera.

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

Installera AMD GPU-drivrutinen (amdgpu) med hjälp av Radeon Software for Linux (RSL)-flödet. För instruktioner för din distribution, se [Installera kärndrivrutinen](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->