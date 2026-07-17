<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

n8n היא פלטפורמת אוטומציה של תהליכי עבודה המאפשרת לך לחבר אפליקציות ושירותים באמצעות עורך ויזואלי מבוסס-צמתים.

מדריך זה מלמד אותך כיצד להגדיר מסכם חדשות פיננסיות מבוסס בינה מלאכותית, אשר גורד את מדור העסקים של AP News, מחלץ כותרות מרכזיות, ומשתמש ב-LLM מקומי הפועל על המערכת שלך כדי לייצר סיכום ממוקד-משקיעים.

## מה תלמד

- כיצד להתקין ולהפעיל את n8n
- ייבוא והגדרת תהליך עבודה מוכן מראש
- חיבור ל-Lemonade באמצעות האינטגרציה המובנית של n8n
- הבנת צמתי תהליך העבודה וזרימת הנתונים

## מהו Lemonade?

[Lemonade](https://lemonade-server.ai) היא פלטפורמת הגשת LLM מקומית שנבנתה עבור חומרת AMD. היא מספקת API תואם-OpenAI הפועל לחלוטין על המכשיר שלך—הנתונים שלך לעולם אינם עוזבים את המכשיר.

במדריך זה, אנו משתמשים ב-Lemonade להגשת LLM מקומי שאליו n8n מתחבר למשימות מבוססות בינה מלאכותית.

ל-n8n יש **צומת Lemonade מובנה** (`Lemonade Chat Model`) המספק אינטגרציה ברמה ראשונה - אין צורך בהגדרה ידנית. זה הופך את חיבור ה-LLM המקומי שלך לתהליכי עבודה אוטומטיים לפשוט.

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

> **הערה**: ייתכן שתראה אזהרות npm מסוימות. זה צפוי.

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
> **טיפ**: משתמשי Windows עשויים להזדקק לשינוי מדיניות הביצוע של PowerShell (למשל,
> הגדרתה ל-RemoteSigned או Unrestricted) לפני הפעלת פקודות Powershell מסוימות.
<!-- @os:end -->


<!-- @os:windows -->
> **בעיית PATH**: אם `n8n --version` מציג שהפקודה לא נמצאה, ודא שספריית ה-bin הגלובלית של npm נמצאת ב-`PATH` של המשתמש. נתיב ההתקנה הרגיל הוא `C:\Users\<username>\AppData\Roaming\npm`.
> הוסף זאת לנתיב המשתמש (ערוך את משתני סביבת המערכת > משתני סביבה > ערוך נתיב משתמש) וטען מחדש את הטרמינל.

<!-- @os:end -->

<!-- @os:linux -->
אנו עומדים להשתמש בשירות Podman כדי לאגד את התקנת n8n שלנו בקונטיינר.

אנא הורד את הקובץ הבא לספרייה לבחירתך: [compose.yml](assets/compose.yml)

בספרייה זו, הפעל את הפקודה הבאה:
```bash
podman compose up -d
```

פעולה זו אמורה להתקין את n8n ולכתוב לאחסון קבוע.

הפעל את n8n על ידי הקלדת `localhost:5678` בשורת הכתובת של הדפדפן שלך.
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
n8n מפעיל שרת אינטרנט מקומי. לחץ על `'o'` או פתח את הדפדפן שלך לכתובת `http://localhost:5678` כדי לגשת לעורך.
<!-- @os:end -->


> **טיפ**: השאר את חלון הטרמינל פתוח בזמן השימוש ב-n8n. סגירתו עלולה לעצור את השרת.

## הפעלת Lemonade

Lemonade הוא השרת המקומי שיפעיל מודל ויתחבר ל-n8n.

<!-- @os:linux -->
פתח את ממשק המשתמש של Lemonade על ידי לחיצה על סמל Lemonade בשורת המשימות. תוכל לעיין במודלים, בקצוות עורפיים, ולטעון את המודלים המותקנים מראש מכאן.
<!-- @os:end -->

<!-- @os:windows -->
פתח את ממשק המשתמש של Lemonade על ידי לחיצה על סמל Lemonade. לחץ לחיצה ימנית על סמל מגש המערכת כדי לפתוח את האפליקציה. לאחר מכן, תוכל להוסיף מודלים, קצוות עורפיים, ולטעון את המודלים המותקנים מראש.
<!-- @os:end -->

>**טיפ**: לאחר ההפעלה, ממשק המשתמש של Lemonade נגיש גם בכתובת http://localhost:13305

לחלופין, תוכל לפתוח טרמינל ולהפעיל את `lemonade list` כדי לראות אילו מודלים מותקנים. לאחר מכן, הפעל:

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

### שלב 1: הרשמה או כניסה ל-n8n

כאשר תפתח את n8n בפעם הראשונה, תתבקש ליצור חשבון או להתחבר:

1. פתח את `http://localhost:5678` בדפדפן שלך
2. צור חשבון מקומי חדש עם כתובת הדוא"ל שלך, או התחבר אם כבר יש לך חשבון
3. לאחר הכניסה, תראה את לוח המחוונים של n8n

> **טיפ**: אם ננעלת מחוץ לחשבונך, נסה `n8n user-management:reset`

### שלב 2: ייבוא תהליך העבודה

סיפקנו תהליך עבודה מוכן מראש שניתן לייבא ישירות:

1. הורד את קובץ תהליך העבודה הבא: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. לחץ על **Start from Scratch** כדי לפתוח את עורך תהליך העבודה. לחלופין, לחץ על כפתור ה-+ בפינה השמאלית העליונה, ולאחר מכן על **Add workflow**.
3. לחץ על תפריט **...** (שלוש נקודות) בסרגל הימני העליון ובחר **Import from file**
4. בחר את קובץ `financial-news-workflow.json` שהורדת
5. תהליך העבודה יופיע על הבד


### שלב 3: הבנת תהליך העבודה

תהליך העבודה המיובא מכיל 9 צמתים מחוברים:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| צומת | מטרה |
|------|---------|
| **When clicking 'Execute workflow'** | טריגר ידני להפעלת תהליך העבודה |
| **Fetch Financial News Webpage** | בקשת HTTP GET לכתובת `https://apnews.com/business` |
| **Delay to Ensure Page Load** | צומת המתנה להבטחת טעינה מלאה של תוכן הדף |
| **Extract News Headlines & Text** | צומת HTML המחלץ כותרות, בחירות עורכים, סיפורים מובילים וחדשות אזוריות באמצעות בוררי CSS |
| **Clean Extracted News Data** | צומת Set המשלב את כל הנתונים המחולצים לשדה טקסט יחיד |
| **AI Financial News Summarizer** | סוכן בינה מלאכותית המעבד את החדשות עם הנחיית מערכת של אנליסט פיננסי |
| **Lemonade Chat Model** | מתחבר לשרת Lemonade המקומי שלך המפעיל את ה-LLM |
| **Structured Output Parser** | מעצב את פלט הבינה המלאכותית כ-JSON מובנה |
| **Convert to File** | ממיר את הסיכום לקובץ להורדה |

### שלב 4: הגדרת אישורי Lemonade

לפני הפעלת תהליך העבודה, עליך לחבר אותו לשרת Lemonade המקומי שלך:

1. לחץ לחיצה כפולה על צומת **Lemonade Chat Model** ב-n8n
2. בתפריט הנפתח **Credential to connect with** בחר **Create New Credential**
3. הזן את הערכים בטבלה שלהלן ולחץ על שמור.
4. בחר את המודל הרלוונטי שטענת בשרת Lemonade.

  | שדה | ערך |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **הערה**: לפני הבדיקה, הפעל את `lemonade status` בטרמינל כדי לאשר שהשרת Lemonade פועל.
<!-- @device:halo_box -->
> תהליך עבודה זה משתמש ב-GPT-OSS-120B והוא מותקן מראש ב-Lemonade. ניתן לשנות זאת למודלים אחרים שנטענו בהגדרות צומת Lemonade Chat Model.
<!-- @device:end -->

### שלב 5: בדיקת תהליך העבודה

1. ודא ש-Lemonade פועל עם מודל טעון
2. לחץ על **Execute workflow** במרכז התחתון של הבד
3. צפה בכל צומת מתבצע משמאל לימין—הם הופכים לירוק עם השלמתם
4. לחץ לחיצה כפולה על צומת **AI Financial News Summarizer** כדי לראות את הסיכום שנוצר בחלונית התחתונה.
5. לחץ לחיצה כפולה על צומת **Convert to File** כדי להוריד את קובץ הטקסט המתאים בחלונית התחתונה.

## הבנת סוכן הבינה המלאכותית

מסכם החדשות הפיננסיות של הבינה המלאכותית משתמש בהנחיית מערכת המיועדת לניתוח פיננסי:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

הסוכן מקבל את נתוני החדשות המנוקים ומפיק סיכום מובנה עם סנטימנט שוק.

### שמירת תהליך העבודה שלך

לחץ על שם תהליך העבודה בחלק העליון ושנה את שמו אם תרצה. תהליכי עבודה נשמרים אוטומטית בזמן העבודה.

## השלבים הבאים

- **תזמון אוטומציה**: החלף את הטריגר הידני ב-**Schedule Trigger** להפעלה יומית
- **שליחת התראות**: הוסף צומת **Discord**, **Slack**, או **Email** לקבלת סיכומים
- **נסה מודלים שונים**: שנה את המודל בצומת Lemonade Chat Model כדי להתנסות ב-LLM שונים
- **התאמה אישית של החילוץ**: שנה את בוררי ה-CSS של צומת HTML Extract כדי למקד בקטעי חדשות שונים
- **נסה קצוות עורפיים שונים**: n8n תומך גם ב-[Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio, וקצוות עורפיים אחרים של LLM מקומי

### חקור תבניות n8n

ל-n8n יש מאות תבניות תהליכי עבודה מוכנות מראש. עיין בספריית התבניות הרשמית בכתובת:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

חפש "AI", "LLM", או "automation" כדי למצוא תהליכי עבודה שניתן לייבא ולהתאים אישית.

למידע נוסף, עיין ב[תיעוד n8n](https://docs.n8n.io/).