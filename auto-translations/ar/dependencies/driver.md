<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### تعريف كارت الشاشة AMD

قم بتحديث تعريف كارت شاشة AMD إلى أحدث إصدار باستخدام [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. افتح `AMD Software: Adrenalin Edition` من قائمة ابدأ أو من شريط النظام.
2. انتقل إلى **Driver and Software**، ثم انقر على **Manage Updates**.
3. إذا كان هناك تحديث متاح، اتبع التعليمات لتنزيله وتثبيته.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### تعريف كارت الشاشة AMD

قم بتثبيت تعريف كارت شاشة AMD (amdgpu) باستخدام آلية Radeon Software for Linux (RSL). للحصول على التعليمات الخاصة بتوزيعتك، راجع تثبيت ROCm على: [تثبيت تعريف النواة (kernel driver)](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

للحصول على التعريف نفسه، راجع [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->