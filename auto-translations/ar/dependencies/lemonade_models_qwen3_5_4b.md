<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل Qwen3.5 4B لـ Lemonade

يقدّم خادم Lemonade النموذج Qwen3.5 4B (`Qwen3.5-4B-GGUF`). لتنزيله مسبقًا:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

يقوم الأمر `lemonade run Qwen3.5-4B-GGUF` أيضًا بتنزيل النموذج عند أول استخدام إذا لم يكن موجودًا بالفعل، ثم يحمّله من أجل الاستدلال.

يظهر النموذج في قائمة النماذج المُنزَّلة في خادم Lemonade بمجرد اكتمال عملية السحب؛ وتؤكد الفحوصات أدناه وجوده على الجهاز.

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