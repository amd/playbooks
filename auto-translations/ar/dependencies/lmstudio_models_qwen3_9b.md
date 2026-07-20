<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل Qwen3.5 9B على LM Studio

لتنزيل نموذج Qwen3.5 9B:

1. اضغط على "Ctrl" + "Shift" + "M" على لوحة المفاتيح أو انقر على تبويب "Discover" (أيقونة العدسة المكبرة) في الشريط الجانبي الأيسر
2. ابحث عن `Qwen3.5 9B`
3. اختر مستوى التكميم (يُنصح باستخدام `Q4_K_M` لأنه يوفر توازناً جيداً بين الحجم والجودة) ثم انقر على تنزيل

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

سيقوم LM Studio تلقائياً بتنزيل النموذج ووضعه في الدليل الصحيح.

إذا رغبت في تنزيل نماذج إضافية، يمكنك البحث عنها في تبويب Discover وسيتولى LM Studio الباقي.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->