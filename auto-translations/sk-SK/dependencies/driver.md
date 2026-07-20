<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Ovládač GPU AMD

Aktualizujte na najnovší ovládač GPU AMD pomocou [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Otvorte `AMD Software: Adrenalin Edition` z ponuky Štart alebo systémovej lišty.
2. Prejdite na **Driver and Software** a kliknite na **Manage Updates**.
3. Ak je k dispozícii aktualizácia, postupujte podľa pokynov na jej stiahnutie a inštaláciu.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Ovládač GPU AMD

Nainštalujte ovládač GPU AMD (amdgpu) pomocou procesu Radeon Software for Linux (RSL). Pokyny pre vašu distribúciu nájdete v časti [Inštalácia ovládača jadra](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->