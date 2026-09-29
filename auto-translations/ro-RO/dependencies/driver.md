<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Driver GPU AMD

Actualizați la cel mai recent driver GPU AMD folosind [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Deschideți `AMD Software: Adrenalin Edition` din meniul Start sau din bara de sistem.
2. Navigați la **Driver and Software**, faceți clic pe **Manage Updates**.
3. Dacă este disponibilă o actualizare, urmați instrucțiunile pentru a o descărca și instala.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Driver GPU AMD

Instalați Driverul GPU AMD (amdgpu) folosind fluxul Radeon Software for Linux (RSL). Pentru instrucțiuni specifice distribuției dumneavoastră, consultați instalarea ROCm la: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Pentru driverul propriu-zis, consultați [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->