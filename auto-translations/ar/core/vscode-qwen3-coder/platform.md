<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **ترجمة آلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قبل مختص بشري. قد تحتوي على أخطاء، وقد تختلف بعض الخطوات أو الأوامر أو الروابط أو مدى توفر المنتج في لغتك أو منطقتك. إذا لاحظت وجود أي خطأ، يُرجى اعتماد نسخة الدليل الإرشادي (playbook) الأصلية باللغة الإنجليزية كمصدر موثوق.
<!-- auto-translated-disclaimer:end -->

# تكوين المنصة

يصف هذا المستند تكوينات المنصة المتوقعة لتشغيل هذا الدليل التشغيلي.

## Windows

### تثبيت LM Studio

يجب أن يكون LM Studio مثبتًا مسبقًا:

| المكون | الإصدار | الموقع |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### تنزيل النموذج

يجب أن تكون النماذج التالية موجودة بالفعل في دليل نماذج LM Studio (`C:\Users\...\.lmstudio\models`):

| نوع النموذج | التكميم | الحجم | الموقع |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### تثبيت LM Studio

راجع lmstudio.md (داخل مجلد dependencies) لمزيد من التفاصيل.

### تنزيل النموذج

نفس الإجراء المتبع في Windows.