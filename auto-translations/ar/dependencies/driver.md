<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

قم بالتحديث إلى أحدث إصدار من برنامج تشغيل AMD GPU باستخدام [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. افتح `AMD Software: Adrenalin Edition` من قائمة ابدأ أو علبة النظام.
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
### AMD GPU Driver

قم بتثبيت برنامج تشغيل AMD GPU (amdgpu) باستخدام تدفق Radeon Software for Linux (RSL). للاطلاع على التعليمات الخاصة بتوزيعتك، راجع [تثبيت برنامج تشغيل النواة](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->