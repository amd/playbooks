<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# תצורת פלטפורמה

מסמך זה מתאר את תצורת הפלטפורמה הצפויה להרצת ספר משחקים (playbook) זה.

## אפליקציות / מסגרות עבודה נדרשות

| רכיב            | תצורה צפויה                          | הערות                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python עם תמיכה ב-`venv`             | משמש ליצירה והפעלה של `kernel-env`                                            |
| ROCm Python SDK | משפחת חבילות ROCm 7.13                | מותקן דרך תהליך התלויות של ספר המשחקים                                       |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13            | נדרש עבור `torch.cuda`, סביבת ריצה של HIP, קומפילציית JIT, ו-`CUDAExtension`  |
| מנהל התקן GPU   | מנהל התקן AMD GPU עם תמיכה ב-ROCm/HIP | נדרש לפני ש-PyTorch יוכל לזהות את ה-AMD GPU                                   |

> הערה: אם אתה מריץ על AMD Ryzen™ AI Halo Developer Platform, תוכנת AMD ROCm™ ו-PyTorch מותקנות מראש.

## דרישות מוקדמות עבור Linux

חבילות המערכת הבאות נדרשות:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` נדרש ליצירת `kernel-env`.
* `build-essential`, `gcc`, ו-`g++` נדרשים עבור המדריכים להרחבות C++.
* `amd-smi` משמש לבדיקות נראות/ניצולת GPU ב-Linux.

הדוגמאות להרחבות C++ בונות מודולי `.so` מקוריים מקבצי `.cu` באמצעות נתיב ה-`CUDAExtension` של PyTorch.

## דרישות מוקדמות עבור Windows

מריצי Windows דורשים:

* Python זמין דרך `python`
* התקן את הגרסה האחרונה: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) או [חדש יותר](https://visualstudio.microsoft.com/vs/community/) עם עומס העבודה **Desktop development with C++**

סביבת ה-C++ של Visual Studio חייבת לספק:
* `vcvars64.bat`
* `cl.exe`
* נתיבי include וספרייה של Windows SDK

הדוגמאות להרחבות C++ בונות מודולי `.pyd` מקוריים מקבצי `.cu` באמצעות נתיב ה-`CUDAExtension` של PyTorch.