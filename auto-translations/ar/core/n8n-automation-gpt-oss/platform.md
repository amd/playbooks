<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تكوين المنصة

يصف هذا المستند تكوينات المنصة المتوقعة لتشغيل هذا الدليل الإرشادي.

## المتطلبات الأساسية

### Windows

| المكوّن | الإصدار | ملاحظات |
|-----------|---------|-------|
| **Node.js** | 22.16+ | مثبت مسبقًا ومتاح في PATH على منصة AMD Ryzen™ AI Halo Developer Platform؛ يجب تثبيته يدويًا على جميع الأجهزة الأخرى |
| **Lemonade Server** | latest | يعمل على `http://localhost:13305/api/v1` |

### Linux

| المكوّن | الإصدار | ملاحظات |
|-----------|---------|-------|
| **Node.js** | 22.16+ | مثبت مسبقًا ومتاح في PATH على منصة AMD Ryzen™ AI Halo Developer Platform؛ يجب تثبيته يدويًا على جميع الأجهزة الأخرى |
| **Lemonade Server** | latest | يعمل على `http://localhost:13305/api/v1` |


## نموذج Lemonade LLM

يجب أن يكون خادم Lemonade قيد التشغيل مع تحميل النموذج المناسب للجهاز (راجع ملف README الخاص بأمر `lemonade run` لجهازك):

| الجهاز | نقطة النهاية | النموذج |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |