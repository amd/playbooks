<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Driver da GPU AMD

Atualize para o driver de GPU AMD mais recente usando [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abra o `AMD Software: Adrenalin Edition` a partir do menu Iniciar ou da bandeja do sistema.
2. Navegue até **Driver and Software**, clique em **Manage Updates**.
3. Se houver uma atualização disponível, siga as instruções para baixar e instalar.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Driver da GPU AMD

Instale o Driver de GPU AMD (amdgpu) usando o fluxo do Radeon Software for Linux (RSL). Para obter instruções específicas da sua distribuição, consulte a instalação do ROCm em: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Para o driver em si, consulte [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->