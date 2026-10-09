<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### نماذج ومجموعات بيانات Hugging Face

يقوم دليل العمل هذا بتنزيل نماذج ومجموعات بيانات Hugging Face الخاصة به عند أول استخدام لها، ويحتفظ بها في ذاكرة التخزين المؤقت لـ Hugging Face (`~/.cache/huggingface/hub` ما لم يشر `HF_HOME` أو `HF_HUB_CACHE` إلى مكان آخر)، بحيث تبدأ عمليات التشغيل اللاحقة دون الحاجة إلى إعادة تنزيلها مرة أخرى.