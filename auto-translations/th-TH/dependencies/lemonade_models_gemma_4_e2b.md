<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด Gemma-4 E2B สำหรับ Lemonade

เซิร์ฟเวอร์ Lemonade ให้บริการโมเดล Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`) หากต้องการดาวน์โหลดล่วงหน้า:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` จะดาวน์โหลดโมเดลโดยอัตโนมัติเมื่อใช้งานครั้งแรกหากยังไม่มีอยู่ในเครื่อง จากนั้นจะโหลดโมเดลเพื่อใช้ในการอนุมาน (inference)

โมเดลจะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของเซิร์ฟเวอร์ Lemonade เมื่อการดึงข้อมูลเสร็จสมบูรณ์ โดยการตรวจสอบด้านล่างนี้จะยืนยันว่าโมเดลมีอยู่ในเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->