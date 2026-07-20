<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Sürücüsü

[`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) kullanarak en son AMD GPU sürücüsüne güncelleyin.

1. Başlat menünüzden veya sistem tepsisinden `AMD Software: Adrenalin Edition` uygulamasını açın.
2. **Driver and Software** bölümüne gidin, **Manage Updates** üzerine tıklayın.
3. Bir güncelleme varsa, indirmek ve yüklemek için istemleri izleyin.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU Sürücüsü

Radeon Software for Linux (RSL) akışını kullanarak AMD GPU Sürücüsünü (amdgpu) yükleyin. Dağıtımınıza yönelik talimatlar için bkz. [Çekirdek sürücüsünü yükleyin](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->