<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด Qwen3 4B Hybrid สำหรับ Lemonade

เซิร์ฟเวอร์ Lemonade ให้บริการโมเดล Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`) ซึ่งทำงานบน NPU และ GPU ของโปรเซสเซอร์ Ryzen AI หากต้องการดาวน์โหลดล่วงหน้า:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

โมเดลจะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของเซิร์ฟเวอร์ Lemonade เมื่อการดึงข้อมูลเสร็จสมบูรณ์ โดยการตรวจสอบด้านล่างนี้จะยืนยันว่าโมเดลมีอยู่ในเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->