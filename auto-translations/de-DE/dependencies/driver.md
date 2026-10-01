<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU-Treiber

Aktualisieren Sie auf den neuesten AMD GPU-Treiber mit [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Öffnen Sie `AMD Software: Adrenalin Edition` über Ihr Startmenü oder Ihre Systemablage.
2. Navigieren Sie zu **Driver and Software** und klicken Sie auf **Manage Updates**.
3. Falls ein Update verfügbar ist, folgen Sie den Anweisungen, um es herunterzuladen und zu installieren.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU-Treiber

Installieren Sie den AMD GPU-Treiber (amdgpu) über den Radeon Software for Linux (RSL)-Ablauf. Anweisungen für Ihre Distribution finden Sie in der ROCm-Installation unter: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Den eigentlichen Treiber finden Sie unter [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->