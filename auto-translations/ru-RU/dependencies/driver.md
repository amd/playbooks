<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Обновите драйвер AMD GPU до последней версии с помощью [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Откройте `AMD Software: Adrenalin Edition` из меню «Пуск» или системного трея.
2. Перейдите в раздел **Driver and Software** и нажмите **Manage Updates**.
3. Если доступно обновление, следуйте инструкциям для загрузки и установки.

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

Установите драйвер AMD GPU (amdgpu) с помощью процедуры Radeon Software for Linux (RSL). Инструкции для вашего дистрибутива см. в разделе [Установка драйвера ядра](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->