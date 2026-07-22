<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Ovladač AMD GPU

Aktualizujte na nejnovější ovladač AMD GPU pomocí nástroje [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Otevřete `AMD Software: Adrenalin Edition` z nabídky Start nebo systémové lišty.
2. Přejděte na **Driver and Software** a klikněte na **Manage Updates**.
3. Pokud je k dispozici aktualizace, postupujte podle pokynů ke stažení a instalaci.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Ovladač AMD GPU

Nainstalujte ovladač AMD GPU (amdgpu) pomocí postupu Radeon Software for Linux (RSL). Pokyny pro vaši distribuci naleznete v části [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->