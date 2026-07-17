<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

อัปเดตเป็น AMD GPU Driver เวอร์ชันล่าสุดโดยใช้ [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html)

1. เปิด `AMD Software: Adrenalin Edition` จากเมนู Start หรือ system tray ของคุณ
2. ไปที่ **Driver and Software** แล้วคลิก **Manage Updates**
3. หากมีการอัปเดต ให้ทำตามคำแนะนำเพื่อดาวน์โหลดและติดตั้ง

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

ติดตั้ง AMD GPU Driver (amdgpu) โดยใช้ขั้นตอน Radeon Software for Linux (RSL) สำหรับคำแนะนำสำหรับ distribution ของคุณ โปรดดูที่ [ติดตั้ง kernel driver](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)

<!-- @device:end -->
<!-- @os:end -->