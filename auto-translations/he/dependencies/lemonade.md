<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### התקנת Lemonade

<!-- @os:windows -->
הורידו את תוכנית ההתקנה העדכנית ביותר מ-[lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) והריצו את קובץ ה-`.msi`. 

לאחר ההתקנה:
- ה-CLI של `lemonade` מתווסף אוטומטית ל-PATH של המערכת
- שרת Lemonade אמור לרוץ ברקע באופן אוטומטי

ניתן גם להתקין באופן שקט משורת הפקודה:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

עבור הפצות אחרות או להתקנה מהמקור, ראו [אפשרויות ההתקנה המלאות](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### אימות התקנת Lemonade

פתחו מסוף והריצו:
```bash
lemonade --version
```

אמורה להופיע פלט כמו:
```
lemonade version x.y.z
```

אם אתם רואים מספר גרסה, סימן ש-Lemonade הותקן כראוי ומוכן לשימוש.

לעיון מהיר, הנה פקודות CLI נפוצות של Lemonade:

| פקודה | מה היא עושה |
| --- | --- |
| `lemonade --help` | מציגה את כל הפקודות והדגלים הזמינים. |
| `lemonade --version` | מדפיסה את גרסת Lemonade המותקנת. |
| `lemonade status` | מוודאת האם שרת Lemonade פועל ונגיש. כתובת הבסיס ברירת המחדל של ה-API התואם ל-OpenAI היא `http://localhost:13305/api/v1`. |
| `lemonade list` | מציגה רשימה של מודלים הזמינים להתקנת Lemonade שלכם. |
| `lemonade pull <MODEL_NAME>` | מורידה מודל מבלי להפעיל אותו. |
| `lemonade run <MODEL_NAME>` | מורידה את המודל במידת הצורך, ולאחר מכן מפעילה אותו להסקה/צ'אט. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | מפעילה מודל llama.cpp עם ה-backend של ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | מפעילה מודל llama.cpp עם ה-backend של Vulkan. |
| `lemonade config` | מציגה את ערכי התצורה הנוכחיים של Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | מגדירה את ה-backend ברירת המחדל של llama.cpp ל-ROCm. |

עבור אפשרויות שרת Lemonade העדכניות ביותר או פתרון בעיות, עיינו ב-[תיעוד הרשמי של Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).