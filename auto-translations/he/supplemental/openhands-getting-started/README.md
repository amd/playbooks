<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## סקירה כללית

[OpenHands](https://github.com/All-Hands-AI/OpenHands) הוא סוכן תוכנה מבוסס בינה מלאכותית
שיכול לכתוב קוד, להריץ פקודות, לגלוש באינטרנט ולערוך קבצים בסביבת עבודה
אמיתית. במקום להעתיק הצעות מחלון צ'אט, אתם מכוונים את
הסוכן לתיקיית פרויקט ונותנים לו לבצע את העבודה: להטמיע תכונה, לתקן
באג, לכתוב בדיקות, או להסביר בסיס קוד.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא ממשק הדפדפן
המומלץ להרצת OpenHands. פקודת `agent-canvas` יחידה מפעילה
את שרת הסוכן, מנוע האוטומציה, וממשק המשתמש באינטרנט יחד, כך שתוכלו
לנהל שיחה עם הסוכן מהדפדפן שלכם.

כדי לשמור הכל על מערכת ה-AMD שלכם, הסוכן משוחח עם מודל מקומי המוגש
על ידי Lemonade Server. Lemonade חושף את המודל הזה דרך API
תואם OpenAI, כך ש-Agent Canvas יכול להגדיר אותו כמו כל נקודת קצה בסגנון OpenAI אחרת
בעוד המודל, הקוד שלכם, וקונטקסט השיחה נשארים כולם על
המחשב שלכם.

בספר משחקים זה, תתחילו מודל מקומי, תפעילו את Agent Canvas, תכוונו אותו
למודל הזה, ותריצו את משימת הקוד הראשונה שלכם על תיקיית פרויקט אמיתית.

## מה תלמדו

- כיצד להפעיל את Lemonade Server ולאשר שמודל מקומי עונה לבקשות צ'אט
- כיצד להתקין ולהפעיל את Agent Canvas מחבילת ה-npm
- כיצד להגדיר את Agent Canvas להשתמש במודל Lemonade מקומי כ-LLM
- כיצד להתחיל שיחת OpenHands ולצפות בסוכן עורך קבצים ומריץ
  פקודות בסביבת עבודה
- כיצד לבחון מה הסוכן שינה ולכוון אותו עם הודעות המשך

## מושגי ליבה

| מושג | מהו | היכן הוא משתלב בספר משחקים זה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת שירות LLM מקומית שנבנתה עבור חומרת AMD החושפת API תואם OpenAI. הנתונים שלכם לעולם לא עוזבים את המחשב שלכם. | מריצה את המודל שמניע את הסוכן. |
| OpenHands | סוכן תוכנה מבוסס בינה מלאכותית הקורא ועורך קבצים, מריץ פקודות מעטפת, וגולש באינטרנט בתוך סביבת עבודה. | הסוכן שאתם מנהלים מהצ'אט. |
| Agent Canvas | ממשק הדפדפן והמנוע העורפי המריצים שיחות OpenHands ומציגים קריאות כלים ושינויי קבצים. | מפעיל את המערך ומארח את השיחה שלכם. |
| סביבת עבודה | תיקיית הפרויקט שהסוכן רשאי לקרוא ולשנות. | היעד של העריכות והפקודות של הסוכן. |

<!-- @device:stx,krk -->
> [!NOTE]
> תהליכי עבודה של סוכני קוד נהנים ממודל וחלון הקשר גדולים יותר. השתמשו ב-
> לפחות 32 ג'יגה-בייט זיכרון מערכת, ועדיפו 64 ג'יגה-בייט או יותר עבור מודלי GGUF גדולים יותר.
<!-- @device:end -->

## דרישות מוקדמות

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

אתם זקוקים ל:

- Lemonade Server מותקן ומסוגל להגיש את המודל שלהלן.
- Node.js גרסה 22.12 ומעלה ו-`npm` (בשימוש על ידי כלי השורת הפקודה `agent-canvas`).
- `uv`, מנהל חבילות ה-Python שבו משתמש Agent Canvas לניהול סביבת
  שרת הסוכן. אם במערכת שלכם עדיין אין אותו, התקינו אותו מתוך
  [מדריך התקנת uv](https://docs.astral.sh/uv/getting-started/installation/)
  לפני הפעלת Agent Canvas.
- תיקיית פרויקט לעבודה. זה יכול להיות כל מאגר git מקומי או תיקיית
  קוד שתרצו שהסוכן יעבוד עליה.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. הפעלת Lemonade Server

הפעילו את המודל משורת הפקודה של Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade חושף API תואם OpenAI בכתובת:

```text
http://127.0.0.1:13305/api/v1
```



## 2. אימות המודל המקומי

ודאו ש-Lemonade יכול להגיש את המודל הנבחר:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

לאחר מכן שלחו בקשת צ'אט קטנה:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

אם זה מחזיר מערך `choices`, Lemonade מוכן עבור Agent Canvas.

## 3. התקנה והפעלה של Agent Canvas

התקינו את חבילת Agent Canvas המפורסמת באופן גלובלי:

```bash
npm install -g @openhands/agent-canvas
```

לאחר מכן הפעילו את המערך המלא ממסוף:

```bash
agent-canvas
```

כברירת מחדל, Agent Canvas מופעל בכתובת `http://localhost:8000`. פתחו כתובת זו ב-
דפדפן שלכם. אם הפורט 8000 כבר בשימוש, העבירו `--port` (או `-p`) בעת
הפעלת Agent Canvas:

```bash
agent-canvas --port 3000
```

אותה פקודה עובדת ב-PowerShell תחת Windows. לאחר מכן פתחו את
`http://localhost:3000` במקום זאת. הבקאנד המקומי כברירת מחדל אמור להופיע
כתקין במסך הבית.

הפקודה `agent-canvas` מפעילה את שרת הסוכן, מנוע האוטומציה, ואת
ממשק המשתמש באינטרנט יחד. אתם זקוקים רק לפקודה אחת זו כדי להריץ את OpenHands
מקומית.

## 4. הגדרת ה-LLM המקומי

בהפעלה ראשונה, Agent Canvas פותח תהליך היכרות. בתהליך זה:

1. השאירו את **OpenHands** נבחר כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר ל-**API key**.
4. הגדירו את **Custom Model** ל-`openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** ל-`http://127.0.0.1:13305/api/v1`.
6. עבור **API Key**, הזינו כל ערך placeholder שאינו ריק כגון `lemonade-local`.
   Lemonade אינו דורש מפתח אמיתי, אך לקוח OpenHands זקוק לערך
   כדי לשלוח.
7. לחצו על **Next**.

הגדרות ה-Advanced המושלמות אמורות להיראות כך. שדה מפתח ה-API
מוסתר על ידי הממשק.

![הגדרות Advanced של LLM בשימוש ראשון של Agent Canvas עם מודל Lemonade וכתובת URL בסיס מקומית](assets/01-llm-advanced-settings.png)

Agent Canvas שומר ערכים אלה כפרופיל LLM. אם הגרסה שלכם מבקשת ממכם
לתת שם לפרופיל זה, השתמשו בשם ללא רווחים כגון `lemonade-local`. אם תשנו
מודלים בהמשך, פתחו **Settings > LLM** ועדכנו את אותם שדות Advanced. אתם
יכולים לעבור בין פרופילים שמורים משדה הקלט של הצ'אט עם הפקודה `/model`.

## 5. פתיחת סביבת עבודה

הסוכן יכול רק לקרוא ולשנות קבצים בתוך סביבת עבודה שאתם בוחרים. לפני
תחילת משימה, כוונו את Agent Canvas לתיקיית הפרויקט שלכם:

1. ממסך הבית, בחרו **Open Workspace**.
2. בחרו את התיקייה המכילה את הפרויקט שלכם (לדוגמה, מאגר git
   שתרצו שהסוכן יעבוד עליו).
3. התחילו שיחה חדשה בסביבת עבודה זו.

כל מה שהסוכן עושה—קריאת קבצים, הרצת פקודות, עריכת קוד—מוגבל
לסביבת העבודה הזו.

![מסך הבית של Agent Canvas לאחר תהליך ההיכרות](assets/02-agent-canvas-home.png)
## 6. הרץ את משימת התכנות הראשונה שלך

לאחר שסביבת העבודה פתוחה וה-LLM המקומי נבחר, הקלד משימה קונקרטית בצ'אט. משימה ראשונה טובה היא קטנה וניתנת לאימות, לדוגמה:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

עקוב אחר ציר הזמן של השיחה. OpenHands יבצע את הפעולות הבאות:

- קריאת סביבת העבודה כדי להבין את המבנה שלה.
- יצירת `hello.py` עם הפונקציה המבוקשת ובלוק הבדיקה.
- הרצה אופציונלית של `python3 hello.py` כדי לאמת את הפלט.
- דיווח על מה שבוצע ועל כל פלט של פקודות בצ'אט.

אתה אמור לראות את הקובץ החדש מופיע בסביבת העבודה, וההודעה הסופית של הסוכן אמורה לתאר את השינוי שביצע. זהו רגע התוצאה: הסוכן כתב והריץ קוד אמיתי בתיקיית הפרויקט שלך.

## 7. סקור והנחה את הסוכן

לאחר שהסוכן מסיים שלב, סקור את עבודתו לפני שתאשר את השלב הבא:

- **שינויי קבצים**: השתמש בדפדפן הקבצים של סביבת העבודה או בתצוגת ה-diff של הסוכן כדי לראות בדיוק מה נוסף, שונה או נמחק.
- **פלט פקודות**: הרחב כל פקודה שהסוכן הריץ כדי לראות את ה-stdout, ה-stderr וקוד היציאה.
- **המשך פעולות**: אם התוצאה אינה מה שרצית, השב באותה שיחה עם תיקון. הסוכן שומר את ההקשר הקודם וממשיך לעבוד על אותם קבצים.

לדוגמה, אם הבדיקה לא הדפיסה את ברכת השלום המצופה, השב:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

הסוכן יקרא מחדש את הקובץ, יריץ את הפקודה, יאבחן את הבעיה, ויערוך את הקובץ שוב—הכל באותה שיחה.

## פתרון בעיות

- **`agent-canvas` אינו נמצא ב-PATH:** התקן מחדש עם
  `npm install -g @openhands/agent-canvas` וודא שספריית הבינארי הגלובלי של npm
  נמצאת ב-PATH שלך. ב-Windows, הרץ `npm config get prefix`; הספרייה
  המוחזרת, לרוב `%APPDATA%\npm` או `%USERPROFILE%\.npm-global`,
  חייבת להיות ב-PATH של המשתמש שלך לפני ש-`agent-canvas` יוכל להיות מופעל מטרמינל חדש.
- **`npm install -g` נכשל עם שגיאת הרשאות:** הגדר ספריית npm גלובלית בבעלות המשתמש,
  ואז פתח מחדש את הטרמינל והתקן שוב את Agent Canvas.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  כדי להפוך את שינוי ה-PATH ב-Windows לקבוע, הוסף את `%USERPROFILE%\.npm-global` ל-PATH
  של המשתמש שלך דרך **Settings > System > About > Advanced system settings >
  Environment Variables**, ופתח טרמינל חדש.
  <!-- @os:end -->
- **הממשק נטען אך ה-backend מוצג כלא תקין:** המתן מספר שניות עד ששרת הסוכן
  יסיים להיטען, ולאחר מכן רענן. אם הוא נשאר לא תקין, הפעל מחדש את
  `agent-canvas` ובדוק את פלט הטרמינל לאיתור שגיאות.
- **בקשות צ'אט של Lemonade נכשלות עם שגיאת חיבור:** ודא ש-
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` מצליחה וש-
  Lemonade עדיין מגיש את המודל באמצעות `lemonade status`.
- **הסוכן מציג שגיאה של אורך הקשר או מגבלת טוקנים:** הפעל מחדש את
  Lemonade עם `ctx_size` גדול יותר (לדוגמה `ctx_size=65536`), והתחל
  שיחה חדשה כך שהסוכן לא ישא היסטוריה גדולה מדי.
- **הסוכן מפיק עריכות באיכות נמוכה או לא שלמות:** עבור למודל גדול יותר
  ב-Lemonade, או תן לסוכן משימה קטנה וקונקרטית יותר ותן לו לסיים לפני
  שתבקש את השינוי הבא.
- **`uv` חסר:** התקן אותו מ-
  [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas משתמש ב-`uv` כדי לנהל את סביבת ה-Python של שרת הסוכן.

## הצעדים הבאים

- נסה משימה גדולה יותר באותה סביבת עבודה, כגון הוספת קובץ בדיקת יחידה או
  תיקון באג ידוע, וסקור את ה-diff של הסוכן לפני שאתה שומר את השינוי.
- חבר שרת MCP כגון GitHub או Slack תחת **Customize** כך שהסוכן
  יוכל לקרוא issues או לפרסם עדכונים תוך כדי עבודה.
- שמור מספר פרופילי LLM (מודל קטן ומהיר ומודל גדול וחזק יותר) ועבור
  ביניהם עם `/model` באמצע השיחה.
- המשך אל [אוטומציות של OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) כדי
  להפוך לולאות פיתוח חוזרות להרצות סוכן מתוזמנות או מופעלות על ידי אירועים.

## משאבים

- [תיעוד OpenHands](https://docs.openhands.dev/)
- [סקירה כללית של Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [הגדרת Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [פרופילי LLM והגדרת מודלים](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [תיעוד Lemonade Server](https://lemonade-server.ai/docs)