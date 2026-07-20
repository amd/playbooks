<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### דרייבר GPU של AMD

עדכן לגרסה העדכנית ביותר של דרייבר ה-GPU של AMD באמצעות [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. פתח את `AMD Software: Adrenalin Edition` מתפריט ההתחלה או ממגש המערכת.
2. נווט אל **Driver and Software**, ולחץ על **Manage Updates**.
3. אם קיים עדכון זמין, פעל לפי ההנחיות להורדה והתקנה.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### דרייבר GPU של AMD

התקן את דרייבר ה-GPU של AMD (amdgpu) באמצעות תהליך ה-Radeon Software for Linux (RSL). להנחיות עבור ההפצה שלך, ראה [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->