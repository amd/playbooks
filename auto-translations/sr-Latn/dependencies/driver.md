<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU drajver

Ažurirajte na najnoviji AMD GPU drajver koristeći [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Otvorite `AMD Software: Adrenalin Edition` iz Start menija ili sistemske trake.
2. Idite na **Driver and Software**, kliknite na **Manage Updates**.
3. Ako je dostupno ažuriranje, pratite uputstva za preuzimanje i instalaciju.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU drajver

Instalirajte AMD GPU drajver (amdgpu) koristeći tok Radeon Software for Linux (RSL). Za uputstva za vašu distribuciju, pogledajte [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->