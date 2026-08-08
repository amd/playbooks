<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להרצת מדריך זה.

## Windows

### התקנת LM Studio

יש להתקין מראש את LM Studio:

| רכיב | גרסה | מיקום |
|-----------|---------|----------|
| **LM Studio (מודלים + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (תוכנית)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (מטמון)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### הורדת מודל

המודלים הבאים אמורים להיות כבר קיימים בספריית המודלים של LM Studio (`C:\Users\...\.lmstudio\models`):

| מכשיר | סוג מודל | קוונטיזציה | גודל (GB) | מיקום |
| ----- |------------|--------------|------|----------|
| פלטפורמת המפתחים AMD Ryzen™ AI Halo <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### התקנת LM Studio

ראה [lmstudio.md](../../dependencies/lmstudio.md) לפרטים נוספים.

### הורדת מודל

זהה ל-Windows.