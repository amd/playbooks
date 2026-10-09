<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل Qwen3-Coder 30B على LM Studio

لتنزيل نموذج Qwen3-Coder 30B:

1. اضغط على "Ctrl" + "Shift" + "M" على لوحة المفاتيح أو انقر على علامة التبويب "Discover" (أيقونة العدسة المكبرة) في الشريط الجانبي الأيسر
2. ابحث عن `Qwen3-Coder-30B-A3B`
3. اختر مستوى تكميم (يُنصح باستخدام `Q4_K_M` الذي يوفر توازنًا جيدًا بين الحجم والجودة) ثم انقر على Download

سيقوم LM Studio تلقائيًا بتنزيل النموذج ووضعه في الدليل الصحيح.

إذا رغبت في تنزيل نماذج إضافية، يمكنك البحث عنها في علامة التبويب Discover وسيتولى LM Studio الباقي.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->