<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل SDXL-Turbo لـ Lemonade

يقدّم خادم Lemonade نموذج SDXL-Turbo (`SDXL-Turbo`). لتنزيله مسبقًا:

```bash
lemonade pull SDXL-Turbo
```

يقوم الأمر `lemonade run SDXL-Turbo` أيضًا بتنزيل النموذج عند أول استخدام إذا لم يكن موجودًا بالفعل، ثم يحمّله لأغراض الاستدلال.

يظهر النموذج في قائمة النماذج التي تم تنزيلها الخاصة بخادم Lemonade بمجرد اكتمال عملية السحب؛ وتؤكد عمليات التحقق أدناه أنه موجود على الجهاز.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->