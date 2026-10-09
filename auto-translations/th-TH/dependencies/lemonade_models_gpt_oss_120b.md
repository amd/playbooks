<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด GPT-OSS 120B สำหรับ Lemonade

เซิร์ฟเวอร์ Lemonade ให้บริการโมเดล GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`) หากต้องการดาวน์โหลดล่วงหน้า:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` จะดาวน์โหลดโมเดลโดยอัตโนมัติในการใช้งานครั้งแรกหากยังไม่มีอยู่ในเครื่อง จากนั้นจะโหลดโมเดลเพื่อใช้สำหรับการอนุมาน (inference)

โมเดลจะปรากฏในรายการโมเดลที่ดาวน์โหลดแล้วของเซิร์ฟเวอร์ Lemonade เมื่อการดึงข้อมูลเสร็จสมบูรณ์ โดยการตรวจสอบด้านล่างนี้จะยืนยันว่าโมเดลมีอยู่บนเครื่องแล้ว

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->