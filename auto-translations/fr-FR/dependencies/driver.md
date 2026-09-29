<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Pilote GPU AMD

Mettez à jour vers le dernier pilote GPU AMD à l'aide de [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ouvrez `AMD Software: Adrenalin Edition` depuis le menu Démarrer ou la barre d'état système.
2. Accédez à **Pilote et logiciel**, cliquez sur **Gérer les mises à jour**.
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
### Pilote GPU AMD

Installez le pilote GPU AMD (amdgpu) à l'aide du flux Radeon Software for Linux (RSL). Pour connaître les instructions relatives à votre distribution, consultez l'installation de ROCm à l'adresse : [Installer le pilote du noyau](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Pour le pilote lui-même, consultez [Pilotes Linux® pour AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->