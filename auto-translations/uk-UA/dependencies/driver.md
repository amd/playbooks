<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Драйвер AMD GPU

Оновіть до останньої версії драйвера AMD GPU за допомогою [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Відкрийте `AMD Software: Adrenalin Edition` з меню Пуск або системного трею.
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
### Драйвер AMD GPU

Встановіть драйвер AMD GPU (amdgpu) за допомогою потоку Radeon Software for Linux (RSL). Для отримання інструкцій щодо вашого дистрибутива див. інсталяцію ROCm за адресою: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Щодо самого драйвера див. [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->