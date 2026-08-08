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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> ספר משחקים זה דורש מינימום של **32GB** של זיכרון מערכת.
<!-- @device:end -->

n8n היא פלטפורמת אוטומציית תהליכי עבודה המאפשרת לחבר יישומים ושירותים באמצעות עורך ויזואלי מבוסס-צמתים.

ספר משחקים זה מלמד כיצד להגדיר מסכם חדשות פיננסיות מבוסס בינה מלאכותית, הסורק את מדור העסקים של AP News, מחלץ כותרות מרכזיות, ומשתמש במודל שפה מקומי (LLM) הפועל על המערכת שלך כדי ליצור סיכום המיועד למשקיעים.

## מה תלמדו

- כיצד להתקין ולהפעיל את n8n
- ייבוא והגדרה של תהליך עבודה מוכן מראש
- התחברות ל-Lemonade באמצעות האינטגרציה הטבעית של n8n
- הבנת צמתי תהליך העבודה וזרימת הנתונים

## מהו Lemonade?

[Lemonade](https://lemonade-server.ai) היא פלטפורמת שירות מודלי שפה מקומיים (LLM) שנבנתה עבור חומרת AMD. היא מספקת ממשק API תואם-OpenAI הפועל כולו על המכשיר שלך - הנתונים שלך לעולם לא עוזבים את המכשיר.

בספר משחקים זה, אנו משתמשים ב-Lemonade כדי להפעיל מודל שפה מקומי שאליו n8n מתחבר עבור משימות מבוססות בינה מלאכותית.

n8n כולל **צומת Lemonade טבעי** (`Lemonade Chat Model`) המספק אינטגרציה מובנית ברמה ראשונה - אין צורך בהגדרה ידנית. זה הופך את חיבור מודל השפה המקומי שלך לתהליכי אוטומציה לפשוט.

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## התקנת n8n
<!-- @os:windows -->
התקן את n8n באופן גלובלי באמצעות npm.

> **הערה**: ייתכן שתראה כמה אזהרות npm. זה צפוי.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרשאות (Execution Policy) של PowerShell שלהם (לדוגמה,
> להגדיר אותה ל-RemoteSigned או Unrestricted) לפני הרצת פקודות PowerShell מסוימות.
<!-- @os:end -->


<!-- @os:windows -->
> **בעיית PATH**: אם `n8n --version` מציג הודעה שהפקודה לא נמצאה, ודא שספריית ה-bin הגלובלית של npm נמצאת ב-`PATH` של המשתמש. נתיב ההתקנה הרגיל הוא ב-`C:\Users\<username>\AppData\Roaming\npm`.
> הוסף זאת לנתיב המשתמש (עריכת משתני הסביבה של המערכת > משתני סביבה > עריכת נתיב משתמש) וטען מחדש את הטרמינל.

<!-- @os:end -->

<!-- @os:linux -->
כעת נשתמש בשירות Podman כדי להריץ את התקנת n8n שלנו בקונטיינר.

אנא הורד את הקובץ הבא לתיקייה לבחירתך: [compose.yml](assets/compose.yml)

בתיקייה זו, הרץ את הפקודה הבאה:
```bash
podman compose up -d
```

פעולה זו אמורה להתקין את n8n ולכתוב לאחסון קבוע.

הפעל את n8n על ידי הקלדת `localhost:5678` בשורת הכתובת של הדפדפן.
<!-- @os:end -->

<!-- @os:windows -->
## הפעלת n8n

הפעל את n8n מהטרמינל:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n מפעיל שרת אינטרנט מקומי. לחץ על `'o'` או פתח את הדפדפן שלך בכתובת `http://localhost:5678` כדי לגשת לעורך.
<!-- @os:end -->


> **טיפ**: השאר את חלון הטרמינל פתוח בזמן השימוש ב-n8n. סגירתו עלולה לעצור את השרת.

## הפעלת Lemonade

Lemonade הוא השרת המקומי שיריץ מודל ויתחבר ל-n8n.

<!-- @os:linux -->
פתח את ממשק המשתמש הגרפי (GUI) של Lemonade על ידי לחיצה על סמל Lemonade בשורת המשימות. מכאן תוכל לעיין במודלים, במנועים (backends) ולטעון את המודלים המותקנים מראש.
<!-- @os:end -->

<!-- @os:windows -->
פתח את ממשק המשתמש הגרפי (GUI) של Lemonade על ידי לחיצה על סמל Lemonade. לחץ לחיצה ימנית על סמל המגש כדי לפתוח את האפליקציה. לאחר מכן, תוכל להוסיף מודלים, מנועים (backends) ולטעון את המודלים המותקנים מראש.
<!-- @os:end -->

>**טיפ**: לאחר ההפעלה, ניתן לגשת לממשק המשתמש הגרפי (GUI) של Lemonade גם בכתובת http://localhost:13305

לחלופין, ניתן לפתוח טרמינל ולהריץ את `lemonade list` כדי לראות אילו מודלים מותקנים. לאחר מכן, הרץ:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## הגדרת תהליך העבודה

### שלב 1: הרשמה או התחברות ל-n8n

בפעם הראשונה שתפתח את n8n, תתבקש ליצור חשבון או להתחבר:

1. פתח את `http://localhost:5678` בדפדפן שלך
2. צור חשבון מקומי חדש עם כתובת האימייל שלך, או התחבר אם כבר יש לך חשבון
3. לאחר ההתחברות, תראה את לוח הבקרה של n8n

> **טיפ**: אם ננעלת מחוץ לחשבון שלך, נסה להריץ `n8n user-management:reset`

### שלב 2: ייבוא תהליך העבודה

סיפקנו תהליך עבודה מוכן מראש שניתן לייבא ישירות:

1. הורד את קובץ תהליך העבודה הבא: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. לחץ על **Start from Scratch** כדי לפתוח את עורך תהליך העבודה. לחלופין, לחץ על כפתור ה-+ בפינה השמאלית העליונה, ולאחר מכן על **Add workflow**.
3. לחץ על תפריט ה-**...** (שלוש נקודות) בפינה הימנית העליונה ובחר **Import from file**
4. בחר את קובץ ה-`financial-news-workflow.json` שהורדת
5. תהליך העבודה יופיע על גבי הקנבס
### שלב 3: הבנת ה-Workflow

ה-workflow המיובא מכיל 9 צמתים (nodes) מחוברים:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | מטרה |
|------|---------|
| **When clicking 'Execute workflow'** | טריגר ידני להפעלת ה-workflow |
| **Fetch Financial News Webpage** | בקשת HTTP GET אל `https://apnews.com/business` |
| **Delay to Ensure Page Load** | צומת Wait להבטחת טעינה מלאה של תוכן הדף |
| **Extract News Headlines & Text** | צומת HTML שמחלץ כותרות, מבחר עורכים, כתבות מובילות וחדשות אזוריות באמצעות סלקטורים של CSS |
| **Clean Extracted News Data** | צומת Set שמאחד את כל הנתונים שחולצו לשדה טקסט יחיד |
| **AI Financial News Summarizer** | AI Agent שמעבד את החדשות עם system prompt של אנליסט פיננסי |
| **Lemonade Chat Model** | מתחבר לשרת Lemonade המקומי שלך שמריץ את ה-LLM |
| **Structured Output Parser** | מעצב את פלט ה-AI כ-JSON מובנה |
| **Convert to File** | ממיר את הסיכום לקובץ להורדה |

### שלב 4: הגדרת אישורי Lemonade

לפני הרצת ה-workflow, עליך לחבר אותו לשרת Lemonade המקומי שלך:

1. לחץ פעמיים על צומת **Lemonade Chat Model** ב-n8n
2. בתפריט הנפתח **Credential to connect with** בחר **Create New Credential**
3. הזן את הערכים בטבלה שלהלן ולחץ על שמירה.
4. בחר את המודל הרלוונטי שטעון אצלך ב-Lemonade Server.

  | שדה | ערך |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **הערה**: לפני הבדיקה, הרץ `lemonade status` בטרמינל כדי לוודא ששרת Lemonade פועל.
<!-- @device:halo_box -->
> ה-workflow הזה משתמש ב-GPT-OSS-120B והוא מותקן מראש ב-Lemonade. באפשרותך לשנות זאת למודלים טעונים אחרים בהגדרות צומת Lemonade Chat Model.
<!-- @device:end -->

### שלב 5: בדיקת ה-Workflow

1. ודא ש-Lemonade פועל עם מודל טעון
2. לחץ על **Execute workflow** במרכז התחתון של הקנבס
3. עקוב אחר הפעלת כל צומת משמאל לימין—הם הופכים לירוקים בסיום
4. לחץ פעמיים על צומת **AI Financial News Summarizer** כדי לראות את הסיכום שנוצר בחלונית התחתונה.
5. לחץ פעמיים על צומת **Convert to File** כדי להוריד את קובץ הטקסט המתאים בחלונית התחתונה.

## הבנת ה-AI Agent

ה-AI Financial News Summarizer משתמש ב-system prompt שתוכנן לניתוח פיננסי:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

ה-agent מקבל את נתוני החדשות שנוקו ומפיק סיכום מובנה עם סנטימנט שוק.

### שמירת ה-Workflow שלך

לחץ על שם ה-workflow בחלק העליון ושנה את שמו אם תרצה. Workflows נשמרים אוטומטית תוך כדי עבודה.

## הצעדים הבאים

- **תזמון אוטומציה**: החלף את Manual Trigger ב-**Schedule Trigger** כדי להריץ מדי יום
- **שליחת התראות**: הוסף צומת **Discord**, **Slack** או **Email** כדי לקבל סיכומים
- **נסה מודלים שונים**: שנה את המודל בצומת Lemonade Chat Model כדי להתנסות ב-LLM שונים
- **התאמה אישית של החילוץ**: שנה את סלקטורי ה-CSS של צומת HTML Extract כדי למקד לחלקי חדשות שונים
- **נסה backends שונים**: n8n תומך גם ב-[Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio, ו-backends מקומיים אחרים של LLM

### גלה תבניות n8n

ל-n8n יש מאות תבניות workflow מובנות מראש. עיין בספריית התבניות הרשמית בכתובת:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

חפש "AI", "LLM" או "automation" כדי למצוא workflows שתוכל לייבא ולהתאים אישית.

למידע נוסף, עיין ב[תיעוד n8n](https://docs.n8n.io/).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->