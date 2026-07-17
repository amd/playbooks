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

| מכשיר | סוג מודל | כימות | גודל (GB) | מיקום |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### התקנת LM Studio

ראו [lmstudio.md](../../dependencies/lmstudio.md) לפרטים נוספים.

### הורדת מודל

זהה ל-Windows.