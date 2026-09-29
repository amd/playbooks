<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Controlador de GPU AMD

Atualize para o controlador de GPU AMD mais recente utilizando o [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abra o `AMD Software: Adrenalin Edition` a partir do menu Iniciar ou do tabuleiro do sistema.
2. Navegue até **Driver and Software**, clique em **Manage Updates**.
3. Se estiver disponível uma atualização, siga as instruções para transferir e instalar.

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

Instale o controlador de GPU AMD (amdgpu) utilizando o fluxo Radeon Software for Linux (RSL). Para instruções relativas à sua distribuição, consulte a instalação do ROCm em: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Para o controlador em si, consulte [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->