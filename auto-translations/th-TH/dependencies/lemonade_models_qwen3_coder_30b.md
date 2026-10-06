<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด Qwen3-Coder 30B A3B สำหรับ Lemonade

เซิร์ฟเวอร์ Lemonade ให้บริการโมเดล Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`) หากต้องการดาวน์โหลดล่วงหน้า:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` ยังดาวน์โหลดโมเดลในการใช้งานครั้งแรกด้วยหากยังไม่มีอยู่ จากนั้นจะโหลดโมเดลเพื่อใช้ในการอนุมาน

โมเดลจะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของเซิร์ฟเวอร์ Lemonade เมื่อการดึงข้อมูลเสร็จสมบูรณ์ โดยการตรวจสอบด้านล่างนี้จะยืนยันว่ามีโมเดลอยู่ในเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->