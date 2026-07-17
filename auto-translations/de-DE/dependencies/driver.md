<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Aktualisieren Sie auf den neuesten AMD GPU Driver mithilfe von [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Öffnen Sie `AMD Software: Adrenalin Edition` über Ihr Startmenü oder den Systembereich.
2. Navigieren Sie zu **Driver and Software** und klicken Sie auf **Manage Updates**.
3. Falls ein Update verfügbar ist, folgen Sie den Anweisungen zum Herunterladen und Installieren.

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

Installieren Sie den AMD GPU Driver (amdgpu) mithilfe des Radeon Software for Linux (RSL)-Verfahrens. Anweisungen für Ihre Distribution finden Sie unter [Kernel-Treiber installieren](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->