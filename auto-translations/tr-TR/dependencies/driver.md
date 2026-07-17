<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

En son AMD GPU sürücüsüne [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) kullanarak güncelleyin.

1. Başlat menünüzden veya sistem tepsisinden `AMD Software: Adrenalin Edition` uygulamasını açın.
2. **Driver and Software** bölümüne gidin, **Manage Updates** seçeneğine tıklayın.
3. Bir güncelleme mevcutsa, indirip yüklemek için yönergeleri izleyin.

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

AMD GPU Driver'ı (amdgpu), Radeon Software for Linux (RSL) akışını kullanarak yükleyin. Dağıtımınıza yönelik talimatlar için bkz. [Çekirdek sürücüsünü yükleme](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->