<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تهيئة المنصة

يصف هذا المستند تهيئات المنصة المتوقعة لتشغيل هذا الدليل التشغيلي.

## Windows

### تثبيت LM Studio

يجب أن يكون LM Studio مثبتًا مسبقًا:

| المكون | الإصدار | الموقع |
|-----------|---------|----------|
| **LM Studio (النماذج + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (البرنامج)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (ذاكرة التخزين المؤقت)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### تنزيل النموذج

يجب أن تكون النماذج التالية موجودة بالفعل في دليل نماذج LM Studio (`C:\Users\...\.lmstudio\models`):

| الجهاز | نوع النموذج | التكميم | الحجم (جيجابايت) | الموقع |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### تثبيت LM Studio

راجع [lmstudio.md](../../dependencies/lmstudio.md) لمزيد من التفاصيل.

### تنزيل النموذج

نفس الخطوات كما في Windows.