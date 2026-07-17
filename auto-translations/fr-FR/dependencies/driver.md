<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Mettez à jour vers le dernier pilote AMD GPU en utilisant [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ouvrez `AMD Software: Adrenalin Edition` depuis votre menu Démarrer ou la barre des tâches système.
2. Accédez à **Driver and Software**, cliquez sur **Manage Updates**.
3. Si une mise à jour est disponible, suivez les instructions pour télécharger et installer.

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

Installez le AMD GPU Driver (amdgpu) en utilisant le flux Radeon Software for Linux (RSL). Pour les instructions relatives à votre distribution, consultez [Installer le pilote noyau](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->