<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### מנהל ההתקן של AMD GPU

עדכן למנהל ההתקן האחרון של AMD GPU באמצעות [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. פתח את `AMD Software: Adrenalin Edition` מתפריט ה-Start או ממגש המערכת.
2. נווט אל **Driver and Software**, לחץ על **Manage Updates**.
3. אם עדכון זמין, פעל לפי ההנחיות להורדה והתקנה.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### מנהל ההתקן של AMD GPU

התקן את מנהל ההתקן של AMD GPU (amdgpu) באמצעות תהליך ה-Radeon Software for Linux ‏(RSL). להוראות עבור ההפצה שלך, עיין בהתקנת ROCm בכתובת: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

עבור מנהל ההתקן עצמו, ראה [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->