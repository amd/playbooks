<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## סקירה כללית

מפתחים מבלים הרבה זמן בלולאות חוזרות קטנות: בדיקת pull requests מתויגים, מענה על תגובות ב-GitHub, מיון issues חדשים, הפיכת שרשורי Slack לעדכוני סטטוס יומיים או מעקבי תקריות, ומעקב אחר אותות שחרור או מחקר.
כל לולאה מוכרת, אך עדיין דורשת שיקול דעת: איסוף ההקשר הנכון, החלטה מה חשוב, ופרסום עדכון ברור במקום שבו הצוות כבר עובד.

[אוטומציות OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) הופכות את אותן לולאות לשיחות סוכן מתוזמנות או מופעלות על ידי אירועים: הרצות שבהן סוכן תוכנה מבוסס AI יכול לקרוא הקשר, לקרוא לכלים, וליצור עדכון.
תבניות האוטומציה המשותפות בקטלוג ההרחבות של OpenHands עוקבות אחר תבנית זו עבור ביקורת pull request ב-GitHub, מעקב מאגרים (repository monitoring), מיון issues ב-Linear, סיכומי תקריות (incident retrospectives), תקצירי סטטוס יומי ב-Slack, ותקצירי מחקר: אוטומציה מתעוררת, משתמשת באינטגרציות מוגדרות כגון GitHub או Slack כדי לאחזר הקשר, מנמקת על אותו הקשר באמצעות מודל שפה גדול (LLM), וכותבת בחזרה תוצאה.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא מישור הבקרה המקומי לבניה ובדיקה של אותן אוטומציות.
במדריך זה הוא מריץ OpenHands Agent Server, תהליך ה-backend שמבצע שיחות סוכן, ומחבר את הסוכן לשירותים חיצוניים כגון GitHub ו-Slack.

כדי לשמור את זרימת העבודה על מערכת ה-AMD שלך, הסוכן מתקשר עם מודל מקומי המוגש על ידי Lemonade Server.
Lemonade חושף מודל זה דרך API תואם OpenAI, כך ש-Agent Canvas יכול להגדיר אותו כמו נקודת קצה מרוחקת בסגנון OpenAI, בעוד שהמודל, הפרומפט, והקשר זרימת העבודה נשארים מקומיים.

במדריך זה, תבנה אוטומציה קונקרטית אחת: תקציר פיתוח מתוזמן מ-GitHub ל-Slack.
הוא משתמש ב-GitHub כדי לבדוק פעילות מאגר אחרונה, ב-Slack כדי לפרסם את התקציר, בקריאות API של Agent Canvas כדי להגדיר ולבדוק את האוטומציה, וב-Lemonade כדי להריץ את ה-LLM באופן מקומי.

![תרשים ארכיטקטורה המציג GitHub MCP, אוטומציית OpenHands, Lemonade Server, ו-Slack MCP](assets/00-architecture-overview.png)

## מה תלמד

- כיצד להפעיל את Lemonade Server ולוודא שמודל מקומי עונה לבקשות צ'אט
- כיצד להפעיל את Agent Canvas ולהצביע את ה-Agent Server שלו על LLM מקומי
- כיצד להתקין שרתי Model Context Protocol (MCP) של GitHub ו-Slack דרך ה-API של ה-Agent Server
- כיצד ליצור ולהפעיל אוטומציית OpenHands מתוזמנת שמפרסמת תקציר פיתוח ל-Slack
- כיצד לפתור את הבעיות הנפוצות ביותר הקשורות למודל המקומי ולאוטומציה

## מושגי יסוד

| מושג | מהו | היכן הוא משתלב במדריך זה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת הגשת LLM מקומית שנבנתה עבור חומרת AMD וחושפת API תואם OpenAI. הנתונים שלך לעולם לא עוזבים את המחשב שלך. | מריץ את המודל שמפעיל את הסוכן. |
| OpenHands Agent Server | תהליך ה-backend שמבצע שיחות סוכן של OpenHands. | מארח את הסוכן, פרופיל ה-LLM שלו, ושרתי ה-MCP שלו. |
| Agent Canvas | מישור הבקרה המקומי של OpenHands שמריץ Agent Server וממשק משתמש לבדיקת הרצות סוכן. | מפעיל את ה-backends ומספק את ה-API שבו אתה קורא. |
| שרת MCP | שרת Model Context Protocol שמעניק לסוכן כלים עבור שירות חיצוני כגון GitHub או Slack. | מאפשר לסוכן לקרוא מ-GitHub ולכתוב ל-Slack. |
| אוטומציית OpenHands | שיחת סוכן מתוזמנת או מופעלת על ידי אירוע, שמאחזרת הקשר, מנמקת עליו, וכותבת תוצאה איפשהו. | תקציר ה-GitHub-ל-Slack שאתה בונה כאן. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> זרימות עבודה של סוכן קידוד נהנות ממודל גדול יותר וחלון הקשר גדול יותר.
> השתמש לפחות ב-32 GB של זיכרון מערכת, ועדיף 64 GB או יותר עבור מודלי GGUF גדולים יותר.
<!-- @device:end -->

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## דרישות מוקדמות

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

עליך:

- Lemonade Server מותקן על ידי ביצוע [מדריך ההתקנה הסטנדרטי של Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js גרסה 22.12 ומעלה ו-`npm`, המשמשים להתקנת ה-CLI המפורסם של Agent Canvas ולהרצת שרתי MCP באמצעות `npx`.
- `uv`, מנהל חבילות ה-Python ש-Agent Canvas משתמש בו כדי לבנות את סביבת ה-Agent Server. אם הוא עדיין לא מותקן, התקן אותו מ-[מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).
- חבילת `@openhands/agent-canvas` מפורסמת עדכנית עם הגדרות סוכן מבוססות סכמה, `LLMSummarizingCondenserSettings.max_tokens`, ותמיכה ב-`custom_tokenizer` של LLM.
- חבילת ה-Python `transformers` זמינה בסביבת ה-Agent Server. היא נדרשת לספירת אסימונים (token counting) של תבנית צ'אט כאשר `custom_tokenizer` מוגדר.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), מותקן ופועל. ב-Windows, ערימת Agent Canvas פועלת מתוך תמונת ה-Docker המפורסמת, הכוללת את Node.js, `uv`, `transformers`, וחבילת `@openhands/agent-canvas`, כך שאינך צריך להתקין אותם במארח.
<!-- @os:end -->

- אסימון GitHub עם גישת קריאה למאגר שברצונך לסכם.
- אסימון בוט Slack (`xoxb-...`) עם גישת `chat:write` וגישת קריאה לערוץ.
- מזהה צוות Slack (`T...`).
- מזהה ערוץ Slack (`C...`) שבו יש לפרסם את התקציר.

הזמן את אפליקציית Slack לערוץ היעד לפני בדיקת האוטומציה.
## משתנים המשמשים במדריך זה

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

שני משתנים אלו משמשים את פקודות האימות שלהלן.
המודל, ה-tokenizer והגדרות LLM נוספות מוזנים ישירות בממשק המשתמש של Agent Canvas בשלבים הבאים, כך שהערכים המילוליים שלהם מוצגים באופן מוטבע במקומות שבהם תזדקק להם.

הערכים הבאים מוזנים לתוך ממשק המשתמש של Agent Canvas בשלבים הבאים.
הגדר אותם כאן כדי שתוכל להעתיק אותם משם:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

השתמש בערך מפורש בצורת `owner/repo` עבור `GITHUB_REPO_FILTER`.
תווים כלליים (wildcards) רחבים של ארגון עלולים להחזיר יותר מדי הקשר MCP עבור מודלים מקומיים.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. הפעלת Lemonade Server

הפעל את המודל מ-Lemonade CLI:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **בחר מודל שמתאים לחומרה שלך.** `Qwen3.6-35B-A3B-GGUF` (כ-20 ג'יגהבייט) הוא מודל חזק עבור זרימת עבודה זו אך דורש מאגר זיכרון גדול.
> אם למכשיר שלך יש זיכרון מוגבל או VRAM של GPU מוגבל, בחר מודל GGUF קטן יותר מספריית המודלים של Lemonade והשתמש במזהה המודל הזה (ובטוקנייזר התואם לו) לאורך כל המדריך הזה.

> **הערה:** ההרצה הראשונה של `lemonade run` מורידה את המודל אם הוא עדיין לא קיים, מה שעשוי לקחת זמן מה בהתאם לגודל המודל ולחיבור שלך.

Lemonade חושף ממשק API תואם OpenAI בכתובת:

```text
http://127.0.0.1:13305/api/v1
```

אופציונלי: אם Agent Canvas או מריץ האוטומציה אינם על אותו מחשב, פרסם את נקודת הקצה של Lemonade דרך מנהרה מאובטחת והשתמש בכתובת ה-HTTPS ככתובת הבסיס של ה-LLM.
[ngrok](https://ngrok.com/) חושף פורט מקומי לאינטרנט דרך כתובת HTTPS מאובטחת; הוא דורש חשבון ngrok חינמי, ועליך להחליף את `YOUR_NGROK_DOMAIN.ngrok-free.dev` בדומיין השמור שלך:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. אימות המודל המקומי

ודא ש-Lemonade יכול להגיש את המודל שנבחר:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

לאחר מכן שלח בקשת צ'אט קטנה:

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
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

לאחר מכן שלח בקשת צ'אט קטנה:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

אם זה מחזיר מערך `choices`, Lemonade מוכן עבור Agent Canvas.

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
  "max_tokens": 64
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

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. הפעלת Agent Canvas

<!-- @os:linux -->
התקן את חבילת Agent Canvas המפורסמת והפעל את כל המחסנית:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

אם התקנת ה-npm הגלובלית נכשלת עם שגיאת הרשאות, עיין בערך פתרון בעיות הרשאות npm שלהלן.

כברירת מחדל, Agent Canvas מופעל בכתובת `http://localhost:8000`.
פתח כתובת זו בדפדפן שלך.
הפורט אינו מיוחד—אם 8000 כבר תפוס, העבר כל פורט פנוי עם `--port` (או `-p`).
הקצה העורפי המקומי המוגדר כברירת מחדל אמור להופיע כתקין במסך הבית.

> **הערה:** ההפעלה הראשונה בונה את סביבת ה-Python המנוהלת על ידי `uv` של Agent Server, כך שזה יכול לקחת כמה דקות לפני שהקצה העורפי מדווח כתקין.

הפקודה `agent-canvas` מפעילה יחד את שרת הסוכן, קצה העורף של האוטומציה ואת חזית האינטרנט.
אתה זקוק רק לפקודה אחת זו כדי להריץ את OpenHands באופן מקומי.
שאר מדריך זה מגדיר הכול דרך ממשק המשתמש של Agent Canvas בדפדפן שלך.
<!-- @os:end -->

<!-- @os:windows -->
ב-Windows, הרץ את תמונת הקונטיינר המפורסמת של Agent Canvas עם Docker Desktop.
התמונה כוללת את Agent Server, קצה העורף של האוטומציה וחזית האינטרנט, כך שאינך צריך להתקין Node.js,‏ `uv` או את ה-CLI במארח.

ראשית, צור את תיקיות התצורה וסביבת העבודה שהקונטיינר מעגן (mounts):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

משוך את התמונה המפורסמת (כ-6 ג'יגהבייט; היא ציבורית, כך שאין צורך בהתחברות):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

לאחר מכן הפעל את המחסנית:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

פתח את `http://localhost:8000/canvas` בדפדפן שלך.
אם פורט 8000 כבר תפוס, מפה פורט מארח שונה, לדוגמה `-p 8080:8000`, ופתח במקום זאת את `http://localhost:8080/canvas`.

> **הערה:** ההפעלה הראשונה בונה את סביבת Agent Server בתוך הקונטיינר, כך שזה יכול לקחת כמה דקות לפני שהקצה העורפי מדווח כתקין.

העיגון (mount) `.openhands` משמר את פרופיל ה-LLM שלך, שרתי MCP והאוטומציות שלך בין הפעלות מחדש של הקונטיינר.
שאר מדריך זה מגדיר הכול דרך ממשק המשתמש של Agent Canvas בדפדפן שלך בכתובת `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. הגדרת ה-LLM המקומי בממשק המשתמש

בהפעלה הראשונה, Agent Canvas פותח תהליך הכוונה (onboarding).
בתהליך זה:

1. השאירו את **OpenHands** נבחר כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר ל-**API key**.
4. הגדירו את **Custom Model** לערך `openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** לערך `http://127.0.0.1:13305/api/v1`.
6. עבור **API Key**, הזינו כל ערך ממלא-מקום שאינו ריק, כגון `lemonade-local`. Lemonade אינו דורש מפתח אמיתי, אך הלקוח של OpenHands צריך ערך כלשהו לשליחה.

<!-- @os:windows -->
> **Windows (Docker):** שרת הסוכן (Agent Server) פועל בתוך הקונטיינר, לכן יש להגדיר את **Base URL** לערך `http://host.docker.internal:13305/api/v1` במקום `http://127.0.0.1:13305/api/v1`.
> מבפנים הקונטיינר, הכתובת `127.0.0.1` מצביעה אל הקונטיינר עצמו; `host.docker.internal` מגיעה אל Lemonade שפועל על מארח ה-Windows, ו-Docker Desktop מספק את שם המארח הזה באופן אוטומטי.
<!-- @os:end -->

שדות החיבור אמורים להיראות כך.
שדה מפתח ה-API מוסתר על ידי הממשק.

![הגדרות LLM Advanced בשימוש ראשון ב-Agent Canvas עם מודל Lemonade וכתובת בסיס מקומית](assets/01-llm-advanced-settings.png)

לאחר מכן בחרו **All** והגדירו את שדות המודל המקומי הנוספים:

1. גללו אל **Custom Tokenizer** והגדירו אותו לערך `Qwen/Qwen3.6-35B-A3B`.
2. גללו אל **LiteLLM Extra Body** והגדירו אותו לערך `{"enable_thinking": true}`.
3. לחצו על **Next**.

![לשונית LLM All בשימוש ראשון ב-Agent Canvas עם ה-tokenizer המותאם אישית של Qwen](assets/02-llm-all-tokenizer-settings.png)

![לשונית LLM All בשימוש ראשון ב-Agent Canvas עם LiteLLM extra body מוגדר](assets/03-llm-all-extra-body-settings.png)

הגדרות ה-LLM אמורות להציג:

| שדה | ערך |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

הקידומת `openai/` אומרת ל-LiteLLM להשתמש בפורמט בקשות תואם-OpenAI מול נקודת הקצה של Lemonade.
ה-tokenizer המותאם אישית הוא ה-tokenizer המקורי של Hugging Face עבור מודל ה-GGUF; הוא מאפשר ל-OpenHands לספור את אותם טוקנים של תבנית הצ'אט (chat-template) שמודל השרת המקומי רואה.
טופס ה-LLM הנוכחי לשימוש ראשון אינו מציג הגדרות condenser.
אם בגרסת Agent Canvas שלכם מוצגות הגדרות condenser מאוחר יותר תחת **Settings > LLM**, השתמשו ב-`llm_summarizing` והגדירו מספר טוקנים מקסימלי מתחת לחלון ההקשר של Lemonade, כגון `56000`.

## 5. התקנת שרתי MCP עבור GitHub ו-Slack

בממשק המשתמש של Agent Canvas, פתחו את **Customize** (או **Settings > MCP**) כדי להוסיף את שרתי ה-MCP שמעניקים לסוכן כלים עבור GitHub ו-Slack.
ערכי הטוקנים נשלחים רק אל שרת הסוכן המקומי שלכם ונשמרים כהגדרות מוצפנות.

<!-- @os:windows -->
> **Windows (Docker):** פקודות שרת ה-MCP מסוג `npx` שבהמשך פועלות בתוך הקונטיינר, שכולל כבר Node.js, כך שלא מותקן דבר נוסף במארח.
> מכיוון ש-`.openhands` מחובר (mounted), שרתי ה-MCP והטוקנים שלהם נשמרים לאורך הפעלות מחדש של הקונטיינר.
<!-- @os:end -->

### שרת MCP עבור GitHub

הוסיפו שרת MCP חדש עם ההגדרות הבאות:

| שדה | ערך |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = טוקן ה-GitHub שלכם |

השתמשו בטוקן GitHub עם הרשאות קריאה למאגר שברצונכם לסכם.

### שרת MCP עבור Slack

הוסיפו שרת MCP שני עם ההגדרות הבאות:

| שדה | ערך |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = מזהה ערוץ ה-digest שלכם |

הגדירו את `SLACK_CHANNEL_IDS` למזהה ערוץ ה-digest (אותו ערך כמו `SLACK_DIGEST_CHANNEL`) כדי שהסוכן לא יצטרך לדפדף בכל ערוצי ה-Slack.

לאחר הוספת שני השרתים, השתמשו בכפתור **Test** בכל אחד מהם כדי לוודא שהוא מתחבר ומפרסם כלים.
שרת ה-GitHub אמור להציג רשימת כלי GitHub, ושרת ה-Slack אמור להציג רשימת כלי Slack.

![דף MCP ב-Agent Canvas עם שרתי GitHub ו-Slack מותקנים](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. יצירת אוטומציית ה-Digest

בממשק המשתמש של Agent Canvas, פתחו את דף **Automations** וצרו אוטומציה חדשה:

1. בחרו **Create automation** ובחרו בסוג **Prompt preset**.
2. הגדירו את **Name** לערך `GitHub Development Digest to Slack`.
3. הגדירו את **Prompt** לטקסט הבא, תוך החלפת ממלאי המקום של המאגר והערוץ בערכים שלכם:

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

4. הגדירו את **Trigger** לערך **Cron** עם לוח הזמנים `0 9 * * 1-5` (9 בבוקר בימי חול) והגדירו את **Timezone** לאזור הזמן שלכם, לדוגמה `America/New_York`.
5. הגדירו את **Timeout** לערך `900` שניות.
6. שמרו את האוטומציה.

דף פרטי האוטומציה מציג את האוטומציה החדשה עם טריגר ה-cron שלה ונקודת הכניסה שנוצרה עבור ה-prompt preset.

![דף פרטי האוטומציה ב-Agent Canvas לאחר היצירה](assets/05-automation-created.png)
## 7. בדיקת האוטומציה

מעמוד הפרטים של האוטומציה ב-Agent Canvas UI:

1. לחצו על **Run now** (או **Dispatch**) כדי להריץ את האוטומציה פעם אחת באופן מיידי.
2. צפו ברשימת ההרצות באותו עמוד. ההרצה האחרונה אמורה לעבור למצב `COMPLETED`.
3. פתחו את ערוץ ה-Slack היעד שלכם. הוא אמור להכיל את תקציר הסיכום שנוצר.

אין צורך להמתין להפעלת לוח הזמנים של ה-cron—**Run now** מפעיל הרצה לפי דרישה כך שתוכלו לוודא שהפרומפט, חיבורי ה-MCP ופרסום ההודעות ל-Slack כולם עובדים לפני ההסתמכות על לוח הזמנים.

![הרצת אוטומציה ב-Agent Canvas הושלמה בהצלחה](assets/06-automation-run-completed.png)

![ערוץ Slack המציג את תקציר OpenHands שנוצר](assets/07-slackbot-message.png)

## פתרון בעיות

<!-- @os:windows -->
- **פורט 8000 של Docker כבר בשימוש:** מפו פורט מארח אחר, לדוגמה `docker run ... -p 8080:8000 ...`, ופתחו את `http://localhost:8080/canvas`.
- **`docker pull` נכשל עם שגיאת אישורים** (לדוגמה, "A specified logon session does not exist"): הריצו את ה-pull מתוך סשן Windows אינטראקטיבי, או בצעו pre-pull לאימג'. האימג' ציבורי, כך שאין צורך ב-`docker login`.
- **ה-UI נטען אך ה-backend אינו תקין:** ההפעלה הראשונה בונה את סביבת Agent Server בתוך הקונטיינר. המתינו דקה ורעננו, ואז בדקו את `docker logs <container>` להתקדמות.
- **Agent Canvas אינו יכול להגיע ל-Lemonade מתוך הקונטיינר:** הגדירו את **Base URL** של ה-LLM ל-`http://host.docker.internal:13305/api/v1` (לא `127.0.0.1`), ואשרו ש-Lemonade פועל על מארח ה-Windows.
<!-- @os:end -->

- **Lemonade לא פעיל:** הפעילו אותו מחדש עם הפקודה `lemonade run "${LEMONADE_MODEL}"` משלב 1, ולאחר מכן הריצו שוב את בדיקת התקינות.
- **`npm install -g` נכשל עם שגיאת הרשאות:** ב-Linux או WSL, הגדירו ספריית npm גלובלית בבעלות המשתמש, הוסיפו אותה לקובץ ההפעלה של ה-shell שלכם, ולאחר מכן התקינו שוב את Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

אם אתם משתמשים ב-`zsh`, הוסיפו את אותה שורת `export PATH=...` לקובץ `~/.zshrc` במקום `~/.bashrc`.
- **Agent Canvas דוחה את הגדרות ה-LLM לאחר הגדרת `custom_tokenizer`:** התקינו את `transformers` בסביבת ה-Python של Agent Server, הפעילו מחדש את Agent Canvas אם נדרש, ונסו שוב לשמור את הגדרות ה-LLM. OpenHands דורש את Transformers כדי לטעון את תבנית הצ'אט של הטוקנייזר כאשר `custom_tokenizer` מוגדר.
- **Agent Canvas אינו יכול להגיע ל-Lemonade:** ודאו `curl -fsS "${LEMONADE_BASE_URL}/health"` ואשרו שכתובת ה-base URL שהוזנה בטופס ה-LLM בשימוש הראשון או ב-**Settings > LLM** תואמת לנקודת הקצה המקומית הפועלת או למנהרת ה-HTTPS.
- **הגדרות ה-LLM לא נשמרו:** ודאו שלחצתם על **Next** לאחר הזנת הערכים. פתחו מחדש את **Settings > LLM** כדי לאשר שהערכים נשמרו.
- **GitHub MCP אינו יכול לראות מאגרים (repositories) פרטיים:** ודאו שלטוקן ה-GitHub יש גישת קריאה למאגר היעד ושכפתור ה-**Test** של ה-MCP ב-**Customize** מציג כלי GitHub.
- **Slack יכול לקרוא ערוצים אך אינו יכול לפרסם:** הזמינו את אפליקציית ה-Slack לערוץ היעד ואשרו שלבוט יש `chat:write`.
- **האוטומציה מציגה יותר מדי ערוצי Slack:** השתמשו במזהה ערוץ Slack והגדירו `SLACK_CHANNEL_IDS` על שרת ה-Slack MCP ב-**Customize**.
- **הרצת האוטומציה נכשלת או חורגת מההקשר:** ודאו ש-Lemonade הופעל עם `ctx_size=65536`, ודאו של-LLM של OpenHands מוגדר `custom_tokenizer`, והשתמשו במאגר מפורש עם סטי תוצאות GitHub המוגבלים ל-3 עד 5 פריטים. אם גרסת ה-Agent Canvas שלכם חושפת הגדרות condenser, הגדירו את condenser max tokens מתחת לחלון ההקשר של Lemonade.

## השלבים הבאים

- הוסיפו תקציר שבועי המתמקד בגרסאות בלבד (release-only).
- הוסיפו אוטומציה המופעלת על ידי אירוע GitHub להתראות PR או push מהירות יותר.
- נתבו את אותו תקציר לתוך Notion, Linear, או כלי אחר המגובה על ידי MCP.

## משאבים

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [תיעוד Lemonade Server](https://lemonade-server.ai/docs)
- [מאגר ההרחבות של OpenHands](https://github.com/OpenHands/extensions)
- [שרתי Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [חבילת Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->