<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU-drivrutin

Uppdatera till den senaste AMD GPU-drivrutinen med [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Öppna `AMD Software: Adrenalin Edition` från Start-menyn eller systemfältet.
2. Navigera till **Driver and Software** och klicka på **Manage Updates**.
3. Om en uppdatering finns tillgänglig, följ instruktionerna för att ladda ner och installera den.

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

Installera AMD GPU-drivrutinen (amdgpu) med hjälp av flödet Radeon Software for Linux (RSL). För instruktioner för din distribution, se [Installera kärndrivrutinen](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->