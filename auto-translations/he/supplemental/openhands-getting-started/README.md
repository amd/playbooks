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
שיכול לכתוב קוד, להריץ פקודות, לגלוש באינטרנט ולערוך קבצים בסביבת עבודה אמיתית. במקום להעתיק
הצעות מתוך חלון צ'אט, מכוונים את הסוכן לתיקיית פרויקט ונותנים לו לבצע את העבודה: מימוש תכונה, תיקון
באג, כתיבת בדיקות או הסבר על בסיס קוד.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא ממשק הדפדפן המומלץ
להרצת OpenHands. פקודת `agent-canvas` יחידה מפעילה את שרת הסוכן, את הקצה האחורי לאוטומציה,
ואת הקצה הקדמי של האינטרנט יחד, כך שניתן לנהל שיחה עם הסוכן מהדפדפן שלכם.

כדי לשמור הכול על מערכת AMD שלכם, הסוכן מתקשר עם מודל מקומי המוגש
על ידי Lemonade Server. Lemonade חושף את המודל הזה באמצעות API תואם-OpenAI,
כך ש-Agent Canvas יכול להגדיר אותו כמו כל נקודת קצה אחרת בסגנון OpenAI, בעוד
המודל, הקוד שלכם והקשר השיחה נשארים כולם על המחשב שלכם.

במדריך זה, תפעילו מודל מקומי, תשיקו את Agent Canvas, תכוונו אותו
למודל הזה, ותריצו את משימת הקוד הראשונה שלכם על תיקיית פרויקט אמיתית.

## מה תלמדו

- כיצד להפעיל את Lemonade Server ולוודא שמודל מקומי עונה לבקשות צ'אט
- כיצד להתקין ולהשיק את Agent Canvas מחבילת ה-npm
- כיצד להגדיר את Agent Canvas להשתמש במודל Lemonade מקומי כ-LLM
- כיצד להתחיל שיחת OpenHands ולצפות בסוכן עורך קבצים ומריץ
  פקודות בסביבת עבודה
- כיצד לבחון מה הסוכן שינה ולכוון אותו בהודעות המשך

## מושגי יסוד

| מושג | מה זה | היכן הוא משתלב במדריך זה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת הגשת LLM מקומית שנבנתה עבור חומרת AMD וחושפת API תואם-OpenAI. הנתונים שלכם לעולם לא עוזבים את המחשב שלכם. | מריצה את המודל שמפעיל את הסוכן. |
| OpenHands | סוכן תוכנה מבוסס בינה מלאכותית שקורא ועורך קבצים, מריץ פקודות מעטפת, וגולש באינטרנט בתוך סביבת עבודה. | הסוכן שאתם מנהלים מהצ'אט. |
| Agent Canvas | ממשק הדפדפן והקצה האחורי המריצים שיחות OpenHands ומציגים קריאות כלים ושינויי קבצים. | משיק את המערכת ומארח את השיחה שלכם. |
| סביבת עבודה | תיקיית הפרויקט שהסוכן מורשה לקרוא ולשנות. | היעד של העריכות והפקודות של הסוכן. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> תהליכי עבודה של סוכן קידוד נהנים ממודל גדול יותר וחלון הקשר גדול יותר. השתמשו ב-
> לפחות 32 GB זיכרון מערכת, והעדיפו 64 GB או יותר עבור מודלי GGUF גדולים יותר.
<!-- @device:end -->

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## דרישות מוקדמות


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

תזדקקו ל:

- Lemonade Server מותקן ומסוגל להגיש את המודל שלהלן.

<!-- @os:linux -->
- Node.js 22.12 ומעלה ו-`npm` (בשימוש על ידי כלי שורת הפקודה `agent-canvas`).
- `uv`, מנהל חבילות ה-Python ש-Agent Canvas משתמש בו לניהול סביבת שרת
  הסוכן. אם המערכת שלכם עדיין לא מכילה אותו, התקינו אותו מתוך
  [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/)
  לפני השקת Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  מותקן ופועל. ב-Windows, מערכת Agent Canvas פועלת מתוך
  תמונת ה-Docker המפורסמת, הכוללת את Node.js, `uv`, וחבילת
  `@openhands/agent-canvas`, כך שלא צריך להתקין אותם על המארח.
<!-- @os:end -->

- תיקיית פרויקט לעבודה. זה יכול להיות כל מאגר git מקומי או ספריית קוד
  שברצונכם שהסוכן יעבוד עליה.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. הפעלת Lemonade Server

הפעילו את המודל מתוך שורת הפקודה של Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **בחרו מודל שמתאים לחומרה שלכם.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) הוא מודל קידוד חזק אך דורש מאגר זיכרון גדול. אם למכשיר שלכם יש זיכרון מוגבל או VRAM מוגבל של GPU, בחרו במקום זאת מודל GGUF קטן יותר מספריית המודלים של Lemonade והשתמשו במזהה המודל הזה לאורך כל המדריך.

> **הערה:** הפעלת `lemonade run` הראשונה מורידה את המודל אם הוא עדיין לא קיים, מה שעלול לקחת זמן בהתאם לגודל המודל ולחיבור שלכם.

Lemonade חושף API תואם-OpenAI בכתובת:

```text
http://127.0.0.1:13305/api/v1
```

## 2. אימות המודל המקומי

ודאו ש-Lemonade יכול להגיש את המודל שנבחר:

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. התקנה והפעלת Agent Canvas

<!-- @os:linux -->
התקינו את חבילת Agent Canvas שפורסמה באופן גלובלי:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

לאחר מכן הפעילו את מלוא הסטאק מתוך טרמינל:

```bash
agent-canvas
```

כברירת מחדל, Agent Canvas מופעל בכתובת `http://localhost:8000`. פתחו את הכתובת
הזו בדפדפן שלכם. הפורט אינו מיוחד — אם 8000 כבר תפוס, ציינו פורט פנוי כלשהו
עם `--port` (או `-p`) בעת הפעלת Agent Canvas:

```bash
agent-canvas --port 3000
```

לאחר מכן פתחו את `http://localhost:3000` במקום זאת. עבור ה-backend המקומי
כברירת מחדל אמור להופיע מצב תקין (healthy) במסך הבית.

הפקודה `agent-canvas` מפעילה יחד את שרת הסוכן (agent server), את ה-automation
backend ואת ה-web frontend. יש צורך בפקודה יחידה זו בלבד כדי להריץ את
OpenHands באופן מקומי.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
ב-Windows, הריצו את תמונת הקונטיינר המפורסמת של Agent Canvas עם Docker
Desktop. התמונה כוללת את Agent Server, את ה-automation backend ואת
ה-web frontend, כך שאין צורך להתקין Node.js, ‏`uv`, או את ה-CLI על המחשב
המארח (host).

ראשית, צרו את תיקיות ה-config וה-workspace שהקונטיינר יעגן (mount):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

משכו את התמונה שפורסמה (היא ציבורית, כך שאין צורך בהתחברות):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

לאחר מכן הפעילו את הסטאק:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

פתחו את `http://localhost:8000/canvas` בדפדפן שלכם. אם הפורט 8000 כבר תפוס,
מפו פורט אחר במחשב המארח, לדוגמה `-p 8080:8000`, ופתחו במקום זאת את
`http://localhost:8080/canvas`.

> **הערה:** ההפעלה הראשונה מאתחלת את Agent Server בתוך הקונטיינר, כך שייתכן
> שיחלפו דקה או שתיים לפני שה-backend ידווח על מצב תקין (healthy).

עיגון (mount) ה-`.openhands` שומר את פרופיל ה-LLM ואת ההגדרות שלכם בין
הפעלות מחדש של הקונטיינר. שאר המדריך הזה מגדיר את הכל דרך ממשק המשתמש של
Agent Canvas בדפדפן שלכם.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. הגדרת ה-LLM המקומי

בהפעלה הראשונה, Agent Canvas פותח תהליך onboarding. במהלך תהליך זה:

1. השאירו את **OpenHands** מסומן כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר כ-**API key**.
4. הגדירו את **Custom Model** כ-`openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** כ-`http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > ב-Windows הסטאק פועל בתוך קונטיינר, שאינו יכול להגיע אל המחשב המארח
   > בכתובת `127.0.0.1`. השתמשו במקום זאת ב-
   > `http://host.docker.internal:13305/api/v1` כדי שהסוכן המוכל בקונטיינר
   > יוכל להגיע אל Lemonade הרץ על מחשב Windows המארח.
   <!-- @os:end -->
6. עבור **API Key**, הזינו placeholder כלשהו שאינו ריק, כגון
   `lemonade-local`. Lemonade אינו דורש מפתח אמיתי, אך לקוח OpenHands זקוק
   לערך כלשהו לשליחה.
7. לחצו על **Next**.

הגדרות ה-Advanced המושלמות אמורות להיראות כך. שדה מפתח ה-API מוסתר (masked)
בממשק המשתמש.

![הגדרות LLM Advanced בשימוש ראשון של Agent Canvas עם מודל Lemonade וכתובת בסיס מקומית](assets/01-llm-advanced-settings.png)

Agent Canvas שומר את הערכים הללו כפרופיל LLM. אם הגרסה שלכם מבקשת מכם לתת שם
לפרופיל זה, השתמשו בשם ללא רווחים כגון `lemonade-local`. אם תשנו מודלים
בהמשך, פתחו את **Settings > LLM** ועדכנו את אותם שדות Advanced. ניתן להחליף
בין פרופילים שמורים משורת הצ'אט באמצעות הפקודה `/model`.

## 5. פתיחת Workspace

הסוכן יכול לקרוא ולשנות קבצים רק בתוך workspace שבחרתם. לפני התחלת משימה,
כוונו את Agent Canvas לתיקיית הפרויקט שלכם:

1. ממסך הבית, בחרו **Open Workspace**.
2. בחרו את התיקייה המכילה את הפרויקט שלכם (לדוגמה, מאגר git שברצונכם שהסוכן
   יעבוד עליו).
3. התחילו שיחה חדשה בתוך אותו workspace.

כל מה שהסוכן עושה—קריאת קבצים, הרצת פקודות, עריכת קוד—מוגבל לאותו workspace.

![מסך הבית של Agent Canvas לאחר ה-onboarding](assets/02-agent-canvas-home.png)

## 6. הרצת משימת התכנות הראשונה שלכם

עם ה-workspace פתוח וה-LLM המקומי נבחר, הקלידו משימה קונקרטית בצ'אט. משימה
ראשונה טובה היא קטנה וניתנת לאימות, לדוגמה:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

עקבו אחרי ציר הזמן של השיחה. OpenHands יבצע את הפעולות הבאות:

- יקרא את ה-workspace כדי להבין את המבנה שלו.
- ייצור את `hello.py` עם הפונקציה המבוקשת ובלוק הבדיקה.
- אופציונלית, יריץ `python3 hello.py` כדי לאמת את הפלט.
- ידווח מה עשה ואת פלט הפקודה בצ'אט.

אתם אמורים לראות את הקובץ החדש מופיע ב-workspace, וההודעה האחרונה של הסוכן
אמורה לתאר את השינוי שביצע. זהו רגע התגמול: הסוכן כתב והריץ קוד אמיתי בתיקיית
הפרויקט שלכם.

## 7. סקירה והכוונת הסוכן

לאחר שהסוכן מסיים שלב, סקרו את עבודתו לפני אישור השלב הבא:

- **שינויי קבצים**: השתמשו בדפדפן הקבצים של ה-workspace או בתצוגת ה-diff של
  הסוכן כדי לראות בדיוק מה נוסף, שונה, או נמחק.
- **פלט פקודות**: הרחיבו כל פקודה שהסוכן הריץ כדי לראות את ה-stdout,
  ה-stderr, ואת קוד היציאה (exit code).
- **המשך תהליך**: אם התוצאה אינה מה שרציתם, השיבו באותה שיחה עם תיקון. הסוכן
  שומר את ההקשר הקודם וממשיך לעבוד על אותם קבצים.

לדוגמה, אם הבדיקה לא הדפיסה את ברכת השלום המצופה, השיבו:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

הסוכן יקרא מחדש את הקובץ, יריץ את הפקודה, יאבחן את הבעיה, ויערוך את הקובץ
שוב—הכל באותה שיחה.
## פתרון בעיות

<!-- @os:linux -->
- **`agent-canvas` אינו נמצא ב-PATH:** יש להתקין מחדש באמצעות
  `npm install -g @openhands/agent-canvas` ולוודא שהתיקייה הגלובלית של npm
  נמצאת ב-PATH לפני שניתן יהיה להריץ את `agent-canvas` מטרמינל חדש.
- **`npm install -g` נכשל עם שגיאת הרשאות:** יש להגדיר תיקיית npm גלובלית
  בבעלות המשתמש, ולאחר מכן לפתוח מחדש את הטרמינל ולהתקין את Agent Canvas שוב.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` חסר:** יש להתקין אותו מתוך
  [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas משתמש ב-`uv` לניהול סביבת ה-Python של שרת הסוכן.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` או `docker run` נכשל בהתחברות:** יש לוודא ש-Docker Desktop
  פועל (סמל הלווייתן שלו נמצא במגש המערכת) ושהמנוע סיים את תהליך ההפעלה.
  `docker version` אמור להדפיס גם קטע Client וגם קטע Server.
- **הקונטיינר מופעל אך השרת האחורי (backend) אינו הופך לתקין:** ההפעלה
  הראשונה מאתחלת את שרת הסוכן (Agent Server) בתוך הקונטיינר; יש להמתין דקה
  או שתיים, ולאחר מכן לבדוק את `docker logs <container>` לאיתור שגיאות.
- **הקונטיינר אינו מצליח להגיע ל-Lemonade:** הקונטיינר מגיע למארח דרך
  `host.docker.internal`. יש לוודא ש-Lemonade מגיש שירות במארח Windows
  באמצעות `lemonade status`, ולהשתמש ב-`http://host.docker.internal:13305/api/v1`
  ככתובת Base URL בעת הגדרת ה-LLM.
<!-- @os:end -->

- **הממשק נטען אך השרת האחורי מוצג כלא תקין:** יש להמתין דקה או שתיים
  עד שהשרת הסוכן יסיים להיטען, ולאחר מכן לרענן. אם הבעיה נמשכת, יש להפעיל
  מחדש את המערכת ולבדוק את הלוגים לאיתור שגיאות.
- **בקשות שיחה (chat) ל-Lemonade נכשלות עם שגיאת חיבור:** יש לוודא ש-
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` מצליח וש-Lemonade עדיין
  מגיש את המודל, באמצעות `lemonade status`.
- **הסוכן מציג שגיאה בנוגע לאורך ההקשר או למגבלת אסימונים (tokens):** יש
  להתחיל שיחה חדשה כדי שהסוכן לא ישא היסטוריה גדולה מדי. אם התופעה חוזרת
  שוב, יש להפעיל מחדש את Lemonade עם `ctx_size` גדול יותר מברירת המחדל
  65536 (לדוגמה `ctx_size=131072`), אם הזיכרון מאפשר זאת.
- **הסוכן מפיק עריכות באיכות נמוכה או חלקיות:** יש לעבור למודל גדול יותר
  ב-Lemonade, או להעניק לסוכן משימה קטנה וממוקדת יותר ולתת לו לסיים אותה
  לפני שמבקשים את השינוי הבא.

## השלבים הבאים

- כדאי לנסות משימה גדולה יותר באותה סביבת עבודה, כגון הוספת קובץ בדיקת יחידה
  (unit test) או תיקון באג ידוע, ולסקור את ה-diff של הסוכן לפני שמאמצים את
  השינוי.
- ניתן לחבר שרת MCP כגון GitHub או Slack תחת **Customize** כדי שהסוכן יוכל
  לקרוא issues או לפרסם עדכונים תוך כדי עבודתו.
- ניתן לשמור מספר פרופילי LLM (מודל קטן ומהיר ומודל גדול וחזק יותר) ולעבור
  ביניהם באמצעות `/model` באמצע השיחה.
- כדאי להמשיך אל [אוטומציות של OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  כדי להפוך לולאות פיתוח חוזרות להרצות סוכן מתוזמנות או מופעלות על ידי אירועים.

## משאבים

- [תיעוד OpenHands](https://docs.openhands.dev/)
- [סקירת Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [הגדרת Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [פרופילי LLM והגדרות מודל](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [תיעוד Lemonade Server](https://lemonade-server.ai/docs)

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