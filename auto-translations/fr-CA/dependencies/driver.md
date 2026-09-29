<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Pilote AMD GPU

Mettez à jour vers le pilote AMD GPU le plus récent en utilisant [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ouvrez `AMD Software: Adrenalin Edition` à partir de votre menu Démarrer ou de la barre d'état système.
2. Accédez à **Driver and Software**, cliquez sur **Manage Updates**.
3. Si une mise à jour est disponible, suivez les instructions pour la télécharger et l'installer.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Pilote AMD GPU

Installez le pilote AMD GPU (amdgpu) en utilisant le processus Radeon Software for Linux (RSL). Pour connaître les instructions propres à votre distribution, consultez l'installation de ROCm à l'adresse suivante : [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Pour le pilote lui-même, consultez [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->