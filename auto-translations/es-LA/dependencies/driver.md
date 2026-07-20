<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Controlador de GPU de AMD

Actualiza al controlador de GPU de AMD más reciente usando [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abre `AMD Software: Adrenalin Edition` desde el menú Inicio o la bandeja del sistema.
2. Navega a **Driver and Software**, haz clic en **Manage Updates**.
3. Si hay una actualización disponible, sigue las indicaciones para descargarla e instalarla.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Controlador de GPU de AMD

Instala el controlador de GPU de AMD (amdgpu) usando el flujo de Radeon Software for Linux (RSL). Para conocer las instrucciones específicas de tu distribución, consulta [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->