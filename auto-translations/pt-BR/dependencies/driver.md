<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Driver de GPU AMD

Atualize para o driver de GPU AMD mais recente usando o [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abra o `AMD Software: Adrenalin Edition` no menu Iniciar ou na bandeja do sistema.
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
### Driver de GPU AMD

Instale o Driver de GPU AMD (amdgpu) usando o fluxo do Radeon Software for Linux (RSL). Para instruções específicas da sua distribuição, consulte [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->