<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تكوين المنصة

يصف هذا المستند تكوين المنصة المتوقع لتشغيل هذا الدليل الإرشادي (playbook).

## التطبيقات / الأطر المطلوبة

| المكوّن       | التكوين المتوقع               | ملاحظات                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python مع دعم `venv`         | يُستخدم لإنشاء وتفعيل `kernel-env`                                     |
| ROCm Python SDK | مجموعة حزم ROCm 7.13             | يتم تثبيته من خلال تدفق تبعيات الدليل الإرشادي                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | مطلوب لـ `torch.cuda`، وبيئة تشغيل HIP، والتجميع الفوري (JIT)، وامتداد `CUDAExtension` |
| مُشغّل GPU      | مُشغّل AMD GPU يدعم ROCm/HIP | مطلوب قبل أن يتمكن PyTorch من اكتشاف AMD GPU                               |

> ملاحظة: إذا كنت تعمل على منصة AMD Ryzen™ AI Halo Developer Platform، فإن برنامج AMD ROCm™ و PyTorch مثبّتان مسبقًا.

## متطلبات Linux الأساسية

الحزم النظامية التالية مطلوبة:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` مطلوب لإنشاء `kernel-env`.
* `build-essential` و `gcc` و `g++` مطلوبة لشروحات امتدادات C++.
* يُستخدم `amd-smi` للتحقق من رؤية/استخدام GPU على Linux.

تقوم أمثلة امتدادات C++ ببناء وحدات `.so` أصلية من ملفات `.cu` باستخدام مسار `CUDAExtension` الخاص بـ PyTorch.

## متطلبات Windows الأساسية

تتطلب أجهزة تشغيل Windows ما يلي:

* توفر Python من خلال `python`
* تثبيت أحدث إصدار من: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) أو [إصدار أحدث](https://visualstudio.microsoft.com/vs/community/) مع حزمة عمل **Desktop development with C++**

يجب أن توفر بيئة Visual Studio C++ ما يلي:
* `vcvars64.bat`
* `cl.exe`
* مسارات ملفات التضمين والمكتبات الخاصة بـ Windows SDK

تقوم أمثلة امتدادات C++ ببناء وحدات `.pyd` أصلية من ملفات `.cu` باستخدام مسار `CUDAExtension` الخاص بـ PyTorch.