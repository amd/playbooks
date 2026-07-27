<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Controlador de GPU AMD

Actualice al controlador de GPU AMD más reciente usando [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abra `AMD Software: Adrenalin Edition` desde el menú Inicio o la bandeja del sistema.
2. Navegue a **Driver and Software**, haga clic en **Manage Updates**.
3. Si hay una actualización disponible, siga las indicaciones para descargarla e instalarla.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Controlador de GPU AMD

Instale el controlador de GPU AMD (amdgpu) usando el flujo de Radeon Software for Linux (RSL). Para obtener instrucciones para su distribución, consulte [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->