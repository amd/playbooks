<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU-drivrutin

Uppdatera till den senaste AMD GPU-drivrutinen med [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Öppna `AMD Software: Adrenalin Edition` från startmenyn eller aktivitetsfältet.
2. Navigera till **Driver and Software** och klicka på **Manage Updates**.
3. Om en uppdatering finns tillgänglig, följ anvisningarna för att ladda ned och installera.

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

Installera AMD GPU-drivrutinen (amdgpu) med flödet för Radeon Software for Linux (RSL). För instruktioner som gäller din distribution, se ROCm-installationen på: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

För själva drivrutinen, se [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->