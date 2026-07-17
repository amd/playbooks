<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להפעלת ה-playbook הזה.

## דרישות מוקדמות

### Windows

| רכיב | גרסה | הערות |
|-----------|---------|-------|
| **Node.js** | 22.16+ | מותקן מראש וזמין ב-PATH על פלטפורמת AMD Ryzen™ AI Halo Developer Platform; יש להתקין ידנית בכל שאר המכשירים |
| **Lemonade Server** | עדכנית | פועל על `http://localhost:13305/api/v1` |

### Linux

| רכיב | גרסה | הערות |
|-----------|---------|-------|
| **Node.js** | 22.16+ | מותקן מראש וזמין ב-PATH על פלטפורמת AMD Ryzen™ AI Halo Developer Platform; יש להתקין ידנית בכל שאר המכשירים |
| **Lemonade Server** | עדכנית | פועל על `http://localhost:13305/api/v1` |


## Lemonade LLM

שרת Lemonade אמור לפעול עם המודל המתאים למכשיר שנטען (ראה את ה-README לפקודת `lemonade run` עבור המכשיר שלך):

| מכשיר | נקודת קצה | מודל |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |