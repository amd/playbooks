<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด Qwen3.5 4B สำหรับ Lemonade

Lemonade server ให้บริการโมเดล Qwen3.5 4B (`Qwen3.5-4B-GGUF`) หากต้องการดาวน์โหลดล่วงหน้า:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` จะดาวน์โหลดโมเดลโดยอัตโนมัติในการใช้งานครั้งแรกหากยังไม่มีอยู่ในเครื่อง จากนั้นจะโหลดโมเดลเพื่อใช้ในการอนุมาน (inference)

โมเดลจะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของ Lemonade server เมื่อการดึงข้อมูลเสร็จสมบูรณ์ โดยการตรวจสอบด้านล่างนี้จะยืนยันว่าโมเดลมีอยู่ในเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->