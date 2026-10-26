<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Driver GPU AMD

Aggiorna all'ultimo driver GPU AMD utilizzando [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Apri `AMD Software: Adrenalin Edition` dal menu Start o dalla barra delle applicazioni.
2. Vai su **Driver and Software**, fai clic su **Manage Updates**.
3. Se è disponibile un aggiornamento, segui le istruzioni per scaricarlo e installarlo.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Driver GPU AMD

Installa il driver GPU AMD (amdgpu) utilizzando il flusso Radeon Software for Linux (RSL). Per le istruzioni relative alla tua distribuzione, consulta l'installazione di ROCm su: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Per il driver stesso, consulta [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->