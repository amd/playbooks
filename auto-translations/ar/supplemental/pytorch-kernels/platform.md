<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# تهيئة المنصة

يصف هذا المستند تهيئة المنصة المتوقعة لتشغيل هذا الدليل التطبيقي.

## التطبيقات / الأطر المطلوبة

| المكوّن | التهيئة المتوقعة | ملاحظات |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python | Python مع دعم `venv` | يُستخدم لإنشاء `kernel-env` وتفعيله |
| ROCm Python SDK | حزمة ROCm 7.13 | يتم تثبيتها من خلال تدفق تبعيات الدليل التطبيقي |
| PyTorch ROCm | PyTorch 2.11.0 + ROCm 7.13 | مطلوب لـ `torch.cuda` ووقت تشغيل HIP وتجميع JIT و `CUDAExtension` |
| GPU Driver | مشغّل AMD GPU مع دعم ROCm/HIP | مطلوب قبل أن يتمكن PyTorch من اكتشاف AMD GPU |

> ملاحظة: إذا كنت تعمل على AMD Ryzen™ AI Halo Developer Platform، فإن AMD ROCm™ وPyTorch مثبّتان مسبقاً.

## المتطلبات الأساسية لنظام Linux

حزم النظام التالية مطلوبة:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` مطلوب لإنشاء `kernel-env`.
* `build-essential` و`gcc` و`g++` مطلوبة لعروض امتداد C++.
* `amd-smi` يُستخدم لفحص رؤية GPU واستخدامه في Linux.

تقوم أمثلة امتداد C++ ببناء وحدات `.so` أصلية من ملفات `.cu` باستخدام مسار `CUDAExtension` الخاص بـ PyTorch.

## المتطلبات الأساسية لنظام Windows

يتطلب تشغيل Windows ما يلي:

* Python متاح من خلال `python`
* تثبيت الأحدث: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) أو [أحدث](https://visualstudio.microsoft.com/vs/community/) مع حزمة عمل **تطوير سطح المكتب باستخدام C++**

يجب أن توفر بيئة C++ الخاصة بـ Visual Studio:
* `vcvars64.bat`
* `cl.exe`
* مسارات تضمين ومكتبات Windows SDK

تقوم أمثلة امتداد C++ ببناء وحدات `.pyd` أصلية من ملفات `.cu` باستخدام مسار `CUDAExtension` الخاص بـ PyTorch.