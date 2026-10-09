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

[Open WebUI](https://docs.openwebui.com) הוא ממשק מבוסס דפדפן המתארח באופן עצמאי, המספק חוויית צ'אטבוט מוכרת תוך פעולה כחזית (frontend) לשרת מודל AI אחד או יותר. במקום להיות קשור לספק אחד, Open WebUI יכול להתחבר ל**כל backend החושף API תואם OpenAI**, כך שניתן להחליף מודלים ויכולות מבלי להחליף ממשקים.

במדריך זה, אנו משתמשים ב-[**Lemonade**](https://lemonade-server.ai) כ-backend מכיוון שהוא חושף **נקודת קצה אחודה תואמת OpenAI** התומכת במספר מודליות:
- **מודלי שפה גדולים (LLMs)** ליצירת טקסט
- **מודלי ראייה** להבנת תמונות
- **Stable Diffusion** ליצירת תמונות
- **מודלי תמלול שמע** להמרת דיבור לטקסט

הגדרה זו מאפשרת לך לחקור את **זרימת העבודה המולטימודלית המלאה מקצה לקצה**.

---

## מה תלמד

בסיום, תוכל:

- לחבר את Open WebUI ל-backend מקומי תואם OpenAI (Lemonade)
- לשוחח עם LLM מקומי מהדפדפן שלך
- להעלות תמונה ולשאול מודל ראייה שאלות עליה
- ליצור תמונות מהנחיות טקסט באמצעות מודלי Stable Diffusion (SDXL-Turbo / SDXL)
- להבין את המודל המנטלי כדי שתוכל להשתמש ב-backends אחרים (Ollama, vLLM, שרת llama.cpp וכו')

---

## מושגי ליבה (מודל מנטלי)

### שלושת הרכיבים

| רכיב | מה הוא עושה | דוגמאות |
|---|---|---|
| חזית (UI) | אפליקציית הרשת שאיתה אתה מקיים אינטראקציה | Open WebUI |
| Backend (שרת מודלים) | מארח מודלים וחושף נקודות קצה HTTP | Lemonade, Ollama, vLLM, שרת llama.cpp, שרתים תואמי OpenAI |
| מודלים | ה-LLM / מודל ראייה / דיפוזיה / שמע בפועל | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### למה "API תואם OpenAI" חשוב

Open WebUI בנוי סביב נקודות קצה בסגנון OpenAI סטנדרטי, כמו:
  - צ'אט: `/chat/completions`
  - רשימת מודלים: `/models`
  - יצירת תמונות: `/images/generations`
  - תמלול שמע: `/audio/transcriptions`

Lemonade חושף אותן תחת `http://localhost:13305/api/v1/...`

אם backend תומך בנקודות קצה אלו, Open WebUI יכול לתקשר איתו עם הגדרה מינימלית. זו הסיבה שאנחנו יכולים להחליף backends מבלי לשנות את זרימת העבודה שלנו.

#### שני שירותים, שני פורטים

לאורך מדריך זה תעבוד עם שני שירותים נפרדים:

| שירות | כתובת URL | מה אתה עושה שם |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | עיון, הורדה וניהול מודלים |
| **Open WebUI** | `http://localhost:8080` | צ'אט, העלאת תמונות, יצירת תמונות — הממשק הפונה למשתמש |

Lemonade מפעיל את המודלים; Open WebUI הוא הממשק שאיתו אתה מקיים אינטראקציה. השתמש ב-Lemonade GUI כדי להוריד את המודלים שלך קודם, ולאחר מכן השתמש בהם מתוך Open WebUI.

---

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## הגדרה חד-פעמית

מדריך זה דורש ש-Lemonade יפעל כ-backend וכן, ב-Linux, מנוע מכולות (Podman) להפעלת Open WebUI. הגדר את אלה לפני התקנת Open WebUI.

<!-- @os:windows -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade -->
<!-- @device:end -->
<!-- @prereq:hf-models-all-minilm-l6-v2 -->
---
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade,podman -->
<!-- @device:end -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
---
<!-- @device:end -->
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:lemonade-models-qwen3-5-4b,lemonade-models-sdxl-turbo -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## הורדת מודלים ב-Lemonade

לפני התקנת Open WebUI, ודא שהמודלים שברצונך להשתמש בהם מורדים וזמינים ב-Lemonade.

1. פתח את Lemonade GUI בכתובת `http://localhost:13305`.
2. עיין במודלים הזמינים והורד את אלה שבהם ברצונך להשתמש (לדוגמה, LLM לצ'אט, מודל ראייה, ו/או מודל Stable Diffusion ליצירת תמונות).
3. ודא שה-API נגיש על ידי ביקור בכתובת `http://localhost:13305/api/v1/models` בדפדפן שלך — אמורה להופיע רשימת המודלים שהורדת.

> יש להוריד מודלים ב-**Lemonade** (`localhost:13305`) לפני שהם יכולים להופיע ב-**Open WebUI** (`localhost:8080`). אם מודל אינו מופיע ב-Open WebUI בהמשך, חזור לכאן ובדוק תחילה ב-Lemonade.


<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
<!-- @prereq:lemonade-models-qwen3-4b-hybrid -->
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
  $pngImg = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAEUlEQVR42mP4z8CAFTEMLQkAKP8/wc53yE8AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$pngImg"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "What color is this image? Reply with only the color name." },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 512
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
  if ($visionText -notmatch "(?i)red") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
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
  $pngImg = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAEUlEQVR42mP4z8CAFTEMLQkAKP8/wc53yE8AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$pngImg"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "What color is this image? Reply with only the color name." },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 512
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
  if ($visionText -notmatch "(?i)red") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
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
png_img = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAEUlEQVR42mP4z8CAFTEMLQkAKP8/wc53yE8AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png_img
vision = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "What color is this image? Reply with only the color name."},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 512,
}, timeout=300)
if not vision.get("choices"):
  raise SystemExit(f"Unexpected vision response (no choices). Raw response:\n{json.dumps(vision, indent=2)}")
vtext = vision["choices"][0]["message"].get("content", "")
if not vtext.strip():
  raise SystemExit(f"Vision returned empty content. Raw response:\n{json.dumps(vision, indent=2)}")
if "red" not in vtext.lower():
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

Open WebUI דורש **Python 3.12** — הוא אינו מותקן על Python 3.13+. מפעיל ה-Python של Windows (`py`) מאפשר להתקין 3.12 לצד כל גרסת Python קיימת ללא התנגשויות.

```powershell
winget install Python.Python.3.12
```

סגור ופתח מחדש את הטרמינל שלך לאחר ההתקנה, ולאחר מכן אמת:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **הערה:** המערכת שלך מגיעה עם Python 3.13 מותקן מראש. התקנת 3.12 אינה משפיעה עליו — `python` ממשיך להשתמש ב-3.13, ו-`py -3.12` מכוון ל-3.12 רק כשאתה זקוק לכך.
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
כעת נשתמש בשירות Podman כדי להריץ את התקנת Open WebUI שלנו במכולה.

אנא הורד את הקובץ הבא לתיקייה לבחירתך: [compose.yml](assets/compose.yml)

בתיקייה זו, הרץ את הפקודה הבאה:

```bash
podman compose up -d
```

פעולה זו מושכת את תמונת Open WebUI וכותבת לאחסון קבוע.

הפעל את Open WebUI על ידי הקלדת `localhost:8080` בשורת הכתובת של הדפדפן שלך.

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

> **טיפ**: Open WebUI מספק גם אפשרויות התקנה נוספות ב-[GitHub](https://github.com/open-webui/open-webui) שלהם.
## התחלת שרת Open WebUI

<!-- @os:windows -->
- הריצו את הפקודה הבאה כדי להפעיל את שרת ה-HTTP של Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- בדפדפן, נווטו אל `http://localhost:8080`.
- Open WebUI יבקש מכם ליצור חשבון מנהל מקומי. לאחר שתתחברו, תראו את ממשק הצ'אט.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> השאירו את חלון הטרמינל פתוח. סגירתו עוצרת את Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> הקונטיינר רץ ברקע. מתוך הספרייה המכילה את `compose.yml`, נהלו אותו באמצעות `podman compose down` (עצירה) ו-`podman compose up -d` (הפעלה). החשבונות וההגדרות שלכם נשמרים בנפח (volume) `open_webui_data`.
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

כעת ששני השירותים פועלים — Lemonade על `localhost:13305` ו-Open WebUI על `localhost:8080` — חברו ביניהם כדי ש-Open WebUI יוכל להשתמש במודלים של Lemonade.

ב-Open WebUI:

1. לחצו על **סמל פרופיל המשתמש** בפינה הימנית העליונה, ולאחר מכן בחרו **הגדרות**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. בפאנל ההגדרות, לחצו על **הגדרות מנהל** בפינה השמאלית התחתונה.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. בסרגל הצד של הגדרות המנהל, לחצו על **חיבורים** (או נווטו ישירות אל `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. תחת **OpenAI API**, הוסיפו חיבור חדש:
   - **כתובת בסיס (Base URL):** `http://localhost:13305/api/v1`
   - **מפתח API:** `-` (מקף בודד עובד עבור שימוש מקומי)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. ודאו שתחת **"ניהול חיבורי OpenAI API"**, רק `http://localhost:13305/api/v1` מופעל. בטלו כל חיבור אחר (לדוגמה, חיבור ברירת המחדל של OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. לחצו על **שמירה**.

7. **(מומלץ)** בטלו תכונות יצירה אוטומטית כדי לשמור על תגובתיות Open WebUI עם מודלי LLM מקומיים. עברו אל **הגדרות מנהל → הגדרות → ממשק** וכבו:
   - יצירת כותרת
   - יצירת שאלות המשך
   - יצירת תגיות

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. לחצו על **שמירה**, ולאחר מכן חזרו אל `http://localhost:8080`.
9. לחצו על תפריט המודלים הנפתח — אמורים להופיע המודלים שהורדתם מ-Lemonade.

---

## פעילויות עיקריות

כעת כל ההגדרות הושלמו. בואו נבחן שלושה דברים מעניינים לעשות.

---

### פעילות 1: שיחה עם LLM מקומי
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. לחצו על תפריט הניפתח בפינה השמאלית העליונה של הממשק. פעולה זו תציג את מודלי Lemonade המותקנים אצלכם. בחרו אחד כדי להמשיך. (לדוגמה: `Qwen3-4B-Hybrid`).

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
1. לחצו על תפריט הניפתח בפינה השמאלית העליונה של הממשק. פעולה זו תציג את מודלי Lemonade המותקנים אצלכם. בחרו אחד כדי להמשיך. (לדוגמה: `Qwen3.5-4B-GGUF`).

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

4. בשלב זה, פתחו את `Task Manager` במערכת שלכם. תראו **ניצול גבוה של GPU או NPU** בהתאם לכך שהמודל שבחרתם הוא **Hybrid** או **NPU**, בהתאמה. באמצעות מנהל המשימות, תוכלו לאשר שאתם מריצים את המודל מקומית.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. לחצו על תפריט הניפתח בפינה השמאלית העליונה של הממשק. פעולה זו תציג את מודלי Lemonade המותקנים אצלכם. בחרו אחד כדי להמשיך. (לדוגמה: `Qwen3.5-4B-GGUF`).

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

פעולה זו מאמתת ש-Open WebUI יכול לשלוח בקשות ל-Lemonade באמצעות נקודת הקצה (endpoint) של הצ'אט התואמת ל-OpenAI.

---

### פעילות 2: העלאת תמונה ושאילת שאלות (ראייה)

פעילות זו דורשת מודל התומך בקלט תמונה (מודל ראייה או מולטימודלי).

1. לחצו על סמל הסינון, בחרו "לפי קטגוריה," ולאחר מכן בחרו מודל מתוך קטגוריית **ראייה** (לדוגמה, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. לחצו על כפתור **`+`** בתיבת ההודעה והעלו תמונה
3. שאלו משהו שמחייב הבנת תמונה אמיתית: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. המודל עונה בהתבסס על תוכן התמונה, ולא על טקסט גנרי.

פעילות זו מדגימה ש-Open WebUI יכול לשלוח בקשות מולטימודליות (טקסט + תמונה) דרך הצד האחורי (Lemonade) למודל ראייה.

---

<!-- @os:windows -->
### פעילות 3: יצירת תמונה מהנחיית טקסט (Stable Diffusion)

מודלי Stable Diffusion אינם תומכים ביצירת טקסט, הם יוצרים תמונות בלבד דרך ה-Images API.

#### שלב 1: הגדרת יצירת תמונות ב-Open WebUI

1. בממשק הגרפי של Lemonade (`http://localhost:13305`), חפשו את `SDXL-Turbo` (מהיר) או `SDXL-Base-1.0` (איכות גבוהה יותר) והורידו אותו.
2. עברו אל **הגדרות מנהל → תמונות** (http://localhost:8080/admin/settings/images)
3. הגדירו:
   - **יצירת תמונות:** פעיל
   - **מנוע יצירת תמונות:** ברירת מחדל (OpenAI)
   - **כתובת בסיס של OpenAI API:** `http://localhost:13305/api/v1`
   - **מפתח OpenAI API:** `-`
   - **מודל:** `SDXL-Turbo` או `SDXL-Base-1.0`
4. אם ברצונכם להוסיף פרמטרים נוספים, הוסיפו אותם לשדה הטקסט כ-JSON. לדוגמה: `{ "steps": 4, "cfg_scale": 1 }`. ראו את הפרמטרים הזמינים ב-[יצירת תמונות (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. שמירה
#### שלב 2: אפשרו יצירת תמונות עבור המודל
שלב זה מבטיח שתפעילו את יצירת התמונות כיכולת עבור המודל שלכם.
1. עברו אל **Admin Settings → Models** (http://localhost:8080/admin/settings/models) ובחרו את המודל שלכם
2. הפעילו את `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### שלב 3: יצרו תמונה ממסך הצ'אט

1. חזרו לצ'אט בכתובת `http://localhost:8080`.
2. בחרו **LLM ליצירת טקסט** בתפריט הנפתח של המודל (לדוגמה: Qwen, Llama). **אל תבחרו מודל Stable Diffusion** מכיוון שזהו בורר מודל צ'אט.
3. באזור ההודעה, לחצו על **Integrations**, והפעילו את המתג **Image**.
4. השתמשו בפרומפט כגון: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. תמונה נוצרת ומופיעה בצ'אט.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

זה מוכיח ש-Open WebUI מסוגל לתאם זרימת עבודה "דו-חלקית":
  - ה-LLM מסייע לחדד את הפרומפט
  - התמונה נוצרת דרך נקודת הקצה (endpoint) של Images ב-Lemonade באמצעות Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### פעילות 3: יצירת תמונה מפרומפט טקסט (Stable Diffusion)

מודלי Stable Diffusion אינם תומכים ביצירת טקסט, הם רק יוצרים תמונות דרך ה-Images API.

#### שלב 1: הגדירו יצירת תמונות ב-Open WebUI

1. ב-Lemonade GUI (`http://localhost:13305`), חפשו את `SDXL-Turbo` (מהיר) או `SDXL-Base-1.0` (איכות גבוהה יותר) והורידו אותו.
2. עברו אל **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. הגדירו:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` או `SDXL-Base-1.0`
4. אם ברצונכם להוסיף פרמטרים נוספים, הוסיפו אותם לשדה הטקסט בפורמט JSON. לדוגמה: `{ "steps": 4, "cfg_scale": 1 }`. ראו פרמטרים זמינים ב-[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. שמרו


#### שלב 2: אפשרו יצירת תמונות עבור המודל
שלב זה מבטיח שתפעילו את יצירת התמונות כיכולת עבור המודל שלכם.
1. עברו אל **Admin Settings → Models** (http://localhost:8080/admin/settings/models) ובחרו את המודל שלכם
2. הפעילו את `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### שלב 3: יצרו תמונה ממסך הצ'אט

1. חזרו לצ'אט בכתובת `http://localhost:8080`.
2. בחרו **LLM ליצירת טקסט** בתפריט הנפתח של המודל (לדוגמה: Qwen, Llama). **אל תבחרו מודל Stable Diffusion** מכיוון שזהו בורר מודל צ'אט.
3. באזור ההודעה, לחצו על **Integrations**, והפעילו את המתג **Image**.
4. השתמשו בפרומפט כגון: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. תמונה נוצרת ומופיעה בצ'אט.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

זה מוכיח ש-Open WebUI מסוגל לתאם זרימת עבודה "דו-חלקית":
  - ה-LLM מסייע לחדד את הפרומפט
  - התמונה נוצרת דרך נקודת הקצה (endpoint) של Images ב-Lemonade באמצעות Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## פתרון בעיות

### "No models show up in Open WebUI"
- ראשית, בדקו את Lemonade: פתחו את `http://localhost:13305/api/v1/models` בדפדפן ואשרו שהמודלים שלכם מופיעים ברשימה והורדתם אותם
- לאחר מכן, בדקו את החיבור של Open WebUI: עברו אל **Admin Settings → Connections** בכתובת `http://localhost:8080/admin/settings/connections` וודאו שכתובת ה-Base URL היא `http://localhost:13305/api/v1`

### הודעת השגיאה "This model does not support chat completion"
- בחרתם מודל תמונה (SDXL-Turbo / SDXL-Base-1.0) בתפריט הנפתח של מודל הצ'אט.
- **פתרון**: בחרו LLM לצ'אט, והשתמשו במתג Image + הגדרות Images ליצירה.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### שגיאות/זמני המתנה ביצירת תמונות
- התחילו עם `SDXL-Turbo` תחילה (מהיר, פחות שלבים)
- לאחר שזה עובד, החליפו את מודל התמונה ל-`SDXL-Base-1.0` לאיכות גבוהה יותר

---

## השלבים הבאים

כעת יש לכם **'ערימת בינה מלאכותית מקומית'** פעילה, ממשק משתמש יחיד השולט בסוגי מודלים מרובים דרך API סטנדרטי.

הנה שלוש הרחבות שפותחות זרימות עבודה חדשות לגמרי:

### 1. המרת דיבור לטקסט עם Whisper

נסו להפוך שמע לטקסט באמצעות מודל Whisper, ולאחר מכן הזינו אותו ל-LLM לסיכום, פעולות נדרשות, או עריכה מחדש. זהו הבסיס לרשימות פגישות ועוזרים מופעלי קול.

### 2. תכנות Python בתוך Open WebUI

השתמשו בחוויית הרצת הקוד המובנית של Open WebUI כדי להריץ קטעי קוד ב-Python, לבדוק פלטים, ולהתקדם מהר יותר - מבלי לצאת מהממשק. [הפניה](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. עיבוד HTML בתוך Open WebUI

עבדו פלטי HTML ישירות בממשק. זה עוצמתי באופן מפתיע לבניית אבי-טיפוס מהירים, דוחות מעוצבים, וקטעי קוד אינטראקטיביים. [הפניה](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## מקורות

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [תיעוד Lemonade Server](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [מדריך שילוב Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [מפרט ה-API של Lemonade Server (נקודות קצה)](https://lemonade-server.ai/docs/server/server_spec)
- [סרטון הדרכה (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [סרטון הדרכה (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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