<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להרצת playbook זה.

## Windows

### התקנת LM Studio

יש להתקין מראש את LM Studio:

| רכיב | גרסה | מיקום |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### הורדת מודלים

המודלים הבאים אמורים להיות כבר קיימים בתיקיית המודלים של LM Studio (`C:\Users\...\.lmstudio\models`):

| סוג מודל | קוונטיזציה | גודל | מיקום |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### התקנת LM Studio

ראו lmstudio.md (בתוך תיקיית dependencies) למידע נוסף.

### הורדת מודלים

זהה ל-Windows.