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

## דרישות מוקדמות

### Windows

| רכיב | גרסה | הערות |
|-----------|---------|-------|
| **Node.js** | 22.16+ | מותקן מראש וזמין ב-PATH ב-AMD Ryzen™ AI Halo Developer Platform; יש להתקין ידנית בכל שאר המכשירים |
| **Lemonade Server** | הגרסה העדכנית ביותר | פועל בכתובת `http://localhost:13305/api/v1` |

### Linux

| רכיב | גרסה | הערות |
|-----------|---------|-------|
| **Node.js** | 22.16+ | מותקן מראש וזמין ב-PATH ב-AMD Ryzen™ AI Halo Developer Platform; יש להתקין ידנית בכל שאר המכשירים |
| **Lemonade Server** | הגרסה העדכנית ביותר | פועל בכתובת `http://localhost:13305/api/v1` |


## Lemonade LLM

שרת Lemonade צריך לפעול עם המודל המתאים למכשיר טעון (ראו את קובץ ה-README לפקודת `lemonade run` המתאימה למכשיר שלכם):

| מכשיר | נקודת קצה | מודל |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |