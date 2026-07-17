<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. قم بتنزيل أحدث مثبّت ComfyUI لنظام Windows من [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. اختر إعداد الأجهزة الخاص بك: حدد `AMD ROCm`.
3. اختر مكان تثبيت ComfyUI: استخدم المسار الافتراضي أو المجلد المفضل لديك.
4. إعدادات تطبيق سطح المكتب: نوصي بإلغاء تحديد "التحديثات التلقائية" لضمان استخدامك للإصدار الموصى به من هذا التطبيق.
5. اضغط على "التالي" لبدء التثبيت.

<!-- @os:end -->

<!-- @os:linux -->
#### استنساخ ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (اختياري) الانتقال إلى إصدار محدد
```bash
git checkout v0.19.2
```

#### تثبيت متطلبات ComfyUI

مع تفعيل البيئة الافتراضية لـ Python، قم بتشغيل:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **ملاحظة**: راجع [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) لمزيد من المعلومات.

<!-- @os:end -->