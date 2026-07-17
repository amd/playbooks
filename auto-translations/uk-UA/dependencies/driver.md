<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Оновіть до останньої версії драйвера AMD GPU за допомогою [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Відкрийте `AMD Software: Adrenalin Edition` з меню «Пуск» або системного трею.
2. Перейдіть до **Driver and Software**, натисніть **Manage Updates**.
3. Якщо доступне оновлення, дотримуйтесь підказок для завантаження та встановлення.

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

Встановіть AMD GPU Driver (amdgpu) за допомогою процесу Radeon Software for Linux (RSL). Інструкції для вашого дистрибутива див. у розділі [Встановлення драйвера ядра](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->