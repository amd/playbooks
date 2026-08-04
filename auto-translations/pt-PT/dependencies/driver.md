<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Controlador de GPU AMD

Atualize para o controlador de GPU AMD mais recente usando o [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

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

Instale o Controlador de GPU AMD (amdgpu) usando o fluxo do Radeon Software for Linux (RSL). Para obter instruções relativas à sua distribuição, consulte [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->