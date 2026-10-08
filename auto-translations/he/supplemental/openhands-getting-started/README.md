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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) הוא סוכן תוכנה מבוסס AI
שיכול לכתוב קוד, להריץ פקודות, לגלוש באינטרנט ולערוך קבצים בסביבת עבודה
אמיתית. במקום להעתיק הצעות מתוך חלון צ'אט, אתם מפנים את הסוכן לתיקיית פרויקט
ונותנים לו לבצע את העבודה: ליישם תכונה, לתקן באג, לכתוב בדיקות, או להסביר בסיס
קוד.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא ממשק הדפדפן
המומלץ להרצת OpenHands. פקודת `agent-canvas` יחידה מפעילה את שרת הסוכן, מנגנון
האוטומציה והממשק הקדמי של האינטרנט יחד, כך שתוכלו לנהל שיחה עם הסוכן מהדפדפן
שלכם.

כדי לשמור הכל על מערכת ה-AMD שלכם, הסוכן משוחח עם מודל מקומי שמוגש על ידי
Lemonade Server. Lemonade חושף את המודל הזה דרך API תואם OpenAI, כך ש-Agent
Canvas יכול להגדיר אותו כמו כל נקודת קצה אחרת בסגנון OpenAI, בעוד שהמודל, הקוד
שלכם וההקשר של השיחה נשארים כולם על המחשב שלכם.

בספר הדרכה זה, תתחילו מודל מקומי, תפעילו את Agent Canvas, תכוונו אותו לאותו
מודל, ותריצו את משימת הקידוד הראשונה שלכם מול תיקיית פרויקט אמיתית.

## מה תלמדו

- כיצד להפעיל את Lemonade Server ולוודא שמודל מקומי עונה לבקשות צ'אט
- כיצד להתקין ולהפעיל את Agent Canvas מחבילת ה-npm
- כיצד להגדיר את Agent Canvas להשתמש במודל Lemonade מקומי כ-LLM
- כיצד להתחיל שיחת OpenHands ולצפות בסוכן עורך קבצים ומריץ פקודות בסביבת עבודה
- כיצד לבדוק מה הסוכן שינה ולכוון אותו בעזרת הודעות המשך

## מושגי יסוד

| מושג | מה זה | היכן זה משתלב בספר ההדרכה הזה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת הגשת LLM מקומית שנבנתה עבור חומרת AMD, שחושפת API תואם OpenAI. הנתונים שלכם לעולם לא עוזבים את המחשב שלכם. | מריץ את המודל שמפעיל את הסוכן. |
| OpenHands | סוכן תוכנה מבוסס AI שקורא ועורך קבצים, מריץ פקודות מעטפת, וגולש באינטרנט בתוך סביבת עבודה. | הסוכן שאתם מנהלים מתוך הצ'אט. |
| Agent Canvas | ממשק הדפדפן והשרת האחורי שמריצים שיחות OpenHands ומציגים קריאות לכלים ושינויי קבצים. | מפעיל את המערכת ומארח את השיחה שלכם. |
| Workspace (סביבת עבודה) | תיקיית הפרויקט שהסוכן רשאי לקרוא ולשנות. | היעד לעריכות ולפקודות של הסוכן. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> זרימות עבודה של סוכן קידוד נהנות ממודל גדול יותר וחלון הקשר גדול יותר. השתמשו
> לפחות ב-32 GB של זיכרון מערכת, והעדיפו 64 GB או יותר עבור מודלי GGUF גדולים
> יותר.
<!-- @device:end -->

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקה לעדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## דרישות מוקדמות


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

אתם צריכים:

- Lemonade Server מותקן ומסוגל להגיש את המודל שלהלן.

<!-- @os:linux -->
- Node.js 22.12 ומעלה ו-`npm` (בשימוש על ידי כלי השורת הפקודה `agent-canvas`).
- `uv`, מנהל חבילות ה-Python ש-Agent Canvas משתמש בו כדי לנהל את סביבת שרת
  הסוכן. אם המערכת שלכם עדיין לא כוללת אותו, התקינו אותו מ[מדריך התקנת uv](https://docs.astral.sh/uv/getting-started/installation/)
  לפני הפעלת Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  מותקן ופועל. ב-Windows, המערכת של Agent Canvas פועלת מתוך תמונת ה-Docker
  המפורסמת, שכוללת את Node.js, `uv`, ואת החבילה `@openhands/agent-canvas`, כך
  שאינכם צריכים להתקין את אלה במחשב המארח.
<!-- @os:end -->

- תיקיית פרויקט לעבודה. זה יכול להיות כל מאגר git מקומי או תיקיית קוד שתרצו
  שהסוכן יעבוד עליה.

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

הפעילו את המודל מכלי השורת הפקודה של Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **בחרו מודל שמתאים לחומרה שלכם.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) הוא מודל קידוד חזק אך דורש מאגר זיכרון גדול. אם במכשיר שלכם יש זיכרון או VRAM מוגבל של GPU, בחרו במקום זאת מודל GGUF קטן יותר מספריית המודלים של Lemonade והשתמשו במזהה המודל הזה לאורך כל ספר ההדרכה.

> **הערה:** הרצת `lemonade run` הראשונה מורידה את המודל אם הוא עדיין לא קיים, מה שעשוי לקחת זמן בהתאם לגודל המודל ולחיבור שלכם.

Lemonade חושף API תואם OpenAI בכתובת:

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
## 3. התקנה והפעלה של Agent Canvas

<!-- @os:linux -->
התקינו את חבילת Agent Canvas המפורסמת באופן גלובלי:

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

לאחר מכן הפעילו את כל הערימה מתוך מסוף:

```bash
agent-canvas
```

כברירת מחדל, Agent Canvas עולה בכתובת `http://localhost:8000`. פתחו את הכתובת הזו
בדפדפן שלכם. הפורט אינו מיוחד — אם 8000 כבר תפוס, העבירו כל
פורט פנוי עם `--port` (או `-p`) בעת הפעלת Agent Canvas:

```bash
agent-canvas --port 3000
```

לאחר מכן פתחו במקום זאת את `http://localhost:3000`. ה-backend המקומי שבברירת המחדל אמור להופיע
כתקין במסך הבית.

הפקודה `agent-canvas` מפעילה את שרת הסוכן, את ה-backend של האוטומציה, ואת
חזית האינטרנט (frontend) יחד. תזדקקו רק לפקודה אחת זו כדי להריץ את OpenHands
באופן מקומי.

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
ב-Windows, הריצו את תמונת הקונטיינר המפורסמת של Agent Canvas באמצעות Docker Desktop.
התמונה כוללת את ה-Agent Server, את ה-backend של האוטומציה, ואת חזית האינטרנט, כך
שאינכם צריכים להתקין Node.js‏, `uv`, או את ה-CLI במארח.

ראשית, צרו את תיקיות התצורה (config) והסביבת העבודה (workspace) שהקונטיינר מעגן (mount):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

משכו (pull) את התמונה המפורסמת (היא ציבורית, כך שאין צורך בהתחברות):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

לאחר מכן הפעילו את הערימה:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

פתחו את `http://localhost:8000/canvas` בדפדפן שלכם. אם פורט 8000 כבר
תפוס, מפו פורט אחר במארח, לדוגמה `-p 8080:8000`, ופתחו במקום זאת את
`http://localhost:8080/canvas`.

> **הערה:** ההפעלה הראשונה מאתחלת את ה-Agent Server בתוך הקונטיינר,
> כך שייתכן שייקח דקה או שתיים עד שה-backend ידווח כתקין.

העיגון (mount) `.openhands` משמר את פרופיל ה-LLM וההגדרות שלכם בין הפעלות מחדש של הקונטיינר.
שאר ספר ההדרכה הזה מגדיר הכול דרך ממשק המשתמש של
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

בהפעלה הראשונה, Agent Canvas פותח תהליך onboarding. בתהליך זה:

1. השאירו את **OpenHands** נבחר כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר ל-**API key**.
4. הגדירו את **Custom Model** לערך `openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** לערך `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > ב-Windows הערימה פועלת בתוך קונטיינר, שאינו יכול להגיע למארח בכתובת
   > `127.0.0.1`. השתמשו במקום זאת ב-`http://host.docker.internal:13305/api/v1` כדי
   > שהסוכן שרץ בקונטיינר יוכל להגיע ל-Lemonade הרץ על מארח ה-Windows.
   <!-- @os:end -->
6. עבור **API Key**, הזינו ערך זמני כלשהו שאינו ריק, כגון `lemonade-local`.
   Lemonade אינו דורש מפתח אמיתי, אך לקוח ה-OpenHands זקוק לערך
   כדי לשלוח.
7. לחצו על **Next**.

הגדרות ה-Advanced המושלמות אמורות להיראות כך. שדה מפתח ה-API
מוסתר על ידי הממשק.

![הגדרות LLM Advanced של Agent Canvas בשימוש ראשון עם מודל Lemonade וכתובת בסיס מקומית](assets/01-llm-advanced-settings.png)

Agent Canvas שומר ערכים אלו כפרופיל LLM. אם הגרסה שלכם מבקשת שתציינו
שם לאותו פרופיל, השתמשו בשם ללא רווחים כגון `lemonade-local`. אם תשנו
מודלים מאוחר יותר, פתחו **Settings > LLM** ועדכנו את אותם שדות Advanced. תוכלו
לעבור בין פרופילים שמורים משדה הצ'אט עם הפקודה `/model`.

## 5. פתיחת סביבת עבודה (Workspace)

הסוכן יכול לקרוא ולשנות קבצים רק בתוך סביבת עבודה שתבחרו. לפני
התחלת משימה, הפנו את Agent Canvas לתיקיית הפרויקט שלכם:

1. במסך הבית, בחרו **Open Workspace**.
2. בחרו את התיקייה המכילה את הפרויקט שלכם (לדוגמה, מאגר git
   שעליו תרצו שהסוכן יעבוד).
3. התחילו שיחה חדשה באותה סביבת עבודה.

כל פעולה שהסוכן מבצע — קריאת קבצים, הרצת פקודות, עריכת קוד — מוגבלת
לאותה סביבת עבודה.

![מסך הבית של Agent Canvas לאחר ה-onboarding](assets/02-agent-canvas-home.png)

## 6. הרצת משימת קידוד ראשונה

כשסביבת העבודה פתוחה וה-LLM המקומי נבחר, הקלידו משימה קונקרטית בתוך
הצ'אט. משימה ראשונה טובה היא קטנה וניתנת לאימות, לדוגמה:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

עקבו אחר ציר הזמן של השיחה. OpenHands יבצע:

- קריאת סביבת העבודה כדי להבין את המבנה.
- יצירת `hello.py` עם הפונקציה המבוקשת וגוש הבדיקה.
- אופציונלית, הרצת `python3 hello.py` כדי לאמת את הפלט.
- דיווח על מה שבוצע ועל כל פלט פקודה בתוך הצ'אט.

אתם אמורים לראות את הקובץ החדש מופיע בסביבת העבודה, וההודעה הסופית של הסוכן
אמורה לתאר את השינוי שבוצע. זהו רגע התגמול: הסוכן
כתב והריץ קוד אמיתי בתיקיית הפרויקט שלכם.

## 7. סקירה והכוונה של הסוכן

לאחר שהסוכן מסיים שלב, סקרו את עבודתו לפני אישור השלב הבא:

- **שינויי קבצים**: השתמשו בדפדפן הקבצים של סביבת העבודה או בתצוגת ה-diff של הסוכן כדי
  לראות בדיוק מה נוסף, שונה, או נמחק.
- **פלט פקודות**: הרחיבו כל פקודה שהסוכן הריץ כדי לראות את stdout‏, stderr,
  ואת קוד היציאה (exit code).
- **המשכים**: אם התוצאה אינה מה שרציתם, השיבו באותה
  שיחה עם תיקון. הסוכן שומר את ההקשר הקודם
  וממשיך לעבוד על אותם קבצים.

לדוגמה, אם הבדיקה לא הדפיסה את הברכה המצופה, השיבו:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

הסוכן יקרא מחדש את הקובץ, יריץ את הפקודה, יאבחן את הבעיה, ויערוך
את הקובץ שוב — הכול באותה שיחה.
## פתרון בעיות

<!-- @os:linux -->
- **`agent-canvas` אינו נמצא ב-PATH:** התקינו מחדש באמצעות
  `npm install -g @openhands/agent-canvas` וודאו שספריית ה-binary הגלובלית של npm
  נמצאת ב-PATH שלכם לפני ש-`agent-canvas` יכול לפעול מטרמינל חדש.
- **`npm install -g` נכשל עם שגיאת הרשאות:** הגדירו ספריית npm גלובלית בבעלות המשתמש,
  לאחר מכן פתחו מחדש את הטרמינל והתקינו שוב את Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` חסר:** התקינו אותו מתוך
  [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas משתמש ב-`uv` לניהול סביבת הפייתון של שרת הסוכן.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` או `docker run` נכשלים בהתחברות:** ודאו ש-Docker Desktop
  פועל (סמל הלוויתן שלו נמצא במגש המערכת) ושהמנוע סיים להתחיל.
  `docker version` אמור להדפיס גם קטע Client וגם קטע Server.
- **הקונטיינר מתחיל אך ה-backend לעולם לא הופך לתקין:** ההפעלה הראשונה מאתחלת את
  Agent Server בתוך הקונטיינר; המתינו דקה-שתיים, ולאחר מכן בדקו
  `docker logs <container>` לאיתור שגיאות.
- **הקונטיינר אינו מצליח להגיע ל-Lemonade:** הקונטיינר מגיע למארח דרך
  `host.docker.internal`. ודאו ש-Lemonade משרת על מארח ה-Windows באמצעות
  `lemonade status`, והשתמשו ב-`http://host.docker.internal:13305/api/v1` כ-Base URL
  בעת הגדרת ה-LLM.
<!-- @os:end -->

- **ממשק המשתמש נטען אך ה-backend מוצג כלא תקין:** המתינו דקה-שתיים כדי ששרת
  הסוכן יסיים להתחיל, ואז רעננו. אם הוא נשאר לא תקין, הפעילו מחדש את המחסנית
  ובדקו את היומנים לאיתור שגיאות.
- **בקשות צ'אט של Lemonade נכשלות עם שגיאת חיבור:** ודאו ש-
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` מצליחה ושLemonade
  עדיין משרת את המודל באמצעות `lemonade status`.
- **הסוכן מחזיר שגיאה בנוגע לאורך הקשר או מגבלת טוקנים:** התחילו שיחה
  חדשה כך שהסוכן לא יישא היסטוריה גדולה מדי. אם זה ממשיך לקרות, הפעילו מחדש
  את Lemonade עם `ctx_size` גדול יותר מברירת המחדל 65536 (לדוגמה `ctx_size=131072`),
  בכפוף לזיכרון הזמין.
- **הסוכן מייצר עריכות באיכות נמוכה או לא שלמות:** עברו למודל גדול יותר ב-Lemonade,
  או תנו לסוכן משימה קטנה וקונקרטית יותר ותנו לו לסיים לפני שתבקשו את השינוי הבא.

## הצעדים הבאים

- נסו משימה גדולה יותר באותה סביבת עבודה, כגון הוספת קובץ בדיקת יחידה או
  תיקון באג ידוע, וסקרו את ה-diff של הסוכן לפני שמירת השינוי.
- חברו שרת MCP כגון GitHub או Slack תחת **Customize** כך שהסוכן
  יוכל לקרוא issues או לפרסם עדכונים בזמן העבודה.
- שמרו מספר פרופילי LLM (מודל קטן ומהיר ומודל גדול וחזק יותר) ועברו
  ביניהם באמצעות `/model` באמצע השיחה.
- המשיכו אל [אוטומציות OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) כדי
  להפוך לולאות פיתוח חוזרות להרצות סוכן מתוזמנות או מופעלות על ידי אירועים.

## משאבים

- [תיעוד OpenHands](https://docs.openhands.dev/)
- [סקירה כללית של Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [הגדרת Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [פרופילי LLM והגדרת מודלים](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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