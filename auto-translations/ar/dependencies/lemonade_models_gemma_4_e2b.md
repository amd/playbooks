<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل Gemma-4 E2B لـ Lemonade

يقدم خادم Lemonade نموذج Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). لتنزيله مسبقًا:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

يقوم الأمر `lemonade run Gemma-4-E2B-it-GGUF` أيضًا بتنزيل النموذج عند أول استخدام إذا لم يكن موجودًا بالفعل، ثم يقوم بتحميله للاستدلال.

يظهر النموذج في قائمة النماذج المُنزَّلة في خادم Lemonade بمجرد اكتمال عملية السحب؛ وتؤكد الفحوصات أدناه وجوده على الجهاز.

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