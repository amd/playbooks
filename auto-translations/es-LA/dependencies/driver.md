<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Actualiza al controlador de AMD GPU más reciente usando [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abre `AMD Software: Adrenalin Edition` desde el menú Inicio o la bandeja del sistema.
2. Ve a **Driver and Software**, haz clic en **Manage Updates**.
3. Si hay una actualización disponible, sigue las instrucciones para descargar e instalar.

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

Instala el AMD GPU Driver (amdgpu) usando el flujo de Radeon Software for Linux (RSL). Para obtener instrucciones para tu distribución, consulta [Instalar el controlador del kernel](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->