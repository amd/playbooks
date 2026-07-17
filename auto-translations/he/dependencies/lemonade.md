<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### התקנת Lemonade

<!-- @os:windows -->
הורד את המתקין העדכני מ-[lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) והפעל את קובץ ה-`.msi`.

לאחר ההתקנה:
- ה-CLI של `lemonade` מתווסף אוטומטית ל-PATH של המערכת
- שרת Lemonade אמור לפעול ברקע באופן אוטומטי

ניתן גם להתקין בשקט משורת הפקודה:
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

להפצות אחרות או להתקנה מקוד המקור, ראה את [אפשרויות ההתקנה המלאות](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### אימות התקנת Lemonade

פתח מסוף והפעל:
```bash
lemonade --version
```

אמור להופיע פלט כגון:
```
lemonade version x.y.z
```

אם מופיע מספר גרסה, Lemonade מותקן כראוי ומוכן לשימוש.

לעיון מהיר, להלן פקודות CLI נפוצות של Lemonade:

| פקודה | מה היא עושה |
| --- | --- |
| `lemonade --help` | מציג את כל הפקודות והדגלים הזמינים. |
| `lemonade --version` | מדפיס את גרסת Lemonade המותקנת. |
| `lemonade status` | מאשר האם שרת Lemonade פועל ונגיש. כתובת ה-API הבסיסית התואמת ל-OpenAI כברירת מחדל היא `http://localhost:13305/api/v1`. |
| `lemonade list` | מפרט את המודלים הזמינים להגדרת Lemonade שלך. |
| `lemonade pull <MODEL_NAME>` | מוריד מודל מבלי להפעיל אותו. |
| `lemonade run <MODEL_NAME>` | מוריד את המודל במידת הצורך, ולאחר מכן מפעיל אותו לצורך הסקה/שיחה. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | מפעיל מודל llama.cpp עם ה-backend של ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | מפעיל מודל llama.cpp עם ה-backend של Vulkan. |
| `lemonade config` | מציג את ערכי התצורה הנוכחיים של Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | מגדיר את ה-backend הברירת מחדל של llama.cpp ל-ROCm. |

לאפשרויות שרת Lemonade העדכניות ביותר או לפתרון בעיות, אנא עיין ב[תיעוד הרשמי של Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).