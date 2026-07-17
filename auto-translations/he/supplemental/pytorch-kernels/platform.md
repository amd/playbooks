<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה

מסמך זה מתאר את תצורת הפלטפורמה הנדרשת להפעלת ה-playbook הזה.

## אפליקציות / מסגרות נדרשות

| רכיב            | תצורה צפויה                          | הערות                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python עם תמיכה ב-`venv`           | משמש ליצירה והפעלה של `kernel-env`                                           |
| ROCm Python SDK | משפחת חבילות ROCm 7.13              | מותקן דרך זרימת התלויות של ה-playbook                                        |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | נדרש עבור `torch.cuda`, סביבת HIP, קומפילציית JIT, ו-`CUDAExtension`        |
| GPU Driver      | מנהל התקן GPU של AMD עם תמיכה ב-ROCm/HIP | נדרש לפני ש-PyTorch יכול לזהות את ה-GPU של AMD                         |

> הערה: אם אתם מריצים על AMD Ryzen™ AI Halo Developer Platform, תוכנת AMD ROCm™ ו-PyTorch מותקנות מראש.

## דרישות מוקדמות ל-Linux

חבילות המערכת הבאות נדרשות:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` נדרש ליצירת `kernel-env`.
* `build-essential`, `gcc`, ו-`g++` נדרשים לתרגילי ההדרכה של הרחבת C++.
* `amd-smi` משמש לבדיקות נראות/ניצול GPU ב-Linux.

דוגמאות הרחבת C++ בונות מודולי `.so` מקוריים מקבצי `.cu` באמצעות נתיב `CUDAExtension` של PyTorch.

## דרישות מוקדמות ל-Windows

מריצי Windows דורשים:

* Python זמין דרך `python`
* התקינו את הגרסה העדכנית ביותר: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) או [גרסה חדשה יותר](https://visualstudio.microsoft.com/vs/community/) עם עומס העבודה **Desktop development with C++**

סביבת C++ של Visual Studio חייבת לספק:
* `vcvars64.bat`
* `cl.exe`
* נתיבי כלילה וספריות של Windows SDK

דוגמאות הרחבת C++ בונות מודולי `.pyd` מקוריים מקבצי `.cu` באמצעות נתיב `CUDAExtension` של PyTorch.