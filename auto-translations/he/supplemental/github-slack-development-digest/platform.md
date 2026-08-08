<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להרצת ספר משחקים זה.

## אפליקציות/מסגרות עבודה נדרשות

### Windows/Linux

- יש להתקין את **Lemonade Server** בהתאם ל[מדריך ההתקנה של Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ואילך** וכן `npm`, המשמשים את ה-CLI של `agent-canvas` ואת שרתי ה-MCP המופעלים באמצעות `npx`.
- **uv**, מנהל חבילות ה-Python ש-Agent Canvas משתמש בו לניהול סביבת שרת הסוכן. יש להתקין אותו מ[מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).

## מודלים נדרשים

### Windows/Linux

המודל הבא חייב להיות זמין עבור Lemonade Server לפני התחלת ספר המשחקים.

| סוג מודל | מזהה מודל | הערות |
| --- | --- | --- |
| מודל צ'אט GGUF | `Qwen3.6-35B-A3B-GGUF` | מוגש על ידי Lemonade Server בכתובת `http://127.0.0.1:13305/api/v1`. יש להשתמש במודל GGUF קטן יותר במכשירים עם פחות מ-32 ג'יגה-בייט זיכרון. |

יש להפעיל את המודל באמצעות:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## פרטי גישה חיצוניים

ספר משחקים זה דורש:

- אסימון GitHub עם הרשאת קריאה למאגר המסוכם.
- אסימון בוט Slack עם הרשאות `chat:write` וקריאת ערוצים.
- מזהה צוות Slack ומזהה ערוץ Slack היעד.