<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل Qwen3-Coder 30B A3B لـ Lemonade

يقوم خادم Lemonade بتقديم نموذج Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). لتنزيله مسبقًا:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

يقوم الأمر `lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` أيضًا بتنزيل النموذج عند أول استخدام إذا لم يكن موجودًا بالفعل، ثم يحمّله للاستدلال.

يظهر النموذج في قائمة النماذج التي تم تنزيلها في خادم Lemonade بمجرد اكتمال عملية السحب؛ وتؤكد الفحوصات أدناه وجوده على الجهاز.

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