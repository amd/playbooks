<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تنزيل GPT-OSS 120B على LM Studio

لتنزيل نموذج GPT-OSS 120B:

1. اضغط على "Ctrl" + "Shift" + "M" على لوحة المفاتيح أو انقر على تبويب "Discover" (أيقونة العدسة المكبرة) في الشريط الجانبي الأيسر
2. ابحث عن `ggml-org/gpt-oss-120b-GGUF`
3. اختر `mxfp4` وانقر على Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

سيقوم LM Studio تلقائيًا بتنزيل النموذج ووضعه في الدليل الصحيح.

إذا رغبت في تنزيل نماذج إضافية، يمكنك البحث عنها في تبويب Discover وسيتولى LM Studio الباقي.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->