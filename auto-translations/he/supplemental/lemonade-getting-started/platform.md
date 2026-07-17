<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה — Lemonade Local AI

מסמך זה מתאר את התוכנות המותקנות מראש, נתיבי המודלים, ודרישות הפלטפורמה הספציפיות שהפלייבוק הזה מניח.

## תוכנות מותקנות מראש

| תוכנה | גרסה | מטרה |
|----------|---------|---------|
| Lemonade Server | מהדורה אחרונה | שרת LLM מקומי עם API תואם OpenAI |
| Python | 3.10–3.13 | נדרש לדוגמת לקוח Python של OpenAI |

## אחסון מודלים כברירת מחדל

מודלים שהורדו דרך Lemonade מאוחסנים לפי מפרט Hugging Face Hub:

| פלטפורמה | נתיב ברירת מחדל |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

כדי לשנות את מיקום האחסון, הגדר את משתנה הסביבה `HF_HOME`.

## דרישות חומרה

| יעד חומרה | דרישות |
|----------------|-------------|
| **CPU** | כל מעבד x86-64 מודרני (AMD או Intel) |
| **GPU (Vulkan)** | כל GPU עם תמיכה במנהל התקן Vulkan |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series או Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | מעבד AMD Ryzen AI 300 series, Windows 11 |

## דרישות רשת

- נדרש חיבור לאינטרנט להורדה ראשונית של המודל (1–25 GB בהתאם למודל)
- אין צורך באינטרנט לאחר הורדת המודלים