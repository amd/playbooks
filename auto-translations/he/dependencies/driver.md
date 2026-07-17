<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

עדכן לדרייבר AMD GPU העדכני ביותר באמצעות [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. פתח את `AMD Software: Adrenalin Edition` מתפריט התחל או מסרגל המגש של המערכת.
2. נווט אל **Driver and Software**, לחץ על **Manage Updates**.
3. אם קיים עדכון זמין, עקוב אחר ההנחיות להורדה והתקנה.

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

התקן את דרייבר AMD GPU‏ (amdgpu) באמצעות תהליך Radeon Software for Linux‏ (RSL). להוראות עבור ההפצה שלך, ראה [התקנת דרייבר הקרנל](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->