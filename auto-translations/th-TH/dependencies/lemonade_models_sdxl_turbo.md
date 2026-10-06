<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด SDXL-Turbo สำหรับ Lemonade

เซิร์ฟเวอร์ Lemonade ให้บริการโมเดล SDXL-Turbo (`SDXL-Turbo`) หากต้องการดาวน์โหลดล่วงหน้า:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` จะดาวน์โหลดโมเดลโดยอัตโนมัติเมื่อใช้งานครั้งแรกหากยังไม่มีอยู่ในเครื่อง จากนั้นจะโหลดโมเดลเพื่อใช้ในการอนุมาน

โมเดลจะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของเซิร์ฟเวอร์ Lemonade เมื่อการดึงข้อมูลเสร็จสมบูรณ์ โดยการตรวจสอบด้านล่างนี้จะยืนยันว่ามีโมเดลอยู่ในเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->