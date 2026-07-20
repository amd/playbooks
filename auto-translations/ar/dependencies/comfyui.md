<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. حمّل أحدث برنامج تثبيت ComfyUI الخاص بويندوز من [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. اختر إعداد العتاد الخاص بك: حدد `AMD ROCm`.
3. اختر مكان تثبيت ComfyUI: استخدم المسار الافتراضي أو المجلد الذي تفضله.
4. إعدادات تطبيق سطح المكتب: نوصي بإلغاء تحديد "التحديثات التلقائية" لضمان استخدامك للإصدار الموصى به من هذا التطبيق.
5. اضغط "التالي" لبدء التثبيت.

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

مع تفعيل البيئة الافتراضية لبايثون، شغّل:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **ملاحظة**: راجع [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) لمزيد من المعلومات.

<!-- @os:end -->