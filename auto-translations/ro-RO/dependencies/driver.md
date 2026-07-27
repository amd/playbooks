<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Driver AMD GPU

Actualizați la cel mai recent driver AMD GPU folosind [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

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
### Driver AMD GPU

Instalați driverul AMD GPU (amdgpu) folosind fluxul Radeon Software for Linux (RSL). Pentru instrucțiuni specifice distribuției dvs., consultați [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->