<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# تهيئة المنصة

يصف هذا المستند تهيئة المنصة المتوقعة لتشغيل هذا الدليل التطبيقي.

## التطبيقات/الأطر المطلوبة

### Windows/Linux
يجب تثبيت Lemonade مسبقاً من [هنا](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (تطبيق الويب للواجهة الأمامية)
- **Lemonade Server** (خادم النماذج الخلفي)

> يُشغّل هذا الدليل التطبيقي **Lemonade** (خادم/تطبيق Lemonade) **بشكل أصلي**. يعمل **Open WebUI** كـ **حاوية** على Linux (عبر Podman) وكـ **حزمة Python** على Windows. تدعم حزمة `open-webui` في PyPI إصدار Python ≤ 3.12 فقط، لذا تتجنب حاوية Linux الحاجة إلى إدارة إصدارات Python الأقدم.

## النماذج (في Lemonade)

يجب تنزيل النماذج داخل **تطبيق Lemonade** (باستخدام مدير النماذج المدمج) أو عبر أوامر إدارة النماذج في Lemonade (`lemonade pull <model_name>`). يفترض هذا الدليل التطبيقي أن النماذج الموصى بها أدناه قد تم تنزيلها وتظهر في نقطة نهاية قائمة النماذج.

التحقق من توفر النماذج:
- افتح: `http://localhost:13305/api/v1/models`
- ستُدرج النماذج المنزّلة تحت `"data"`.

### النماذج الموصى بها

| القدرة | معرّف النموذج | ملاحظات |
|---|----|-----|
| LLM (إدخال نص ← إخراج نص) | `Qwen3-4B-Hybrid` (أو ما شابهه) | أي نموذج LLM في Lemonade للمحادثة أو إكمال النص أو البرمجة أو الاستدلال |
| VLM (صورة ← نص) | `Qwen3.5-4B-GGUF` (أو أي نموذج في فئة **Vision**) | أي نموذج متعدد الوسائط/قادر على الرؤية يمكنه قبول الصور كجزء من مدخلاته |
| توليد الصور (نص ← صورة) | `SDXL-Turbo` (أو أي نموذج في فئة **Image**) | أي نموذج Stable Diffusion يولّد صوراً من موجّه نصي |
| الصوت (كلام ← نص) | `Whisper-Large-v3` (أو أي نموذج في فئة **Audio**) | أي نموذج ASR يحوّل الصوت إلى نص |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## المنافذ المستخدمة

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

إذا كانت هذه المنافذ مستخدمة بالفعل على نظامك، فقم بتغييرها عند تشغيل الخادم (الخوادم).