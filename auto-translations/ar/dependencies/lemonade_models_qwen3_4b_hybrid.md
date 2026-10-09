<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل Qwen3 4B Hybrid لأجل Lemonade

يقدّم خادم Lemonade نموذج Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`)، الذي يعمل على NPU وGPU في معالجات Ryzen AI. لتنزيله مسبقًا:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

يظهر النموذج في قائمة النماذج التي تم تنزيلها الخاصة بخادم Lemonade بمجرد اكتمال عملية السحب؛ يؤكد الفحص أدناه وجوده على الجهاز.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->