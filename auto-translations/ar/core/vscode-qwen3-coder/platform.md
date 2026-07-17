<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# تهيئة المنصة

يصف هذا المستند تهيئات المنصة المتوقعة لتشغيل هذا الدليل التشغيلي.

## Windows

### تثبيت LM Studio

يجب أن يكون LM Studio مثبتاً مسبقاً:

| المكوّن | الإصدار | الموقع |
|-----------|---------|----------|
| **LM Studio (النماذج والمتنوعات)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (البرنامج)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (الذاكرة المؤقتة)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### تنزيل النماذج

يجب أن تكون النماذج التالية موجودة مسبقاً في مجلد نماذج LM Studio (`C:\Users\...\.lmstudio\models`):

| نوع النموذج | التكميم | الحجم | الموقع |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### تثبيت LM Studio

راجع ملف lmstudio.md (داخل مجلد التبعيات) لمزيد من التفاصيل.

### تنزيل النماذج

نفس الأمر كما هو على Windows.