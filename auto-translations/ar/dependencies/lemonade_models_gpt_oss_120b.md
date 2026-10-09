<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل GPT-OSS 120B لـ Lemonade

يقدّم خادم Lemonade نموذج GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). لتنزيله مسبقًا:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

يقوم الأمر `lemonade run gpt-oss-120b-mxfp-GGUF` أيضًا بتنزيل النموذج عند أول استخدام إذا لم يكن موجودًا بالفعل، ثم يُحمّله للاستدلال.

يظهر النموذج في قائمة النماذج المنزّلة في خادم Lemonade بمجرد اكتمال عملية السحب؛ تتحقق الفحوصات أدناه من وجوده على الجهاز.

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