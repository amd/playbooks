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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## סקירה כללית

מפתחים מבלים זמן רב בלולאות חוזרות וקטנות: סקירת בקשות משיכה (pull requests) מתויגות, מענה לתגובות ב-GitHub, מיון בעיות חדשות, הפיכת שרשורי Slack לתקצירי סטטוס יומי או מעקבי תקריות, ומעקב אחר אותות שחרור או מחקר.
כל לולאה מוכרת, אך עדיין דורשת שיקול דעת: איסוף ההקשר הנכון, החלטה מה חשוב, ופרסום עדכון ברור במקום שבו הצוות כבר עובד.

[אוטומציות של OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) הופכות לולאות אלו לשיחות סוכן מתוזמנות או מופעלות באירוע: ריצות שבהן סוכן תוכנה מבוסס בינה מלאכותית יכול לקרוא הקשר, לקרוא לכלים, וליצור עדכון.
תבניות האוטומציה המשותפות בקטלוג ההרחבות של OpenHands עוקבות אחר דפוס זה עבור סקירת בקשות משיכה ב-GitHub, מעקב אחר מאגרים, מיון בעיות ב-Linear, סיכומי תקריות, תקצירי סטטוס יומי ב-Slack, ותקצירי מחקר: אוטומציה מתעוררת, משתמשת באינטגרציות מוגדרות כגון GitHub או Slack כדי לאחזר הקשר, מנתחת את ההקשר הזה באמצעות מודל שפה גדול (LLM), וכותבת בחזרה תוצאה.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא מישור הבקרה המקומי לבניית ובדיקת אוטומציות אלו.
במדריך זה הוא מריץ OpenHands Agent Server, תהליך הקצה האחורי שמבצע שיחות סוכן, ומחבר את הסוכן לשירותים חיצוניים כגון GitHub ו-Slack.

כדי לשמור על זרימת העבודה במערכת ה-AMD שלך, הסוכן מדבר עם מודל מקומי המוגש על ידי Lemonade Server.
Lemonade חושף את המודל הזה דרך API תואם-OpenAI, כך ש-Agent Canvas יכול להגדיר אותו כנקודת קצה מרוחקת בסגנון OpenAI, בעוד שהמודל, ה-prompt, והקשר זרימת העבודה נשארים מקומיים.

במדריך זה, תבנה אוטומציה קונקרטית אחת: תקציר פיתוח מתוזמן מ-GitHub ל-Slack.
הוא משתמש ב-GitHub כדי לבדוק פעילות מאגר אחרונה, ב-Slack כדי לפרסם את התקציר, בקריאות API של Agent Canvas כדי להגדיר ולבדוק את האוטומציה, וב-Lemonade כדי להריץ את ה-LLM מקומית.

![תרשים ארכיטקטורה המציג GitHub MCP, אוטומציית OpenHands, Lemonade Server, ו-Slack MCP](assets/00-architecture-overview.png)

## מה תלמד

- כיצד להפעיל את Lemonade Server ולוודא שמודל מקומי עונה לבקשות צ'אט
- כיצד להפעיל את Agent Canvas ולהצביע את Agent Server שלו למודל LLM מקומי
- כיצד להתקין שרתי Model Context Protocol (MCP) עבור GitHub ו-Slack דרך ה-API של Agent Server
- כיצד ליצור ולהפעיל אוטומציית OpenHands מתוזמנת שמפרסמת תקציר פיתוח ל-Slack
- כיצד לפתור את הכשלים הנפוצים ביותר הקשורים למודל מקומי ואוטומציה

## מושגי יסוד

| מושג | מה זה | היכן זה משתלב במדריך זה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת הגשת LLM מקומית שנבנתה עבור חומרת AMD וחושפת API תואם-OpenAI. הנתונים שלך לעולם לא יוצאים מהמכונה שלך. | מריץ את המודל שמפעיל את הסוכן. |
| OpenHands Agent Server | תהליך הקצה האחורי שמבצע שיחות סוכן של OpenHands. | מארח את הסוכן, פרופיל ה-LLM שלו, ושרתי ה-MCP שלו. |
| Agent Canvas | מישור הבקרה המקומי של OpenHands שמריץ את Agent Server וממשק משתמש לבדיקת ריצות סוכן. | מפעיל את הקצוות האחוריים ומספק את ה-API שאתה קורא לו. |
| שרת MCP | שרת Model Context Protocol שנותן לסוכן כלים עבור שירות חיצוני כגון GitHub או Slack. | מאפשר לסוכן לקרוא מ-GitHub ולכתוב ל-Slack. |
| אוטומציית OpenHands | שיחת סוכן מתוזמנת או מופעלת באירוע שמאחזרת הקשר, מנתחת אותו, וכותבת תוצאה לאנשהו. | תקציר ה-GitHub-ל-Slack שאתה בונה כאן. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> זרימות עבודה של סוכן קידוד נהנות ממודל גדול יותר וחלון הקשר רחב יותר.
> השתמש לפחות ב-32 ג'יגה-בייט זיכרון מערכת, ועדיף 64 ג'יגה-בייט או יותר עבור מודלי GGUF גדולים יותר.
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
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

עליך:

- להתקין את Lemonade Server על ידי ביצוע [מדריך ההתקנה הסטנדרטי של Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ומעלה ו-`npm`, המשמשים להתקנת ה-CLI המפורסם של Agent Canvas ולהרצת שרתי MCP באמצעות `npx`.
- `uv`, מנהל חבילות ה-Python ש-Agent Canvas משתמש בו כדי לבנות את סביבת Agent Server. אם הוא עדיין לא מותקן, התקן אותו מתוך [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).
- חבילת `@openhands/agent-canvas` מפורסמת ועדכנית עם הגדרות סוכן מבוססות סכמה, `LLMSummarizingCondenserSettings.max_tokens`, ותמיכה ב-`custom_tokenizer` של LLM.
- חבילת ה-Python `transformers` זמינה בסביבת Agent Server. היא נדרשת לספירת אסימונים (token) של תבניות צ'אט כאשר `custom_tokenizer` מוגדר.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop עבור Windows](https://docs.docker.com/desktop/setup/install/windows-install/), מותקן ופועל. ב-Windows, ערימת Agent Canvas פועלת מתוך תמונת ה-Docker המפורסמת, הכוללת את Node.js, `uv`, `transformers`, וחבילת `@openhands/agent-canvas`, כך שאינך צריך להתקין אותם במארח.
<!-- @os:end -->

- טוקן GitHub עם גישת קריאה למאגר שברצונך לסכם.
- טוקן בוט Slack (`xoxb-...`) עם `chat:write` וגישת קריאה לערוץ.
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

שני משתנים אלה משמשים בפקודות האימות שלהלן.
המודל, ה-tokenizer והגדרות LLM אחרות מוזנות ישירות בממשק Agent Canvas UI בשלבים מאוחרים יותר, כך שהערכים המילוליים שלהם מוצגים inline במקום שבו תזדקקו להם.

הערכים הבאים מוזנים בממשק Agent Canvas UI בשלבים מאוחרים יותר.
הגדירו אותם כאן כדי שתוכלו להעתיק אותם:

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

השתמשו בערך מפורש בצורת `owner/repo` עבור `GITHUB_REPO_FILTER`.
תווי wildcard רחבים ברמת הארגון עלולים להחזיר יותר מדי הקשר MCP עבור מודלים מקומיים.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. הפעלת שרת Lemonade

הפעילו את המודל מתוך ה-Lemonade CLI:

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

> **בחרו מודל המתאים לחומרה שלכם.** `Qwen3.6-35B-A3B-GGUF` (כ-20GB) הוא מודל חזק לתהליך עבודה זה אך דורש מאגר זיכרון גדול.
> אם למכשיר שלכם יש זיכרון מוגבל או VRAM מוגבל של ה-GPU, בחרו מודל GGUF קטן יותר מספריית המודלים של Lemonade והשתמשו במזהה המודל הזה (ובה-tokenizer המתאים לו) לאורך כל המדריך הזה.

> **הערה:** ההרצה הראשונה של `lemonade run` מורידה את המודל אם הוא עדיין לא קיים, מה שעשוי לקחת זמן מה בהתאם לגודל המודל ולחיבור שלכם.

Lemonade חושף API תואם-OpenAI בכתובת:

```text
http://127.0.0.1:13305/api/v1
```

אופציונלי: אם Agent Canvas או מריץ האוטומציה אינם על אותה מכונה, פרסמו את ה-endpoint של Lemonade דרך מנהרה מאובטחת והשתמשו בכתובת ה-HTTPS ככתובת הבסיס (base URL) של ה-LLM.
[ngrok](https://ngrok.com/) חושף פורט מקומי לאינטרנט דרך כתובת HTTPS מאובטחת; הוא דורש חשבון ngrok חינמי, ואתם מחליפים את `YOUR_NGROK_DOMAIN.ngrok-free.dev` בדומיין השמור שלכם:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. אימות המודל המקומי

ודאו ש-Lemonade יכול להגיש את המודל הנבחר:

<!-- @os:linux -->
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
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

לאחר מכן שלחו בקשת צ'אט קטנה:

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
התקינו את חבילת Agent Canvas המפורסמת והפעילו את כל המחסנית (stack):

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

אם התקנת ה-npm הגלובלית נכשלת עם שגיאת הרשאות, עיינו בפריט פתרון בעיות הרשאות npm שלהלן.

כברירת מחדל, Agent Canvas מופעל בכתובת `http://localhost:8000`.
פתחו את הכתובת הזו בדפדפן שלכם.
הפורט אינו מיוחד—אם 8000 כבר תפוס, העבירו כל פורט פנוי באמצעות `--port` (או `-p`).
הבק-אנד המקומי כברירת מחדל אמור להופיע כתקין במסך הבית.

> **הערה:** ההפעלה הראשונה בונה את סביבת הפייתון המנוהלת על ידי `uv` של Agent Server, כך שזה עשוי לקחת כמה דקות לפני שהבק-אנד יתעד כתקין.

הפקודה `agent-canvas` מפעילה את שרת הסוכן, בק-אנד האוטומציה, ואת ה-frontend של האתר יחד.
אתם זקוקים רק לפקודה אחת זו כדי להריץ את OpenHands באופן מקומי.
שאר המדריך הזה מגדיר את הכול דרך ממשק Agent Canvas UI בדפדפן שלכם.
<!-- @os:end -->

<!-- @os:windows -->
ב-Windows, הריצו את תמונת הקונטיינר המפורסמת של Agent Canvas עם Docker Desktop.
התמונה כוללת את Agent Server, בק-אנד האוטומציה, ואת ה-frontend של האתר, כך שאינכם צריכים להתקין Node.js, `uv`, או ה-CLI על המארח.

ראשית, צרו את תיקיות התצורה וסביבת העבודה שהקונטיינר מצמיד (mounts):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

משכו את התמונה המפורסמת (כ-6GB; היא ציבורית, כך שאין צורך בהתחברות):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

לאחר מכן הפעילו את המחסנית (stack):

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

פתחו את `http://localhost:8000/canvas` בדפדפן שלכם.
אם פורט 8000 כבר תפוס, מפו פורט מארח אחר, לדוגמה `-p 8080:8000`, ופתחו במקום זאת את `http://localhost:8080/canvas`.

> **הערה:** ההפעלה הראשונה בונה את סביבת Agent Server בתוך הקונטיינר, כך שזה עשוי לקחת כמה דקות לפני שהבק-אנד יתעד כתקין.

ההצמדה (mount) `.openhands` שומרת על פרופיל ה-LLM שלכם, שרתי ה-MCP, והאוטומציות שלכם לאורך הפעלות מחדש של הקונטיינר.
שאר המדריך הזה מגדיר את הכול דרך ממשק Agent Canvas UI בדפדפן שלכם בכתובת `http://localhost:8000/canvas`.
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

בהפעלה הראשונה, Agent Canvas פותח תהליך onboarding.
בתהליך זה:

1. השאירו את **OpenHands** נבחר כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר ל-**API key**.
4. הגדירו את **Custom Model** לערך `openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** לערך `http://127.0.0.1:13305/api/v1`.
6. עבור **API Key**, הזינו placeholder כלשהו שאינו ריק, כגון `lemonade-local`. Lemonade אינו דורש מפתח אמיתי, אבל לקוח ה-OpenHands זקוק לערך כלשהו כדי לשלוח.

<!-- @os:windows -->
> **Windows (Docker):** שרת ה-Agent פועל בתוך הקונטיינר, לכן הגדירו את **Base URL** לערך `http://host.docker.internal:13305/api/v1` במקום `http://127.0.0.1:13305/api/v1`.
> מתוך הקונטיינר, `127.0.0.1` מתייחס לקונטיינר עצמו; `host.docker.internal` מגיע ל-Lemonade הרץ על מארח ה-Windows, ו-Docker Desktop מספק את שם המארח הזה אוטומטית.
<!-- @os:end -->

שדות החיבור אמורים להיראות כך.
שדה ה-API key מוסתר על ידי הממשק.

![הגדרות LLM Advanced בשימוש ראשון ב-Agent Canvas עם מודל Lemonade וכתובת base URL מקומית](assets/01-llm-advanced-settings.png)

לאחר מכן בחרו **All** והגדירו את שדות המודל המקומי הנוספים:

1. גללו אל **Custom Tokenizer** והגדירו אותו לערך `Qwen/Qwen3.6-35B-A3B`.
2. גללו אל **LiteLLM Extra Body** והגדירו אותו לערך `{"enable_thinking": true}`.
3. לחצו על **Next**.

![כרטיסיית LLM All בשימוש ראשון ב-Agent Canvas עם ה-custom tokenizer של Qwen](assets/02-llm-all-tokenizer-settings.png)

![כרטיסיית LLM All בשימוש ראשון ב-Agent Canvas עם LiteLLM extra body מוגדר](assets/03-llm-all-extra-body-settings.png)

הגדרות ה-LLM אמורות להציג:

| שדה | ערך |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

הקידומת `openai/` מורה ל-LiteLLM להשתמש בפורמט בקשות תואם OpenAI מול נקודת הקצה של Lemonade.
ה-custom tokenizer הוא ה-tokenizer המקורי של Hugging Face עבור מודל ה-GGUF; הוא מאפשר ל-OpenHands לספור את אותם טוקנים של chat-template שרואה שרת המודל המקומי.
טופס ה-LLM הנוכחי בשימוש ראשון אינו מציג הגדרות condenser.
אם גרסת ה-Agent Canvas שלכם חושפת הגדרות condenser בהמשך תחת **Settings > LLM**, השתמשו ב-`llm_summarizing` והגדירו מספר טוקנים מקסימלי מתחת לחלון ההקשר של Lemonade, כגון `56000`.

## 5. התקנת שרתי MCP של GitHub ו-Slack

בממשק המשתמש של Agent Canvas, פתחו את **Customize** (או **Settings > MCP**) כדי להוסיף את שרתי ה-MCP שמעניקים לסוכן כלים עבור GitHub ו-Slack.
ערכי הטוקן נשלחים רק לשרת ה-Agent המקומי שלכם ונשמרים כהגדרות מוצפנות.

<!-- @os:windows -->
> **Windows (Docker):** פקודות שרת ה-MCP מסוג `npx` שלהלן פועלות בתוך הקונטיינר, שכבר כולל Node.js, כך שלא מותקן דבר נוסף על המארח.
> מכיוון ש-`.openhands` מחובר (mounted), שרתי ה-MCP והטוקנים שלהם נשמרים גם לאחר הפעלות מחדש של הקונטיינר.
<!-- @os:end -->

### שרת ה-MCP של GitHub

הוסיפו שרת MCP חדש עם ההגדרות הבאות:

| שדה | ערך |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = טוקן ה-GitHub שלכם |

השתמשו בטוקן GitHub עם הרשאת קריאה ל-repository שברצונכם לסכם.

### שרת ה-MCP של Slack

הוסיפו שרת MCP שני עם ההגדרות הבאות:

| שדה | ערך |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = מזהה ערוץ ה-digest שלכם |

הגדירו את `SLACK_CHANNEL_IDS` למזהה ערוץ ה-digest (אותו ערך כמו `SLACK_DIGEST_CHANNEL`) כדי שהסוכן לא יצטרך לעבור על כל ערוצי ה-Slack.

לאחר הוספת שני השרתים, השתמשו בכפתור **Test** בכל אחד מהם כדי לאשר שהוא מתחבר ומפרסם כלים (tools).
שרת ה-GitHub אמור להציג כלי GitHub, ושרת ה-Slack אמור להציג כלי Slack.

![עמוד MCP ב-Agent Canvas עם שרתי GitHub ו-Slack מותקנים](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. יצירת אוטומציית ה-Digest

בממשק המשתמש של Agent Canvas, פתחו את עמוד ה-**Automations** וצרו אוטומציה חדשה:

1. בחרו **Create automation** ובחרו את הסוג **Prompt preset**.
2. הגדירו את ה-**Name** לערך `GitHub Development Digest to Slack`.
3. הגדירו את ה-**Prompt** לטקסט הבא, תוך החלפת ה-placeholder-ים של ה-repository והערוץ בערכים שלכם:

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

4. הגדירו את ה-**Trigger** ל-**Cron** עם לוח הזמנים `0 9 * * 1-5` (9 בבוקר בימי חול) והגדירו את ה-**Timezone** לאזור הזמן שלכם, לדוגמה `America/New_York`.
5. הגדירו את ה-**Timeout** לערך `900` שניות.
6. שמרו את האוטומציה.

עמוד פרטי האוטומציה מציג את האוטומציה החדשה עם ה-trigger מסוג cron וה-entrypoint שנוצר מסוג prompt-preset.

![עמוד פרטי אוטומציה ב-Agent Canvas לאחר יצירה](assets/05-automation-created.png)
## 7. בדיקת האוטומציה

מדף הפרטים של האוטומציה בממשק Agent Canvas UI:

1. לחצו על **Run now** (או **Dispatch**) כדי להריץ את האוטומציה פעם אחת באופן מיידי.
2. עקבו אחר רשימת ההרצות באותו עמוד. ההרצה האחרונה אמורה לעבור למצב `COMPLETED`.
3. פתחו את ערוץ ה-Slack היעד שלכם. הוא אמור להכיל את הדיגסט שנוצר.

אין צורך להמתין להפעלת לוח הזמנים של cron—**Run now** מפעיל הרצה לפי דרישה כך שתוכלו לוודא שה-prompt, חיבורי ה-MCP, והפרסום ב-Slack כולם עובדים לפני ההסתמכות על לוח הזמנים.

![הרצת אוטומציה ב-Agent Canvas הושלמה בהצלחה](assets/06-automation-run-completed.png)

![ערוץ Slack מציג את הדיגסט שנוצר עבור OpenHands](assets/07-slackbot-message.png)

## פתרון בעיות

<!-- @os:windows -->
- **פורט Docker 8000 כבר בשימוש:** מפו פורט מארח אחר, למשל `docker run ... -p 8080:8000 ...`, ופתחו את `http://localhost:8080/canvas`.
- **`docker pull` נכשל עם שגיאת אישורים** (לדוגמה, "A specified logon session does not exist"): הריצו את ה-pull מתוך סשן Windows אינטראקטיבי, או בצעו pull מראש לאימג'. האימג' ציבורי, כך שאין צורך ב-`docker login`.
- **הממשק נטען אך ה-backend אינו תקין:** ההפעלה הראשונה בונה את סביבת ה-Agent Server בתוך הקונטיינר. המתינו דקה ורעננו, ואז בדקו את `docker logs <container>` להתקדמות.
- **Agent Canvas אינו מצליח להגיע ל-Lemonade מתוך הקונטיינר:** הגדירו את ה-**Base URL** של ה-LLM ל-`http://host.docker.internal:13305/api/v1` (לא `127.0.0.1`), ואמתו ש-Lemonade פועל על מארח Windows.
<!-- @os:end -->

- **Lemonade לא פועל:** הפעילו אותו מחדש עם הפקודה `lemonade run "${LEMONADE_MODEL}"` משלב 1, ואז הריצו שוב את בדיקת התקינות.
- **`npm install -g` נכשל עם שגיאת הרשאות:** ב-Linux או WSL, הגדירו תיקיית npm גלובלית בבעלות המשתמש, הוסיפו אותה לקובץ ההפעלה של ה-shell שלכם, ולאחר מכן התקינו שוב את Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

אם אתם משתמשים ב-`zsh`, הוסיפו את אותה שורת `export PATH=...` ל-`~/.zshrc` במקום ל-`~/.bashrc`.
- **Agent Canvas דוחה את הגדרות ה-LLM לאחר הגדרת `custom_tokenizer`:** התקינו `transformers` בסביבת ה-Python של ה-Agent Server, הפעילו מחדש את Agent Canvas אם נדרש, ונסו שוב לשמור את הגדרות ה-LLM. OpenHands דורש את Transformers כדי לטעון את תבנית הצ'אט של ה-tokenizer כאשר `custom_tokenizer` מוגדר.
- **Agent Canvas אינו מצליח להגיע ל-Lemonade:** אמתו `curl -fsS "${LEMONADE_BASE_URL}/health"` ווודאו שה-base URL שהוזן בטופס ה-LLM בשימוש הראשון או ב-**Settings > LLM** תואם לנקודת הקצה המקומית הפועלת או למנהרת HTTPS.
- **הגדרות ה-LLM לא נשמרו:** ודאו שלחצתם על **Next** לאחר הזנת הערכים. פתחו מחדש את **Settings > LLM** כדי לאמת שהערכים נשמרו.
- **GitHub MCP אינו רואה מאגרים פרטיים:** אמתו שלטוקן GitHub יש גישת קריאה למאגר היעד ושכפתור ה-**Test** של ה-MCP ב-**Customize** מפרסם כלי GitHub.
- **Slack יכול לקרוא ערוצים אך לא יכול לפרסם:** הזמינו את אפליקציית ה-Slack לערוץ היעד ואמתו שלבוט יש `chat:write`.
- **האוטומציה מציגה רשימה ארוכה מדי של ערוצי Slack:** השתמשו במזהה ערוץ Slack והגדירו `SLACK_CHANNEL_IDS` בשרת ה-Slack MCP ב-**Customize**.
- **הרצת האוטומציה נכשלת או חורגת מההקשר:** אמתו ש-Lemonade הופעל עם `ctx_size=65536`, אמתו של-LLM של OpenHands מוגדר `custom_tokenizer`, והשתמשו במאגר מפורש עם סטים של תוצאות GitHub מוגבלים ל-3 עד 5 פריטים. אם בגרסת ה-Agent Canvas שלכם קיימות הגדרות condenser, הגדירו את מספר הטוקנים המקסימלי של ה-condenser מתחת לחלון ההקשר של Lemonade.

## הצעדים הבאים

- הוסיפו דיגסט שבועי המיועד רק לשחרורי גרסאות (release-only).
- הוסיפו אוטומציה המופעלת על ידי אירועי GitHub להתראות מהירות יותר על PR או push.
- נתבו את אותו דיגסט ל-Notion, Linear, או כלי אחר מבוסס MCP.

## משאבים

- [ספרי המשחק של AMD AI](https://developer.amd.com/playbooks/)
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