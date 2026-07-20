<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# تكوين المنصة

يصف هذا المستند تكوينات المنصة المتوقعة لتشغيل دليل الإرشادات هذا.

## التطبيقات/الأطر المطلوبة

### Windows/Linux

يجب تثبيت GAIA مسبقًا باستخدام التعليمات الواردة في [دليل تثبيت GAIA](../../dependencies/gaia.md).

يجب تثبيت Lemonade Server مسبقًا باستخدام التعليمات الواردة في [دليل تثبيت Lemonade](../../dependencies/lemonade.md).

## النماذج المطلوبة

### Windows/Linux

يستخدم Hardware Advisor Agent نموذج **Qwen3-Coder-30B** للاستدلال الخاص بالوكيل. يتم تنزيل هذا النموذج تلقائيًا أثناء `gaia init`. لا حاجة لتنزيل أي نماذج يدويًا.