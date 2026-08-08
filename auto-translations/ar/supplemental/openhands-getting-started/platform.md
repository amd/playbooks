<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تهيئة المنصة

يصف هذا المستند تهيئات المنصة المتوقعة لتشغيل دليل التشغيل هذا.

## التطبيقات/أطر العمل المطلوبة

### Windows/Linux

- يجب تثبيت **Lemonade Server** باتباع
  [دليل تثبيت Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 أو أحدث** و`npm`، المستخدمان بواسطة أداة سطر الأوامر `agent-canvas`.
- **uv**، مدير حزم Python الذي يستخدمه Agent Canvas لإدارة
  بيئة خادم الوكيل. ثبّته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).

## النماذج المطلوبة

### Windows/Linux

يجب أن يكون النموذج التالي متاحًا لـ Lemonade Server قبل بدء
دليل التشغيل.

| نوع النموذج | معرّف النموذج | ملاحظات |
| --- | --- | --- |
| نموذج محادثة GGUF | `Qwen3.6-35B-A3B-GGUF` | يُقدَّم بواسطة Lemonade Server على `http://127.0.0.1:13305/api/v1`. استخدم نموذج GGUF أصغر على الأجهزة التي تحتوي على أقل من 32 جيجابايت من الذاكرة. |

ابدأ تشغيل النموذج باستخدام:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
