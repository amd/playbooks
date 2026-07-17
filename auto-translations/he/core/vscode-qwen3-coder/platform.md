<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להפעלת ה-playbook הזה.

## Windows

### התקנת LM Studio

יש להתקין את LM Studio מראש:

| רכיב | גרסה | מיקום |
|-----------|---------|----------|
| **LM Studio (מודלים + שונות)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (תוכנית)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (מטמון)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### הורדת מודל

המודלים הבאים אמורים להיות קיימים כבר בתיקיית המודלים של LM Studio (`C:\Users\...\.lmstudio\models`):

| סוג מודל | כימות | גודל | מיקום |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### התקנת LM Studio

ראו את lmstudio.md (בתוך תיקיית התלויות) לפרטים נוספים.

### הורדת מודל

זהה ל-Windows.