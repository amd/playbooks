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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> מדריך זה דורש לפחות **32GB** של זיכרון מערכת.
<!-- @device:end -->

## סקירה כללית

[Open WebUI](https://docs.openwebui.com) הוא ממשק מבוסס דפדפן, המתארח באופן עצמאי, המספק חוויית צ'אטבוט מוכרת תוך שהוא משמש כחזית עבור שרת מודל AI אחד או יותר. במקום להיות מוגבל לספק אחד, Open WebUI יכול להתחבר ל**כל backend החושף API תואם OpenAI**, כך שניתן להחליף מודלים ויכולות מבלי להחליף ממשקי משתמש.

במדריך זה, אנו משתמשים ב-[**Lemonade**](https://lemonade-server.ai) כ-backend מכיוון שהוא חושף **נקודת קצה מאוחדת תואמת OpenAI** התומכת במספר מודליות:
- **מודלי שפה גדולים (LLMs)** ליצירת טקסט
- **מודלי ראייה** להבנת תמונות
- **Stable Diffusion** ליצירת תמונות
- **מודלי תמלול שמע** להמרת דיבור לטקסט

הגדרה זו מאפשרת לך לחקור את **זרימת העבודה המולטימודלית המלאה מקצה לקצה**.

---

## מה תלמדו

בסיום, תוכלו:

- לחבר את Open WebUI ל-backend מקומי תואם OpenAI (Lemonade)
- לשוחח עם LLM מקומי מהדפדפן שלכם
- להעלות תמונה ולשאול מודל ראייה שאלות עליה
- ליצור תמונות מהנחיות טקסט באמצעות מודלי Stable Diffusion (SDXL-Turbo / SDXL)
- להבין את המודל המנטלי כדי שתוכלו להשתמש ב-backends אחרים (Ollama, vLLM, llama.cpp server וכו')

---

## מושגי יסוד (מודל מנטלי)

### שלושת הרכיבים

| רכיב | מה הוא עושה | דוגמאות |
|---|---|---|
| חזית (UI) | אפליקציית האינטרנט שאיתה אתם מקיימים אינטראקציה | Open WebUI |
| Backend (שרת מודלים) | מארח מודלים וחושף נקודות קצה HTTP | Lemonade, Ollama, vLLM, llama.cpp server, שרתים תואמי OpenAI |
| מודלים | ה-LLM / הראייה / הדיפוזיה / השמע בפועל | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### מדוע "API תואם OpenAI" חשוב

Open WebUI בנוי סביב נקודות קצה בסגנון OpenAI סטנדרטי, כגון:
  - צ'אט: `/chat/completions`
  - רשימת מודלים: `/models`
  - יצירת תמונות: `/images/generations`
  - תמלול שמע: `/audio/transcriptions`

Lemonade חושף אלה תחת `http://localhost:13305/api/v1/...`

אם backend תומך בנקודות קצה אלה, Open WebUI יכול לתקשר איתו עם הגדרה מינימלית. זו הסיבה שאנחנו יכולים להחליף backends מבלי לשנות את זרימת העבודה שלנו.

#### שני שירותים, שני יציאות

לאורך מדריך זה תעבדו עם שני שירותים נפרדים:

| שירות | כתובת URL | מה עושים שם |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | לעיין, להוריד ולנהל מודלים |
| **Open WebUI** | `http://localhost:8080` | צ'אט, העלאת תמונות, יצירת תמונות — הממשק הפונה למשתמש |

Lemonade מריץ את המודלים; Open WebUI הוא הממשק שאיתו אתם מקיימים אינטראקציה. השתמשו תחילה ב-GUI של Lemonade כדי להוריד את המודלים שלכם, ולאחר מכן השתמשו בהם מתוך Open WebUI.

---

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## הגדרה חד-פעמית

מדריך זה דורש הפעלת Lemonade כ-backend וכן, ב-Linux, מנוע קונטיינרים (Podman) להרצת Open WebUI. הגדירו אלה לפני התקנת Open WebUI.

<!-- @os:windows -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade -->
<!-- @device:end -->
---
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade,podman -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade,podman -->
<!-- @device:end -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
---
<!-- @device:end -->
<!-- @os:end -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## הורדת מודלים ב-Lemonade

לפני התקנת Open WebUI, ודאו שהמודלים בהם ברצונכם להשתמש הורדו ומוכנים ב-Lemonade.

1. פתחו את ה-GUI של Lemonade בכתובת `http://localhost:13305`.
2. עיינו במודלים הזמינים והורידו את אלה שברצונכם להשתמש בהם (למשל, LLM לצ'אט, מודל ראייה, ו/או מודל Stable Diffusion ליצירת תמונות).
3. ודאו שה-API נגיש על ידי ביקור בכתובת `http://localhost:13305/api/v1/models` בדפדפן שלכם — אמורים להופיע שם המודלים שהורדתם.

> מודלים חייבים להיות מורדים ב-**Lemonade** (`localhost:13305`) לפני שיוכלו להופיע ב-**Open WebUI** (`localhost:8080`). אם מודל לא מופיע ב-Open WebUI מאוחר יותר, חזרו לכאן ובדקו תחילה ב-Lemonade.


<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3-4B-Hybrid",
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3-4B-Hybrid"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=openwebui-lemonade-multimodal-smoke-linux timeout=1800 hidden=True -->
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
import base64, json, os, sys, urllib.request

data = json.loads(os.environ["MODELS_JSON"])
required = [
  "Qwen3.5-4B-GGUF",
  "SDXL-Turbo",
]

by_id = {m.get("id"): m for m in data.get("data", [])}
for mid in required:
  m = by_id.get(mid)
  if not m:
    print(f"Model {mid} is not present in /api/v1/models. Please download it.")
    sys.exit(1)
  if not m.get("downloaded", False):
    print(f"Model {mid} is present but not downloaded. Please download it.")
    sys.exit(1)
  print(f"OK: {mid} is downloaded")

def post_json(url, payload, timeout=300):
  req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
      "Content-Type": "application/json",
      "Authorization": "Bearer -",
    },
    method="POST",
  )
  try:
    with urllib.request.urlopen(req, timeout=timeout) as r:
      return json.loads(r.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    raise SystemExit(f"POST {url} failed with HTTP {e.code}. Response body:\n{body}")

# LLM chat smoke test
chat = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500,
  "stream": False,
}, timeout=300)
text = chat["choices"][0]["message"]["content"]
if "OK" not in text:
  raise SystemExit(f"LLM chat test failed. Got: {text}")
print("OK: LLM chat works")

# Vision smoke test (OpenAI image_url format)
png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png1x1
vision = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "If you can see an image input, reply with exactly: OK"},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 256,
}, timeout=300)
if not vision.get("choices"):
  raise SystemExit(f"Unexpected vision response (no choices). Raw response:\n{json.dumps(vision, indent=2)}")
vtext = vision["choices"][0]["message"].get("content", "")
if not vtext.strip():
  raise SystemExit(f"Vision returned empty content. Raw response:\n{json.dumps(vision, indent=2)}")
if "OK" not in vtext:
  raise SystemExit(f"Vision test failed. Got: {vtext}\nRaw response:\n{json.dumps(vision, indent=2)}")
print("OK: Vision chat works")

# Image generation smoke test
img = post_json("http://127.0.0.1:13305/api/v1/images/generations", {
  "model": "SDXL-Turbo",
  "prompt": "A simple red cube on a white table, studio lighting",
  "size": "256x256",
  "steps": 4,
  "response_format": "b64_json",
}, timeout=900)
b64 = img.get("data", [{}])[0].get("b64_json")
if not b64:
  raise SystemExit("Image generation did not return data[0].b64_json")
print("OK: Image generation works")
PY
```
<!-- @test:end --> 
<!-- @os:end --> 

## התקנת Open WebUI

<!-- @os:windows -->
### 1. התקנת Python 3.12

Open WebUI דורש **Python 3.12** — הוא לא מתקין על Python 3.13 ומעלה. ה-Windows Python Launcher (`py`) מאפשר לכם להתקין 3.12 לצד כל גרסת Python קיימת ללא התנגשויות.

```powershell
winget install Python.Python.3.12
```

סגרו ופתחו מחדש את הטרמינל לאחר ההתקנה, ולאחר מכן אמתו:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **הערה:** במערכת שלכם מותקן מראש Python 3.13. התקנת 3.12 אינה משפיעה עליו — `python` ממשיך להשתמש ב-3.13, ו-`py -3.12` מכוון ל-3.12 רק כשאתם זקוקים לו.
<!-- @device:end -->

<!-- @test:id=python-env-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$v = (& py -3.12 --version) 2>&1
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 was not found. Install it with: winget install Python.Python.3.12" }
if ($v -notmatch "Python 3\.12\.") { throw "Expected Python 3.12.x but got: $v" }

Write-Host "OK: $v"
```
<!-- @test:end --> 

### 2. יצירת סביבה וירטואלית והתקנת Open WebUI

```powershell
mkdir openwebui
cd openwebui
py -3.12 -m venv openwebui-venv
.\openwebui-venv\Scripts\activate
pip install open-webui beautifulsoup4
```

<!-- @test:id=openwebui-install-venv-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $work | Out-Null

Push-Location $work
try {
  py -3.12 -m venv openwebui-venv
  $py = Join-Path $work "openwebui-venv\Scripts\python.exe"

  & $py -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }

  & $py -m pip install open-webui beautifulsoup4
  if ($LASTEXITCODE -ne 0) { throw "pip install open-webui beautifulsoup4 failed" }

  Write-Host "OK: open-webui installed in venv"
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 

<!-- @test:id=openwebui-install-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$py = Join-Path $venv "Scripts\python.exe"

& $py -c "import open_webui; print('OK: import open_webui')"
& $py -c "import bs4; print('OK: bs4 import')"
```
<!-- @test:end --> 

<!-- @test:id=openwebui-cli-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"

if (-not (Test-Path $ow)) { throw "open-webui.exe not found at $ow" }

& $ow --help | Out-Null
Write-Host "OK: open-webui CLI is available"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
כעת נשתמש בשירות Podman כדי להריץ את התקנת Open WebUI שלנו בתוך קונטיינר.

הורידו את הקובץ הבא לתיקייה לבחירתכם: [compose.yml](assets/compose.yml)

באותה תיקייה, הריצו את הפקודה הבאה:

```bash
podman compose up -d
```

פעולה זו מושכת את תמונת Open WebUI וכותבת לאחסון קבוע.

הפעילו את Open WebUI על ידי הקלדת `localhost:8080` בשורת הכתובת של הדפדפן שלכם.

<!-- @test:id=openwebui-podman-prereq-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

podman --version
podman compose version
podman info >/dev/null

if [ ! -f compose.yml ]; then
  echo "compose.yml not found in current working directory (playbooks/supplemental/open-webui-chat/assets)"
  exit 1
fi

echo "OK: Podman, Podman Compose, and compose.yml are available"
```
<!-- @test:end -->

<!-- @test:id=openwebui-compose-validate-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys
import yaml

path = Path("compose.yml")
if not path.exists():
    raise SystemExit("compose.yml not found")

data = yaml.safe_load(path.read_text())
svc = data.get("services", {}).get("open-webui")
if not svc:
    raise SystemExit("compose.yml does not define services.open-webui")

expected_image = "ghcr.io/open-webui/open-webui:main"
if svc.get("image") != expected_image:
    raise SystemExit(f"Expected image {expected_image}, got {svc.get('image')}")

if svc.get("container_name") != "open-webui":
    raise SystemExit("Expected container_name: open-webui")

if svc.get("network_mode") != "host":
    raise SystemExit("Expected network_mode: host")

volumes = svc.get("volumes", [])
if "open_webui_data:/app/backend/data" not in volumes:
    raise SystemExit("Expected open_webui_data:/app/backend/data volume mount")

if "open_webui_data" not in data.get("volumes", {}):
    raise SystemExit("Expected top-level open_webui_data volume")

print("OK: compose.yml matches the Open WebUI Podman setup")
PY

podman compose -f compose.yml config >/dev/null

echo "OK: podman compose can parse compose.yml"
```
<!-- @test:end -->
<!-- @os:end -->

> **טיפ**: Open WebUI מציע גם אפשרויות התקנה נוספות ב-[GitHub](https://github.com/open-webui/open-webui) שלהם.
## הפעלת שרת Open WebUI

<!-- @os:windows -->
- הריצו את הפקודה הבאה כדי להפעיל את שרת ה-HTTP של Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- בדפדפן, נווטו אל `http://localhost:8080`.
- Open WebUI יבקש מכם ליצור חשבון מנהל מקומי. לאחר ההתחברות, תראו את ממשק הצ'אט.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> השאירו את חלון הטרמינל פתוח. סגירתו תעצור את Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> הקונטיינר פועל ברקע. מהתיקייה המכילה את `compose.yml`, ניתן לנהל אותו באמצעות `podman compose down` (עצירה) ו-`podman compose up -d` (הפעלה). החשבונות וההגדרות שלכם נשמרים ב-volume בשם `open_webui_data`.
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openwebui-server-smoke-windows timeout=900 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"
if (-not (Test-Path $ow)) { throw "open-webui not found. Run openwebui-install-venv-windows first." }

# Fresh data dir so auth mode/config isn't polluted by previous runs
$dataDir = Join-Path $work "openwebui-data-ci"
if (Test-Path $dataDir) { Remove-Item -Recurse -Force $dataDir }
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

$env:DATA_DIR = $dataDir
$env:WEBUI_AUTH = "False" # Disable auth for CI
$env:ENABLE_PERSISTENT_CONFIG = "False" # Ensure environment-variable config applies for the run and isn't overridden by persistent settings

$logOut = Join-Path $work "openwebui-ci-out.log"
$logErr = Join-Path $work "openwebui-ci-err.log"
$p = Start-Process -FilePath $ow -ArgumentList "serve --port 8080" -NoNewWindow -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
try {
  $ok = $false
  for ($i=0; $i -lt 90; $i++) {
    $health = curl.exe -s --max-time 2 http://127.0.0.1:8080/health
    if ($health) { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "Open WebUI not ready on http://127.0.0.1:8080" }
  Write-Host "OK: Open WebUI is responding on /health"
}
finally {
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=openwebui-podman-server-smoke-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Clean up a stale container from a previous failed run.
podman rm -f open-webui >/dev/null 2>&1 || true

podman compose -f compose.yml up -d

health=""
for i in $(seq 1 180); do
  health="$(curl -fsS --max-time 2 http://127.0.0.1:8080/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Open WebUI did not become ready on http://127.0.0.1:8080/health"
  echo "Container status:"
  podman ps -a || true
  echo "Open WebUI logs:"
  podman logs --tail 200 open-webui || true
  exit 1
fi

echo "OK: Open WebUI container is responding on /health"

# Verify that the Open WebUI container can reach Lemonade through host networking.
podman exec open-webui sh -lc 'python -c "import json, urllib.request; data=json.load(urllib.request.urlopen(\"http://127.0.0.1:13305/api/v1/models\", timeout=10)); assert \"data\" in data; print(\"OK: Open WebUI container can reach Lemonade models endpoint\")"'
```
<!-- @test:end --> 
<!-- @os:end --> 

## חיבור Open WebUI ל-Lemonade

כעת ששני השירותים פועלים — Lemonade בכתובת `localhost:13305` ו-Open WebUI בכתובת `localhost:8080` — יש לחבר ביניהם כדי ש-Open WebUI יוכל להשתמש במודלים של Lemonade.

ב-Open WebUI:

1. לחצו על **סמל פרופיל המשתמש** בפינה הימנית העליונה, ולאחר מכן בחרו **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. בפאנל ההגדרות, לחצו על **Admin Settings** בפינה השמאלית התחתונה.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. בסרגל הצד של Admin Settings, לחצו על **Connections** (או נווטו ישירות אל `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. תחת **OpenAI API**, הוסיפו חיבור חדש:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (מקף בודד עובד עבור שימוש מקומי)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. ודאו שתחת **"Manage OpenAI API Connections"**, רק `http://localhost:13305/api/v1` מופעל. השביתו כל חיבור אחר (למשל, חיבור ברירת המחדל של OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. לחצו על **Save**.

7. **(מומלץ)** השביתו תכונות יצירה אוטומטיות כדי לשמור על תגובתיות Open WebUI עם מודלי LLM מקומיים. עברו אל **Admin Settings → Settings → Interface** וכבו את:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. לחצו על **Save**, ולאחר מכן חזרו אל `http://localhost:8080`.
9. לחצו על תפריט המודלים הנפתח — אמורים להופיע המודלים שהורדתם מ-Lemonade.

---

## פעילויות עיקריות

כעת הכל מוכן. הבה נבחן שלוש פעילויות מעניינות.

---

### פעילות 1: שיחה עם LLM מקומי
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. לחצו על תפריט הנפתח בפינה השמאלית העליונה של הממשק. יוצגו המודלים של Lemonade שהתקנתם. בחרו אחד כדי להמשיך (לדוגמה: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. הזינו הודעה ל-LLM ולחצו על שליחה (או הקישו Enter). ה-LLM ייקח מספר שניות להיטען לזיכרון ולאחר מכן תראו את התגובה זורמת פנימה.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. לחצו על תפריט הנפתח בפינה השמאלית העליונה של הממשק. יוצגו המודלים של Lemonade שהתקנתם. בחרו אחד כדי להמשיך (לדוגמה: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. הזינו הודעה ל-LLM ולחצו על שליחה (או הקישו Enter). ה-LLM ייקח מספר שניות להיטען לזיכרון ולאחר מכן תראו את התגובה זורמת פנימה.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. המודל יגיב בצ'אט.

4. בשלב זה, פתחו את `Task Manager` במערכת שלכם. תראו **ניצול גבוה של GPU או NPU** בהתאם לכך אם המודל שבחרתם הוא **Hybrid** או **NPU** בהתאמה. באמצעות מנהל המשימות, תוכלו לאשר שאתם מריצים את המודל באופן מקומי.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. לחצו על תפריט הנפתח בפינה השמאלית העליונה של הממשק. יוצגו המודלים של Lemonade שהתקנתם. בחרו אחד כדי להמשיך (לדוגמה: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. הזינו הודעה ל-LLM ולחצו על שליחה (או הקישו Enter). ה-LLM ייקח מספר שניות להיטען לזיכרון ולאחר מכן תראו את התגובה זורמת פנימה.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. המודל יגיב בצ'אט.
<!-- @os:end -->

זה מוודא ש-Open WebUI יכול לשלוח בקשות ל-Lemonade באמצעות נקודת הקצה של הצ'אט התואמת ל-OpenAI.

---

### פעילות 2: העלאת תמונה ושאילת שאלות (ראייה)

זה דורש מודל התומך בקלט תמונה (מודל Vision או Multimodal).

1. לחצו על סמל הסינון, בחרו "By Category", ולאחר מכן בחרו מודל מתוך קטע ה-**Vision** (לדוגמה: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. לחצו על כפתור ה-**`+`** בתיבת ההודעה והעלו תמונה
3. שאלו משהו שמחייב הבנה אמיתית של התמונה: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. המודל עונה בהתבסס על תוכן התמונה, לא על טקסט גנרי.

זה מדגים ש-Open WebUI יכול לשלוח בקשות רב-מודליות (טקסט + תמונה) דרך ה-backend (Lemonade) למודל ראייה.

---

<!-- @os:windows -->
### פעילות 3: יצירת תמונה מתוך הנחיית טקסט (Stable Diffusion)

מודלי Stable Diffusion אינם תומכים ביצירת טקסט, הם מייצרים תמונות בלבד דרך ה-Images API.

#### שלב 1: הגדרת יצירת תמונות ב-Open WebUI

1. בממשק הגרפי של Lemonade (`http://localhost:13305`), חפשו את `SDXL-Turbo` (מהיר) או `SDXL-Base-1.0` (איכות גבוהה יותר) והורידו אותו.
2. עברו אל **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. הגדירו:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` או `SDXL-Base-1.0`
4. אם ברצונכם להוסיף פרמטרים נוספים, הוסיפו אותם לשדה הטקסט כ-JSON. לדוגמה: `{ "steps": 4, "cfg_scale": 1 }`. עיינו בפרמטרים הזמינים ב-[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. שמרו
#### שלב 2: אפשור יצירת תמונות עבור המודל
שלב זה מבטיח שתפעילו יצירת תמונות כיכולת עבור המודל שלכם.
1. עברו אל **Admin Settings → Models** (http://localhost:8080/admin/settings/models) ובחרו את המודל שלכם
2. הפעילו את `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### שלב 3: יצירת תמונה ממסך הצ'אט

1. חזרו לצ'אט בכתובת `http://localhost:8080`.
2. בחרו **Text Generation LLM** בתפריט הנפתח של המודל (לדוגמה: Qwen, Llama). **אל תבחרו במודל Stable Diffusion** מכיוון שזהו בורר מודל צ'אט.
3. באזור ההודעה, לחצו על **Integrations**, והפעילו את **Image**.
4. השתמשו בפרומפט כגון: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. תמונה נוצרת ומופיעה בצ'אט.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

זה מבסס את העובדה ש-Open WebUI יכול לתאם זרימת עבודה "דו-חלקית":
  - ה-LLM עוזר לחדד את הפרומפט
  - התמונה נוצרת דרך נקודת הקצה Images של Lemonade באמצעות Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### פעילות 3: יצירת תמונה מפרומפט טקסט (Stable Diffusion)

מודלים מסוג Stable Diffusion אינם תומכים ביצירת טקסט, הם יוצרים תמונות בלבד דרך ה-Images API.

#### שלב 1: הגדרת יצירת תמונות ב-Open WebUI

1. ב-Lemonade GUI (`http://localhost:13305`), חפשו את `SDXL-Turbo` (מהיר) או `SDXL-Base-1.0` (איכות גבוהה יותר) והורידו אותו.
2. עברו אל **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. הגדירו:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` או `SDXL-Base-1.0`
4. אם ברצונכם להוסיף פרמטרים נוספים, הוסיפו אותם לשדה הטקסט כ-JSON. לדוגמה: `{ "steps": 4, "cfg_scale": 1 }`. ניתן לראות את הפרמטרים הזמינים ב-[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. שמרו


#### שלב 2: אפשור יצירת תמונות עבור המודל
שלב זה מבטיח שתפעילו יצירת תמונות כיכולת עבור המודל שלכם.
1. עברו אל **Admin Settings → Models** (http://localhost:8080/admin/settings/models) ובחרו את המודל שלכם
2. הפעילו את `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### שלב 3: יצירת תמונה ממסך הצ'אט

1. חזרו לצ'אט בכתובת `http://localhost:8080`.
2. בחרו **Text Generation LLM** בתפריט הנפתח של המודל (לדוגמה: Qwen, Llama). **אל תבחרו במודל Stable Diffusion** מכיוון שזהו בורר מודל צ'אט.
3. באזור ההודעה, לחצו על **Integrations**, והפעילו את **Image**.
4. השתמשו בפרומפט כגון: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. תמונה נוצרת ומופיעה בצ'אט.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

זה מבסס את העובדה ש-Open WebUI יכול לתאם זרימת עבודה "דו-חלקית":
  - ה-LLM עוזר לחדד את הפרומפט
  - התמונה נוצרת דרך נקודת הקצה Images של Lemonade באמצעות Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## פתרון בעיות

### "No models show up in Open WebUI"
- ראשית, בדקו את Lemonade: פתחו את `http://localhost:13305/api/v1/models` בדפדפן וודאו שהמודלים שלכם רשומים ומורדים
- לאחר מכן, בדקו את החיבור של Open WebUI: עברו אל **Admin Settings → Connections** בכתובת `http://localhost:8080/admin/settings/connections` וודאו שכתובת ה-Base URL היא `http://localhost:13305/api/v1`

### הודעת השגיאה "This model does not support chat completion"
- בחרתם במודל תמונה (SDXL-Turbo / SDXL-Base-1.0) בתפריט הנפתח של מודל הצ'אט.
- **תיקון**: בחרו LLM עבור צ'אט, והשתמשו במתג Image + בהגדרות Images ליצירה.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### שגיאות/פסקי זמן ביצירת תמונות
- התחילו עם `SDXL-Turbo` תחילה (מהיר, פחות שלבים)
- לאחר שזה עובד, החליפו את מודל התמונה ל-`SDXL-Base-1.0` לאיכות

---

## הצעדים הבאים

כעת יש לכם **'ערימת AI מקומית'** פעילה, ממשק משתמש יחיד השולט במספר סוגי מודלים דרך API סטנדרטי.

הנה שלוש הרחבות שפותחות זרימות עבודה חדשות לגמרי:

### 1. המרת דיבור לטקסט עם Whisper

נסו להפוך אודיו לטקסט באמצעות מודל Whisper, ולאחר מכן להזין אותו ל-LLM לצורך סיכום, פריטי פעולה או כתיבה מחדש. זהו הבסיס עבור סיכומי פגישות ועוזרים מבוססי קול.

### 2. תכנות ב-Python בתוך Open WebUI

השתמשו בחוויית הרצת הקוד המובנית של Open WebUI כדי להריץ קטעי קוד Python, לבדוק פלטים, ולחזור על תהליכים מהר יותר - מבלי לצאת מהממשק. [הפניה](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. רינדור HTML בתוך Open WebUI

בצעו רינדור לפלטי HTML ישירות בממשק. זה עוצמתי באופן מפתיע לבניית אבות-טיפוס מהירים, דוחות מעוצבים וקטעי קוד אינטראקטיביים. [הפניה](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## הפניות

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [תיעוד Lemonade Server](https://lemonade-server.ai/docs)
- [ה-CLI של Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [מדריך שילוב Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [מפרט ה-API של Lemonade Server (נקודות קצה)](https://lemonade-server.ai/docs/server/server_spec)
- [סרטון הדגמה (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [סרטון הדגמה (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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