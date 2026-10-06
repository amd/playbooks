<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل GPT-OSS 20B لـ Lemonade

يقدّم خادم Lemonade نموذج GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). لتنزيله مسبقًا:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

يقوم الأمر `lemonade run gpt-oss-20b-mxfp4-GGUF` أيضًا بتنزيل النموذج عند أول استخدام إذا لم يكن موجودًا مسبقًا، ثم يحمّله للاستدلال.

يظهر النموذج في قائمة النماذج التي تم تنزيلها الخاصة بخادم Lemonade بمجرد اكتمال عملية السحب؛ تؤكد عمليات التحقق أدناه وجوده على الجهاز.

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