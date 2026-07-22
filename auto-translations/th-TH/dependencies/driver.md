<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### ไดรเวอร์ AMD GPU

อัปเดตไดรเวอร์ AMD GPU ให้เป็นเวอร์ชันล่าสุดโดยใช้ [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html)

1. เปิด `AMD Software: Adrenalin Edition` จากเมนู Start หรือถาดระบบ (system tray)
2. ไปที่ **Driver and Software** แล้วคลิก **Manage Updates**
3. หากมีอัปเดตให้ใช้งาน ให้ทำตามคำแนะนำเพื่อดาวน์โหลดและติดตั้ง

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### ไดรเวอร์ AMD GPU

ติดตั้งไดรเวอร์ AMD GPU (amdgpu) โดยใช้ขั้นตอนของ Radeon Software for Linux (RSL) สำหรับคำแนะนำเฉพาะดิสทริบิวชันของคุณ โปรดดูที่ [Install the kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)

<!-- @device:end -->
<!-- @os:end -->