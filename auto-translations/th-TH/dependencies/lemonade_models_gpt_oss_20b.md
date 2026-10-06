<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด GPT-OSS 20B สำหรับ Lemonade

เซิร์ฟเวอร์ Lemonade ให้บริการโมเดล GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`) หากต้องการดาวน์โหลดล่วงหน้า:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` จะดาวน์โหลดโมเดลโดยอัตโนมัติเมื่อใช้งานครั้งแรกหากยังไม่มีอยู่ในเครื่อง จากนั้นจึงโหลดโมเดลเพื่อใช้ในการอนุมาน

โมเดลนี้จะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของเซิร์ฟเวอร์ Lemonade เมื่อการดึงข้อมูลเสร็จสมบูรณ์ การตรวจสอบด้านล่างนี้จะยืนยันว่าโมเดลมีอยู่ในเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->