<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Pilote GPU AMD

Mettez à jour vers la dernière version du pilote GPU AMD à l'aide de [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Ouvrez `AMD Software: Adrenalin Edition` à partir du menu Démarrer ou de la barre d'état système.
2. Accédez à **Driver and Software**, cliquez sur **Manage Updates**.
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

Installez le pilote GPU AMD (amdgpu) en suivant le processus Radeon Software for Linux (RSL). Pour connaître les instructions propres à votre distribution, consultez [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->