<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Atualize para o driver AMD GPU mais recente usando o [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Abra o `AMD Software: Adrenalin Edition` pelo menu Iniciar ou pela bandeja do sistema.
2. Navegue até **Driver and Software**, clique em **Manage Updates**.
3. Se uma atualização estiver disponível, siga as instruções para baixar e instalar.

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

Instale o AMD GPU Driver (amdgpu) usando o fluxo Radeon Software for Linux (RSL). Para instruções específicas da sua distribuição, consulte [Instalar o driver do kernel](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->