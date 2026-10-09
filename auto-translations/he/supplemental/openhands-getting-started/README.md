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
אמיתית. במקום להעתיק הצעות מתוך חלון צ'אט, אתם מפנים את
הסוכן לתיקיית פרויקט ונותנים לו לבצע את העבודה: לממש תכונה, לתקן
באג, לכתוב בדיקות, או להסביר בסיס קוד.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא ממשק הדפדפן
המומלץ להרצת OpenHands. פקודת `agent-canvas` יחידה מפעילה את
שרת הסוכן, את גב התשתית (backend) של האוטומציה, ואת חזית הרשת (frontend) יחד, כך שניתן
לנהל שיחה עם הסוכן מתוך הדפדפן שלכם.

כדי לשמור הכול על מערכת ה-AMD שלכם, הסוכן מתקשר עם מודל מקומי המוגש
על ידי Lemonade Server. Lemonade חושף את אותו מודל דרך API
תואם OpenAI, כך ש-Agent Canvas יכול להגדיר אותו כמו כל נקודת קצה
בסגנון OpenAI אחרת, בעוד המודל, הקוד שלכם, והקשר השיחה כולם נשארים על
המכונה שלכם.

במדריך זה, תפעילו מודל מקומי, תשיקו את Agent Canvas, תפנו אותו
אל אותו מודל, ותריצו את משימת הקידוד הראשונה שלכם על תיקיית פרויקט אמיתית.

## מה תלמדו

- כיצד להפעיל את Lemonade Server ולאשר שמודל מקומי עונה על בקשות צ'אט
- כיצד להתקין ולהשיק את Agent Canvas מחבילת ה-npm
- כיצד להגדיר את Agent Canvas להשתמש במודל Lemonade מקומי כ-LLM
- כיצד להתחיל שיחת OpenHands ולצפות כיצד הסוכן עורך קבצים ומריץ
  פקודות בסביבת עבודה
- כיצד לסקור מה הסוכן שינה ולכוון אותו עם הודעות המשך

## מושגי יסוד

| מושג | מה זה | היכן זה משתלב במדריך זה |
| --- | --- | --- |
| Lemonade Server | פלטפורמת הגשה מקומית ל-LLM שנבנתה עבור חומרת AMD וחושפת API תואם OpenAI. המידע שלכם לעולם לא עוזב את המכונה שלכם. | מריצה את המודל שמפעיל את הסוכן. |
| OpenHands | סוכן תוכנה מבוסס בינה מלאכותית שקורא ועורך קבצים, מריץ פקודות מעטפת, וגולש באינטרנט בתוך סביבת עבודה. | הסוכן שאתם מנהלים מתוך הצ'אט. |
| Agent Canvas | ממשק הדפדפן וגב התשתית שמריצים שיחות OpenHands ומציגים קריאות כלים ושינויי קבצים. | משיק את מערך הכלים ומארח את השיחה שלכם. |
| סביבת עבודה (Workspace) | תיקיית הפרויקט שהסוכן רשאי לקרוא ולשנות. | היעד של העריכות והפקודות של הסוכן. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> תהליכי עבודה של סוכן קידוד נהנים ממודל גדול יותר וחלון הקשר גדול יותר. השתמשו ב
> לפחות 32 ג"ב של זיכרון מערכת, והעדיפו 64 ג"ב או יותר עבור מודלי GGUF גדולים יותר.
<!-- @device:end -->

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## דרישות מוקדמות


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

דרוש לכם:

- Lemonade Server מותקן ומסוגל להגיש את המודל שלהלן.

<!-- @os:linux -->
- Node.js 22.12 ומעלה ו-`npm` (בשימוש כלי שורת הפקודה `agent-canvas`).
- `uv`, מנהל חבילות ה-Python ש-Agent Canvas משתמש בו כדי לנהל את
  סביבת שרת הסוכן. אם המערכת שלכם עדיין לא כוללת אותו, התקינו אותו מתוך
  [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/)
  לפני השקת Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  מותקן ופעיל. ב-Windows, מערך הכלים של Agent Canvas פועל מתוך
  תמונת ה-Docker הפרסומית, הכוללת Node.js, `uv`, וחבילת
  `@openhands/agent-canvas`, כך שלא צריך להתקין אותם על המארח.
<!-- @os:end -->

- תיקיית פרויקט לעבודה. זו יכולה להיות כל מאגר git מקומי או תיקיית
  קוד שברצונכם שהסוכן יעבוד עליה.

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

הפעילו את המודל מתוך ממשק שורת הפקודה (CLI) של Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **בחרו מודל שמתאים לחומרה שלכם.** `Qwen3.6-35B-A3B-GGUF` (כ-20 ג"ב) הוא מודל קידוד חזק אך דורש מאגר זיכרון גדול. אם במכשיר שלכם יש זיכרון מוגבל או זיכרון וידאו (VRAM) מוגבל ל-GPU, בחרו במקום זאת מודל GGUF קטן יותר מספריית המודלים של Lemonade והשתמשו במזהה המודל הזה לאורך כל המדריך.

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

אם התגובה כוללת מערך `choices`, Lemonade מוכן עבור Agent Canvas.

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

לאחר מכן הפעילו את כל הסטאק מטרמינל:

```bash
agent-canvas
```

כברירת מחדל, Agent Canvas עולה בכתובת `http://localhost:8000`. פתחו כתובת זו
בדפדפן שלכם. הפורט אינו מיוחד — אם 8000 כבר תפוס, העבירו כל פורט פנוי
באמצעות `--port` (או `-p`) בעת הפעלת Agent Canvas:

```bash
agent-canvas --port 3000
```

לאחר מכן פתחו את `http://localhost:3000` במקום זאת. הבאק-אנד המקומי שבברירת המחדל
אמור להופיע כתקין במסך הבית.

הפקודה `agent-canvas` מפעילה יחד את שרת הסוכן, את הבאק-אנד לאוטומציה, ואת
חזית האינטרנט. אתם זקוקים רק לפקודה אחת זו כדי להריץ את OpenHands
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
ב-Windows, הריצו את קונטיינר Image הפרסום של Agent Canvas עם Docker Desktop.
ה-Image כולל את ה-Agent Server, הבאק-אנד לאוטומציה, וחזית האינטרנט, כך
שאינכם צריכים להתקין Node.js, `uv`, או את ה-CLI על המארח.

ראשית, צרו את תיקיות התצורה וסביבת העבודה שהקונטיינר יעגן (mount):

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

משכו את ה-image המפורסם (הוא ציבורי, כך שלא נדרשת התחברות):

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

פתחו את `http://localhost:8000/canvas` בדפדפן שלכם. אם פורט 8000 כבר תפוס,
מפו פורט מארח אחר, לדוגמה `-p 8080:8000`, ופתחו את
`http://localhost:8080/canvas` במקום זאת.

> **הערה:** ההפעלה הראשונה מאתחלת את ה-Agent Server בתוך הקונטיינר,
> כך שזה עשוי לקחת דקה או שתיים לפני שהבאק-אנד מדווח כתקין.

העיגון (mount) של `.openhands` שומר את פרופיל ה-LLM וההגדרות שלכם בין
הפעלות מחדש של הקונטיינר. שאר חוברת ההדרכה הזו מגדירה הכול דרך
ממשק המשתמש של Agent Canvas בדפדפן שלכם.

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

בהפעלה הראשונה, Agent Canvas פותח תהליך הכוונה (onboarding). בתהליך זה:

1. השאירו את **OpenHands** נבחר כסוכן ולחצו על **Next**.
2. במסך **Set up your LLM**, בחרו **Advanced**.
3. השאירו את **Authentication** מוגדר כ-**API key**.
4. הגדירו את **Custom Model** לערך `openai/Qwen3.6-35B-A3B-GGUF`.
5. הגדירו את **Base URL** לערך `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > ב-Windows הסטאק רץ בתוך קונטיינר, שאינו יכול להגיע למארח בכתובת
   > `127.0.0.1`. השתמשו במקום זאת בכתובת `http://host.docker.internal:13305/api/v1`
   > כך שהסוכן המוכל בקונטיינר יוכל להגיע ל-Lemonade הרץ על מארח ה-Windows.
   <!-- @os:end -->
6. עבור **API Key**, הזינו כל ערך ממלא-מקום שאינו ריק, כמו `lemonade-local`.
   Lemonade אינו דורש מפתח אמיתי, אך לקוח OpenHands זקוק לערך כלשהו
   לשליחה.
7. לחצו על **Next**.

הגדרות ה-Advanced המושלמות אמורות להיראות כך. שדה מפתח ה-API מוסתר
על ידי הממשק.

![הגדרות LLM מתקדמות בשימוש ראשון ב-Agent Canvas עם מודל Lemonade וכתובת בסיס מקומית](assets/01-llm-advanced-settings.png)

Agent Canvas שומר ערכים אלה כפרופיל LLM. אם הגרסה שלכם מבקשת מכם לתת
שם לפרופיל זה, השתמשו בשם ללא רווחים כגון `lemonade-local`. אם תחליפו
מודלים מאוחר יותר, פתחו את **Settings > LLM** ועדכנו את אותם שדות Advanced. תוכלו
להחליף בין פרופילים שמורים משדה הצ'אט באמצעות הפקודה `/model`.

## 5. פתיחת סביבת עבודה (Workspace)

הסוכן יכול לקרוא ולשנות קבצים רק בתוך סביבת עבודה שתבחרו. לפני
התחלת משימה, הפנו את Agent Canvas לתיקיית הפרויקט שלכם:

1. ממסך הבית, בחרו **Open Workspace**.
2. בחרו את התיקייה המכילה את הפרויקט שלכם (לדוגמה, מאגר git
   שעליו תרצו שהסוכן יעבוד).
3. התחילו שיחה חדשה בסביבת עבודה זו.

כל מה שהסוכן עושה—קריאת קבצים, הרצת פקודות, עריכת קוד—מוגבל
לסביבת העבודה הזו.

![מסך הבית של Agent Canvas לאחר ההכוונה](assets/02-agent-canvas-home.png)

## 6. הרצת משימת הקידוד הראשונה שלכם

כאשר סביבת העבודה פתוחה וה-LLM המקומי נבחר, הקלידו משימה קונקרטית לתוך
הצ'אט. משימה ראשונה טובה היא קטנה וניתנת לאימות, לדוגמה:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

צפו בציר הזמן של השיחה. OpenHands יבצע:

- קריאת סביבת העבודה כדי להבין את המבנה.
- יצירת `hello.py` עם הפונקציה המבוקשת ובלוק הבדיקה.
- הרצה אופציונלית של `python3 hello.py` כדי לאמת את הפלט.
- דיווח על מה שעשה וכל פלט פקודה בצ'אט.

אתם אמורים לראות את הקובץ החדש מופיע בסביבת העבודה, וההודעה הסופית
של הסוכן אמורה לתאר את השינוי שביצע. זהו רגע התגמול: הסוכן כתב
והריץ קוד אמיתי בתיקיית הפרויקט שלכם.

## 7. סקירה והכוונת הסוכן

לאחר שהסוכן מסיים שלב, סקרו את עבודתו לפני אישור השלב הבא:

- **שינויי קבצים**: השתמשו בדפדפן הקבצים של סביבת העבודה או בתצוגת ה-diff
  של הסוכן כדי לראות בדיוק מה נוסף, שונה, או נמחק.
- **פלט פקודות**: הרחיבו כל פקודה שהסוכן הריץ כדי לראות את ה-stdout, ה-stderr,
  וקוד היציאה.
- **המשכים**: אם התוצאה אינה מה שרציתם, השיבו באותה
  שיחה עם תיקון. הסוכן שומר על ההקשר הקודם
  וממשיך לעבוד על אותם קבצים.

לדוגמה, אם הבדיקה לא הדפיסה את ברכת השלום הצפויה, השיבו:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

הסוכן יקרא מחדש את הקובץ, יריץ את הפקודה, יאבחן את הבעיה, ויערוך
את הקובץ שוב—הכול באותה שיחה.
## פתרון בעיות

<!-- @os:linux -->
- **`agent-canvas` לא נמצא ב-PATH:** התקינו מחדש באמצעות
  `npm install -g @openhands/agent-canvas` וודאו שתיקיית הבינארי הגלובלי של npm
  נמצאת ב-PATH שלכם לפני ש-`agent-canvas` יכול להיות מופעל מטרמינל חדש.
- **`npm install -g` נכשל עם שגיאת הרשאות:** הגדירו תיקיית npm גלובלית בבעלות המשתמש,
  ולאחר מכן פתחו מחדש את הטרמינל והתקינו שוב את Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` חסר:** התקינו אותו מתוך
  [מדריך ההתקנה של uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas משתמש ב-`uv` כדי לנהל את סביבת ה-Python של שרת הסוכן.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` או `docker run` נכשלים בחיבור:** ודאו ש-Docker Desktop
  פועל (סמל הלוויתן שלו נמצא במגש המערכת) ושהמנוע סיים את האתחול. `docker version`
  אמור להדפיס גם קטע Client וגם קטע Server.
- **הקונטיינר עולה אך ה-backend אף פעם לא הופך לתקין:** ההפעלה הראשונה מאתחלת את
  Agent Server בתוך הקונטיינר; תנו לזה דקה או שתיים, ולאחר מכן בדקו את
  `docker logs <container>` לאיתור שגיאות.
- **הקונטיינר לא מצליח להגיע ל-Lemonade:** הקונטיינר מגיע למארח דרך
  `host.docker.internal`. ודאו ש-Lemonade משרת ב-host של Windows באמצעות
  `lemonade status`, והשתמשו ב-`http://host.docker.internal:13305/api/v1` בתור
  ה-Base URL בעת הגדרת ה-LLM.
<!-- @os:end -->

- **הממשק נטען אך ה-backend מוצג כלא תקין:** המתינו דקה או שתיים עד שהשרת של הסוכן
  מסיים לעלות, ולאחר מכן רעננו. אם הוא נשאר לא תקין, הפעילו מחדש את הסטאק ובדקו
  את הלוגים לאיתור שגיאות.
- **בקשות צ'אט של Lemonade נכשלות עם שגיאת חיבור:** ודאו ש-
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` מצליח ושש-Lemonade עדיין
  משרת את המודל באמצעות `lemonade status`.
- **הסוכן מחזיר שגיאה של אורך הקשר או מגבלת טוקנים:** התחילו שיחה חדשה כדי שהסוכן
  לא ישאת היסטוריה גדולה מדי. אם זה ממשיך לקרות, הפעילו מחדש את Lemonade עם
  `ctx_size` גדול יותר מברירת המחדל 65536 (לדוגמה `ctx_size=131072`), אם הזיכרון
  מאפשר זאת.
- **הסוכן מייצר עריכות באיכות נמוכה או לא שלמות:** עברו למודל גדול יותר ב-Lemonade,
  או תנו לסוכן משימה קטנה וקונקרטית יותר ותנו לו לסיים אותה לפני שתבקשו את השינוי הבא.

## השלבים הבאים

- נסו משימה גדולה יותר באותה סביבת עבודה, כגון הוספת קובץ בדיקת יחידה או
  תיקון באג ידוע, וסקרו את ה-diff של הסוכן לפני שמירת השינוי.
- חברו שרת MCP כגון GitHub או Slack תחת **Customize** כדי שהסוכן
  יוכל לקרוא issues או לפרסם עדכונים בזמן שהוא עובד.
- שמרו מספר פרופילי LLM (מודל קטן ומהיר ומודל גדול וחזק יותר) ועברו
  ביניהם באמצעות `/model` באמצע שיחה.
- המשיכו אל [אוטומציות של OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) כדי
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