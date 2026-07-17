<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# تكوين المنصة

يصف هذا المستند تكوينات المنصة المتوقعة لتشغيل هذا الدليل التشغيلي.

## المتطلبات الأساسية

### Windows

| المكوّن | الإصدار | ملاحظات |
|-----------|---------|-------|
| **Node.js** | 22.16+ | مثبّت مسبقاً ومتاح في PATH على AMD Ryzen™ AI Halo Developer Platform؛ يجب تثبيته يدوياً على جميع الأجهزة الأخرى |
| **Lemonade Server** | الأحدث | يعمل على `http://localhost:13305/api/v1` |

### Linux

| المكوّن | الإصدار | ملاحظات |
|-----------|---------|-------|
| **Node.js** | 22.16+ | مثبّت مسبقاً ومتاح في PATH على AMD Ryzen™ AI Halo Developer Platform؛ يجب تثبيته يدوياً على جميع الأجهزة الأخرى |
| **Lemonade Server** | الأحدث | يعمل على `http://localhost:13305/api/v1` |


## Lemonade LLM

يجب أن يكون خادم Lemonade قيد التشغيل مع تحميل النموذج المناسب للجهاز (راجع ملف README للاطلاع على أمر `lemonade run` الخاص بجهازك):

| الجهاز | نقطة النهاية | النموذج |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |