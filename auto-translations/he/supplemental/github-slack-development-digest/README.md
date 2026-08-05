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

מפתחים מבלים זמן רב בלולאות חוזרות וקטנות: סקירת בקשות משיכה (pull requests) מתויגות, מענה על תגובות ב-GitHub, מיון בעיות (issues) חדשות, הפיכת שרשורי Slack להערות עמידה יומית (standup) או למעקבי אירועים, ומעקב אחר אותות שחרור (release) או מחקר. כל לולאה מוכרת, אך היא עדיין דורשת שיקול דעת: לאסוף את ההקשר הנכון, להחליט מה חשוב, ולפרסם עדכון ברור במקום שבו הצוות כבר עובד.

[אוטומציות של OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
הופכות את הלולאות הללו לשיחות סוכן מתוזמנות או מופעלות על ידי אירועים: הרצות שבהן סוכן תוכנה מבוסס AI יכול לקרוא הקשר, לקרוא לכלים, ולהפיק עדכון. תבניות האוטומציה המשותפות בקטלוג ההרחבות של OpenHands עוקבות אחר דפוס זה עבור סקירת בקשות משיכה ב-GitHub, ניטור מאגרים, מיון בעיות ב-Linear, ניתוחי תקריות (retrospectives), תקצירי עמידה יומית ב-Slack, ותקצירי מחקר: אוטומציה מתעוררת, משתמשת באינטגרציות מוגדרות כגון GitHub או Slack כדי להביא הקשר, מנמקת על ההקשר הזה באמצעות מודל שפה גדול (LLM), וכותבת חזרה תוצאה.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא מישור הבקרה המקומי לבניה ובדיקה של האוטומציות הללו. במדריך זה הוא מריץ OpenHands Agent Server, תהליך הרקע שמבצע שיחות סוכן, ומחבר את הסוכן לשירותים חיצוניים כגון GitHub ו-Slack.

כדי לשמור על זרימת העבודה במערכת ה-AMD שלכם, הסוכן משוחח עם מודל מקומי המוגש על ידי Lemonade Server. Lemonade חושף את המודל הזה דרך API תואם-OpenAI, כך ש-Agent Canvas יכול להגדיר אותו כמו נקודת קצה מרוחקת בסגנון OpenAI, בעוד שהמודל, ההנחיה (prompt) והקשר זרימת העבודה נשארים מקומיים.

במדריך זה, תבנו אוטומציה קונקרטית אחת: תקציר פיתוח מתוזמן מ-GitHub ל-Slack. הוא משתמש ב-GitHub כדי לבדוק פעילות מאגר אחרונה, ב-Slack כדי לפרסם את התקציר, בקריאות API של Agent Canvas כדי להגדיר ולבדוק את האוטומציה, וב-Lemonade כדי להריץ את ה-LLM באופן מקומי.

![תרשים ארכיטקטורה המציג GitHub MCP, אוטומציית OpenHands, Lemonade Server ו-Slack MCP](assets/00-architecture-overview.png)

## מה תלמדו

- כיצד להפעיל את Lemonade Server ולוודא שמודל מקומי עונה על בקשות צ'אט
- כיצד להפעיל את Agent Canvas ולהפנות את Agent Server שלו ל-LLM מקומי
- כיצד להתקין שרתי Model Context Protocol (MCP) של GitHub ו-Slack דרך ה-API של Agent Server
- כיצד ליצור ולהפעיל אוטומציית OpenHands מתוזמנת שמפרסמת תקציר פיתוח ל-Slack
- כיצד לפתור את כשלי המודל המקומי והאוטומציה הנפוצים ביותר

## מושגי יסוד

| מושג | מה זה | היכן זה משתלב במדריך הזה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת הגשת LLM מקומית שנבנתה עבור חומרת AMD וחושפת API תואם-OpenAI. הנתונים שלכם אף פעם לא עוזבים את המחשב שלכם. | מריצה את המודל שמפעיל את הסוכן. |
| OpenHands Agent Server | תהליך הרקע שמבצע שיחות סוכן של OpenHands. | מארח את הסוכן, פרופיל ה-LLM שלו, ושרתי ה-MCP שלו. |
| Agent Canvas | מישור הבקרה המקומי עבור OpenHands שמריץ את Agent Server וממשק משתמש לבדיקת הרצות סוכן. | מפעיל את שרתי הרקע ומספק את ה-API שאתם קוראים לו. |
| שרת MCP | שרת Model Context Protocol שנותן לסוכן כלים עבור שירות חיצוני כגון GitHub או Slack. | מאפשר לסוכן לקרוא מ-GitHub ולכתוב ל-Slack. |
| אוטומציית OpenHands | שיחת סוכן מתוזמנת או מופעלת על ידי אירוע שמביאה הקשר, מנמקת עליו, וכותבת תוצאה איפשהו. | תקציר ה-GitHub-ל-Slack שאתם בונים כאן. |

<!-- @device:stx,krk -->
> [!NOTE]
> זרימות עבודה של סוכן קידוד נהנות ממודל גדול יותר וחלון הקשר גדול יותר. השתמשו בלפחות 32 GB של זיכרון מערכת, והעדיפו 64 GB או יותר עבור מודלי GGUF גדולים יותר.
<!-- @device:end -->

## דרישות מוקדמות

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

נדרש לכם:

- Lemonade Server מותקן על ידי ביצוע [מדריך ההתקנה הסטנדרטי של Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ואילך ו-`npm`, המשמשים להתקנת ה-CLI המפורסם של Agent Canvas ולהרצת שרתי MCP באמצעות `npx`.
- חבילת `@openhands/agent-canvas` מפורסמת עדכנית עם הגדרות סוכן מבוססות-סכימה, `LLMSummarizingCondenserSettings.max_tokens`, ותמיכת `custom_tokenizer` ב-LLM.
- חבילת ה-Python `transformers` זמינה בסביבת Agent Server. היא נדרשת לספירת אסימונים (tokens) בתבנית צ'אט כאשר `custom_tokenizer` מוגדר.
- אסימון (token) GitHub עם גישת קריאה למאגר שברצונכם לסכם.
- אסימון בוט Slack (`xoxb-...`) עם `chat:write` וגישת קריאה לערוץ.
- מזהה צוות Slack (`T...`).
- מזהה ערוץ Slack (`C...`) שבו יש לפרסם את התקציר.

הזמינו את אפליקציית ה-Slack לערוץ היעד לפני בדיקת האוטומציה.

## משתנים המשמשים במדריך זה

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

הערכים הבאים מוזנים לממשק המשתמש של Agent Canvas בשלבים מאוחרים יותר. הגדירו אותם כאן כדי שתוכלו להעתיק אותם פנימה:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

השתמשו בערך מפורש `owner/repo` עבור `GITHUB_REPO_FILTER`. תווי כלליים (wildcards) רחבים ברמת ארגון עלולים להחזיר יותר מדי הקשר MCP עבור מודלים מקומיים.

## 1. הפעלת Lemonade Server

הפעילו את המודל מה-CLI של Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade חושף API תואם-OpenAI בכתובת:

```text
http://127.0.0.1:13305/api/v1
```

אופציונלי: אם Agent Canvas או מריץ האוטומציה אינם על אותה מכונה, פרסמו את נקודת הקצה של Lemonade דרך מנהרה מאובטחת והשתמשו בכתובת ה-URL של HTTPS ככתובת הבסיס (base URL) של ה-LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. אימות המודל המקומי

ודאו ש-Lemonade יכול להגיש את המודל שנבחר:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

לאחר מכן שלחו בקשת צ'אט קטנה:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

אם זה מחזיר מערך `choices`, Lemonade מוכן עבור Agent Canvas.
## 3. הפעלת Agent Canvas

התקינו את חבילת Agent Canvas שפורסמה והפעילו את המחסנית המלאה:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

אם ההתקנה הגלובלית של npm נכשלת עם שגיאת הרשאות, עיינו בערך פתרון בעיות
ההרשאות של npm בהמשך.

כברירת מחדל, Agent Canvas עולה בכתובת `http://localhost:8000`. פתחו את הכתובת
הזו בדפדפן שלכם. הבקאנד המקומי המוגדר כברירת מחדל אמור להופיע כתקין (healthy)
במסך הבית.

הפקודה `agent-canvas` מפעילה את שרת הסוכן, הבקאנד לאוטומציה, ואת חזית האתר
(frontend) יחד. אתם זקוקים רק לפקודה אחת זו כדי להריץ את OpenHands באופן
מקומי. שאר המדריך הזה מגדיר את הכל דרך ממשק המשתמש של Agent Canvas בדפדפן
שלכם.

## 4. הגדרת ה-LLM המקומי בממשק המשתמש

בהפעלה הראשונה, Agent Canvas פותח תהליך onboarding. בתהליך זה:

1. השאירו את **OpenHands** מסומן כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר ל-**API key**.
4. הגדירו את **Custom Model** לערך של `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** ל-`http://127.0.0.1:13305/api/v1`.
6. עבור **API Key**, הזינו כל ערך placeholder שאינו ריק, כגון `lemonade-local`.
   Lemonade אינו דורש מפתח אמיתי, אך הלקוח של OpenHands זקוק לערך כלשהו
   כדי לשלוח.

שדות החיבור אמורים להיראות כך. שדה מפתח ה-API מוסתר על ידי הממשק.

![הגדרות Advanced של LLM במסך השימוש הראשון ב-Agent Canvas עם מודל Lemonade וכתובת בסיס מקומית](assets/01-llm-advanced-settings.png)

לאחר מכן בחרו **All** והגדירו את שדות המודל המקומי הנוספים:

1. גללו אל **Custom Tokenizer** והגדירו אותו ל-`Qwen/Qwen3.6-35B-A3B`.
2. גללו אל **LiteLLM Extra Body** והגדירו אותו ל-
   `{"enable_thinking": true}`.
3. לחצו על **Next**.

![לשונית All של LLM במסך השימוש הראשון ב-Agent Canvas עם ה-tokenizer המותאם אישית של Qwen](assets/02-llm-all-tokenizer-settings.png)

![לשונית All של LLM במסך השימוש הראשון ב-Agent Canvas עם LiteLLM extra body מוגדר](assets/03-llm-all-extra-body-settings.png)

הגדרות ה-LLM אמורות להראות:

| שדה | ערך |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

הקידומת `openai/` אומרת ל-LiteLLM להשתמש בעיצוב בקשות תואם-OpenAI מול נקודת
הקצה של Lemonade. ה-tokenizer המותאם אישית הוא ה-tokenizer המקורי של
Hugging Face עבור מודל ה-GGUF; הוא מאפשר ל-OpenHands לספור את אותם טוקנים של
תבנית הצ'אט (chat-template) שרואה שרת המודל המקומי. טופס ה-LLM הנוכחי לשימוש
ראשון אינו מציג הגדרות condenser. אם גרסת ה-Agent Canvas שלכם חושפת הגדרות
condenser מאוחר יותר תחת **Settings > LLM**, השתמשו ב-`llm_summarizing` והגדירו
מספר טוקנים מקסימלי נמוך מחלון ההקשר של Lemonade, כגון `56000`.

## 5. התקנת שרתי MCP של GitHub ו-Slack

בממשק המשתמש של Agent Canvas, פתחו את **Customize** (או **Settings > MCP**)
כדי להוסיף את שרתי ה-MCP שמעניקים לסוכן כלים עבור GitHub ו-Slack. ערכי
הטוקנים נשלחים רק לשרת הסוכן המקומי שלכם ונשמרים כהגדרות מוצפנות.

### שרת MCP של GitHub

הוסיפו שרת MCP חדש עם ההגדרות הבאות:

| שדה | ערך |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = הטוקן שלכם ב-GitHub |

השתמשו בטוקן GitHub עם גישת קריאה למאגר שברצונכם לסכם.

### שרת MCP של Slack

הוסיפו שרת MCP שני עם ההגדרות הבאות:

| שדה | ערך |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = מזהה ערוץ הדיגסט שלכם |

הגדירו את `SLACK_CHANNEL_IDS` למזהה ערוץ הדיגסט (אותו ערך כמו
`SLACK_DIGEST_CHANNEL`) כדי שהסוכן לא יצטרך לעבור על כל ערוצי ה-Slack.

לאחר הוספת שני השרתים, השתמשו בכפתור **Test** בכל אחד מהם כדי לוודא שהוא
מתחבר ומפרסם כלים. שרת ה-GitHub אמור להציג רשימת כלי GitHub, ושרת ה-Slack
אמור להציג רשימת כלי Slack.

![עמוד MCP ב-Agent Canvas עם שרתי GitHub ו-Slack מותקנים](assets/04-mcp-servers-installed.png)

## 6. יצירת אוטומציית הדיגסט

בממשק המשתמש של Agent Canvas, פתחו את עמוד **Automations** וצרו אוטומציה
חדשה:

1. בחרו **Create automation** ובחרו בסוג **Prompt preset**.
2. הגדירו את ה-**Name** ל-`GitHub Development Digest to Slack`.
3. הגדירו את ה-**Prompt** לטקסט הבא, תוך החלפת ה-placeholders של המאגר
   והערוץ בערכים שלכם:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. הגדירו את ה-**Trigger** ל-**Cron** עם התזמון `0 9 * * 1-5` (9 בבוקר בימי
   חול) והגדירו את ה-**Timezone** לאזור הזמן שלכם, לדוגמה
   `America/New_York`.
5. הגדירו את ה-**Timeout** ל-`900` שניות.
6. שמרו את האוטומציה.

עמוד פרטי האוטומציה מציג את האוטומציה החדשה עם ה-trigger מסוג cron שלה
ונקודת הכניסה של ה-prompt-preset שנוצרה.

![עמוד פרטי האוטומציה ב-Agent Canvas לאחר היצירה](assets/05-automation-created.png)
## 7. בדיקת האוטומציה

מדף פרטי האוטומציה בממשק Agent Canvas UI:

1. לחצו על **Run now** (או **Dispatch**) כדי להריץ את האוטומציה פעם אחת מיידית.
2. עקבו אחר רשימת ההרצות באותו דף. ההרצה האחרונה אמורה לעבור למצב
   `COMPLETED`.
3. פתחו את ערוץ ה-Slack היעד שלכם. הוא אמור להכיל את התקציר שנוצר.

אין צורך להמתין להפעלת לוח הזמנים של cron—**Run now** מפעיל
הרצה על פי דרישה כך שתוכלו לוודא שהפרומפט, חיבורי ה-MCP, ופרסום ה-Slack
כולם עובדים לפני ההסתמכות על לוח הזמנים.

![הרצת אוטומציה ב-Agent Canvas הושלמה בהצלחה](assets/06-automation-run-completed.png)

![ערוץ Slack המציג את תקציר OpenHands שנוצר](assets/07-slackbot-message.png)

## פתרון בעיות

- **Lemonade לא פעיל:** הפעילו אותו מחדש עם
  הפקודה `lemonade run "${LEMONADE_MODEL}"` משלב 1, ולאחר מכן הריצו מחדש את בדיקת
  התקינות.
- **`npm install -g` נכשל עם שגיאת הרשאות:** ב-Linux או WSL,
  הגדירו ספריית npm גלובלית בבעלות המשתמש, הוסיפו אותה לקובץ אתחול ה-shell
  שלכם, ולאחר מכן התקינו את Agent Canvas שוב:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  אם אתם משתמשים ב-`zsh`, הוסיפו את אותה שורת `export PATH=...` לקובץ
  `~/.zshrc` במקום ל-`~/.bashrc`.
- **Agent Canvas דוחה את הגדרות ה-LLM לאחר הגדרת `custom_tokenizer`:**
  התקינו את `transformers` בסביבת ה-Python של Agent Server, הפעילו מחדש את Agent
  Canvas אם נדרש, ונסו שוב לשמור את הגדרות ה-LLM. OpenHands דורש
  Transformers כדי לטעון את תבנית הצ'אט של ה-tokenizer כאשר `custom_tokenizer`
  מוגדר.
- **Agent Canvas לא מצליח להגיע ל-Lemonade:** ודאו
  `curl -fsS "${LEMONADE_BASE_URL}/health"` ואשרו שכתובת הבסיס שהוזנה בטופס
  ה-LLM בשימוש הראשון או ב-**Settings > LLM** תואמת לנקודת הקצה המקומית
  הפועלת או למנהרת HTTPS.
- **הגדרות ה-LLM לא נשמרו:** ודאו שלחצתם על **Next** לאחר
  הזנת הערכים. פתחו מחדש את **Settings > LLM** כדי לאשר שהערכים
  נשמרו.
- **GitHub MCP לא רואה מאגרים פרטיים:** ודאו שלטוקן GitHub יש
  גישת קריאה למאגר היעד ושכפתור ה-**Test** ב-MCP
  ב-**Customize** מציג כלי GitHub.
- **Slack יכול לקרוא ערוצים אך לא יכול לפרסם:** הזמינו את אפליקציית ה-Slack אל
  ערוץ היעד ואשרו שלבוט יש `chat:write`.
- **האוטומציה מציגה רשימה ארוכה מדי של ערוצי Slack:** השתמשו במזהה ערוץ Slack ו
  הגדירו את `SLACK_CHANNEL_IDS` בשרת ה-Slack MCP ב-**Customize**.
- **הרצת האוטומציה נכשלת או חורגת מהקונטקסט:** ודאו ש-Lemonade הופעל
  עם `ctx_size=65536`, ודאו של-LLM של OpenHands מוגדר `custom_tokenizer`,
  והשתמשו במאגר מפורש עם קבוצות תוצאות GitHub המוגבלות ל-3 עד 5
  פריטים. אם גרסת ה-Agent Canvas שלכם חושפת הגדרות condenser, הגדירו את מספר האסימונים
  המקסימלי של ה-condenser מתחת לחלון הקונטקסט של Lemonade.

## השלבים הבאים

- הוסיפו תקציר שבועי המתמקד רק בשחרורי גרסאות.
- הוסיפו אוטומציה המופעלת על ידי אירוע GitHub להתראות מהירות יותר על PR או push.
- נתבו את אותו תקציר לתוך Notion, Linear, או כלי אחר מבוסס MCP.

## משאבים

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [תיעוד Lemonade Server](https://lemonade-server.ai/docs)
- [מאגר ההרחבות של OpenHands](https://github.com/OpenHands/extensions)
- [שרתי Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [חבילת Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)