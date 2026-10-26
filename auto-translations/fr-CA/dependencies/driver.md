<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Pilote GPU AMD

Mettez à jour le pilote GPU AMD le plus récent à l'aide de [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ouvrez `AMD Software: Adrenalin Edition` à partir du menu Démarrer ou de la zone de notification système.
2. Accédez à **Driver and Software**, puis cliquez sur **Manage Updates**.
3. Si une mise à jour est disponible, suivez les invites pour la télécharger et l'installer.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Pilote GPU AMD

Installez le pilote GPU AMD (amdgpu) à l'aide du processus Radeon Software for Linux (RSL). Pour connaître les instructions propres à votre distribution, consultez la procédure d'installation de ROCm : [Installer le pilote du noyau](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Pour le pilote lui-même, consultez [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->