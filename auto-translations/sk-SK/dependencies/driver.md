<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Ovládač AMD GPU

Aktualizujte na najnovší ovládač AMD GPU pomocou nástroja [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Otvorte `AMD Software: Adrenalin Edition` z ponuky Štart alebo systémovej lišty.
2. Prejdite na **Driver and Software**, kliknite na **Manage Updates**.
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
### Ovládač AMD GPU

Nainštalujte ovládač AMD GPU (amdgpu) pomocou postupu Radeon Software for Linux (RSL). Pokyny pre vašu distribúciu nájdete v návode na inštaláciu ROCm na: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Samotný ovládač nájdete tu: [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->