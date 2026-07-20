<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل التوجيهي علامات خاصة لا يمكن لـ GitHub عرضها. يُرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> يتطلب هذا الدليل التوجيهي حدًا أدنى قدره **32 جيجابايت** من ذاكرة النظام.
<!-- @device:end -->

## نظرة عامة

[Open WebUI](https://docs.openwebui.com) هي واجهة مستضافة ذاتيًا وقائمة على المتصفح توفر تجربة روبوت دردشة مألوفة مع العمل كواجهة أمامية لخادم واحد أو أكثر من خوادم نماذج الذكاء الاصطناعي. بدلًا من الارتباط بمزود واحد، يمكن لـ Open WebUI الاتصال بأي **خلفية تعرض واجهة برمجة تطبيقات متوافقة مع OpenAI**، مما يتيح لك تبديل النماذج والإمكانيات دون تغيير الواجهات.

في هذا الدليل التوجيهي، نستخدم [**Lemonade**](https://lemonade-server.ai) كخلفية لأنها تعرض **نقطة نهاية موحدة متوافقة مع OpenAI** تدعم أنماطًا متعددة:
- **نماذج اللغة الكبيرة (LLMs)** لتوليد النصوص
- **نماذج الرؤية** لفهم الصور
- **Stable Diffusion** لتوليد الصور
- **نماذج نسخ الصوت** لتحويل الكلام إلى نص

يتيح لك هذا الإعداد استكشاف **سير العمل متعدد الوسائط الكامل من البداية إلى النهاية**.

---

## ما ستتعلمه

بنهاية هذا الدليل، ستكون قادرًا على:

- ربط Open WebUI بخلفية محلية متوافقة مع OpenAI (Lemonade)
- الدردشة مع نموذج لغة كبير محلي من متصفحك
- تحميل صورة وطرح أسئلة على نموذج رؤية بشأنها
- توليد صور من مطالبات نصية باستخدام نماذج Stable Diffusion (SDXL-Turbo / SDXL)
- فهم النموذج الذهني حتى تتمكن من استخدام خلفيات أخرى (Ollama، vLLM، خادم llama.cpp، إلخ)

---

## المفاهيم الأساسية (النموذج الذهني)

### المكونات الثلاثة

| العنصر | ما يقوم به | أمثلة |
|---|---|---|
| الواجهة الأمامية (UI) | تطبيق الويب الذي تتفاعل معه | Open WebUI |
| الخلفية (خادم النموذج) | يستضيف النماذج ويعرض نقاط نهاية HTTP | Lemonade، Ollama، vLLM، خادم llama.cpp، خوادم متوافقة مع OpenAI |
| النماذج | نماذج LLM / الرؤية / الانتشار / الصوت الفعلية | CodeLlama، DeepSeek، Gemma-MM، SDXL، SD-Turbo، Whisper |

#### لماذا تُعد "واجهة برمجة تطبيقات متوافقة مع OpenAI" مهمة

تم بناء Open WebUI حول نقاط نهاية قياسية بأسلوب OpenAI، مثل:
  - الدردشة: `/chat/completions`
  - قائمة النماذج: `/models`
  - توليد الصور: `/images/generations`
  - نسخ الصوت: `/audio/transcriptions`

يعرض Lemonade هذه ضمن `http://localhost:13305/api/v1/...`

إذا كانت الخلفية تدعم نقاط النهاية هذه، يمكن لـ Open WebUI التواصل معها بأقل إعداد ممكن. لهذا السبب يمكننا تبديل الخلفيات دون تغيير سير عملنا.

#### خدمتان، منفذان

طوال هذا الدليل التوجيهي، ستعمل مع خدمتين منفصلتين:

| الخدمة | العنوان | ما تفعله هناك |
|---|---|---|
| **Lemonade** (واجهة رسومية) | `http://localhost:13305` | تصفح النماذج وتنزيلها وإدارتها |
| **Open WebUI** | `http://localhost:8080` | الدردشة وتحميل الصور وتوليد الصور — الواجهة الموجهة للمستخدم |

يُشغّل Lemonade النماذج؛ ويُعد Open WebUI الواجهة التي تتفاعل معها. استخدم واجهة Lemonade الرسومية لتنزيل نماذجك أولًا، ثم استخدمها من Open WebUI.

---

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## الإعداد لمرة واحدة

يحتاج هذا الدليل التوجيهي إلى تشغيل Lemonade كخلفية، وعلى Linux، محرك حاويات (Podman) لتشغيل Open WebUI. قم بإعداد هذه العناصر قبل تثبيت Open WebUI.

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

## تنزيل النماذج في Lemonade

قبل تثبيت Open WebUI، تأكد من تنزيل النماذج التي تريد استخدامها وجاهزيتها في Lemonade.

1. افتح واجهة Lemonade الرسومية على `http://localhost:13305`.
2. تصفح النماذج المتاحة ونزّل النماذج التي تريد استخدامها (على سبيل المثال، نموذج لغة كبير للدردشة، ونموذج رؤية، و/أو نموذج Stable Diffusion لتوليد الصور).
3. تأكد من إمكانية الوصول إلى واجهة برمجة التطبيقات بزيارة `http://localhost:13305/api/v1/models` في متصفحك — يجب أن ترى النماذج التي نزّلتها مدرجة.

> يجب تنزيل النماذج في **Lemonade** (`localhost:13305`) قبل أن تظهر في **Open WebUI** (`localhost:8080`). إذا لم يظهر نموذج ما في Open WebUI لاحقًا، ارجع إلى هنا وتحقق من Lemonade أولًا.


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

## تثبيت Open WebUI

<!-- @os:windows -->
### 1. تثبيت Python 3.12

يتطلب Open WebUI **Python 3.12** — لا يتم تثبيته على Python 3.13 أو أحدث. يتيح لك مُشغّل Python الخاص بـ Windows (`py`) تثبيت 3.12 جنبًا إلى جنب مع أي إصدار Python موجود بالفعل دون أي تعارضات.

```powershell
winget install Python.Python.3.12
```

أغلق نافذة الطرفية وأعد فتحها بعد التثبيت، ثم تحقق من ذلك:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **ملاحظة:** يأتي نظامك مع Python 3.13 مثبتًا مسبقًا. تثبيت 3.12 لا يؤثر عليه — يستمر `python` في استخدام 3.13، بينما يستهدف `py -3.12` الإصدار 3.12 فقط عند الحاجة إليه.
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

### 2. إنشاء بيئة افتراضية وتثبيت Open WebUI

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
سنستخدم الآن خدمة Podman لوضع تثبيت Open WebUI الخاص بنا في حاوية.

يُرجى تنزيل الملف التالي إلى دليل من اختيارك: [compose.yml](assets/compose.yml)

في ذلك الدليل، شغّل الأمر التالي:

```bash
podman compose up -d
```

يقوم هذا بسحب صورة Open WebUI والكتابة إلى التخزين الدائم.

شغّل Open WebUI بكتابة `localhost:8080` في شريط عنوان متصفحك.

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

> **تلميح**: يوفر Open WebUI أيضًا خيارات تثبيت أخرى على [GitHub](https://github.com/open-webui/open-webui) الخاص بهم.
## بدء تشغيل خادم Open WebUI

<!-- @os:windows -->
- شغّل الأمر التالي لبدء تشغيل خادم Open WebUI HTTP:
```bash
open-webui serve
```
<!-- @os:end -->

- في المتصفح، انتقل إلى `http://localhost:8080`.
- سيطلب منك Open WebUI إنشاء حساب مسؤول محلي. بمجرد تسجيل الدخول، ستشاهد واجهة الدردشة.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> أبقِ نافذة الطرفية مفتوحة. إغلاقها يوقف Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> يعمل الحاوية في الخلفية. من الدليل الذي يحتوي على `compose.yml`، يمكنك إدارته باستخدام `podman compose down` (للإيقاف) و`podman compose up -d` (للتشغيل). تبقى حساباتك وإعداداتك محفوظة في وحدة التخزين `open_webui_data`.
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

## ربط Open WebUI بـ Lemonade

بما أن كلتا الخدمتين تعملان الآن — Lemonade على `localhost:13305` وOpen WebUI على `localhost:8080` — قم بربطهما ليتمكن Open WebUI من استخدام نماذج Lemonade.

في Open WebUI:

1. انقر على **أيقونة الملف الشخصي للمستخدم** في الزاوية العلوية اليمنى، ثم اختر **الإعدادات (Settings)**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. في لوحة الإعدادات، انقر على **إعدادات المسؤول (Admin Settings)** في أسفل اليسار.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. في الشريط الجانبي لإعدادات المسؤول، انقر على **الاتصالات (Connections)** (أو انتقل مباشرة إلى `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. ضمن **OpenAI API**، أضف اتصالاً جديدًا:
   - **عنوان URL الأساسي (Base URL):** `http://localhost:13305/api/v1`
   - **مفتاح API:** `-` (شرطة واحدة تعمل للاستخدام المحلي)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. تأكد من أنه ضمن **"إدارة اتصالات OpenAI API"**، يكون فقط `http://localhost:13305/api/v1` مفعّلاً. عطّل أي اتصالات أخرى (مثل اتصال OpenAI الافتراضي).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. انقر على **حفظ (Save)**.

7. **(موصى به)** عطّل ميزات التوليد التلقائي للحفاظ على استجابة Open WebUI مع النماذج اللغوية المحلية. اذهب إلى **إعدادات المسؤول ← الإعدادات ← الواجهة (Admin Settings → Settings → Interface)** وأوقف تشغيل:
   - توليد العنوان (Title Generation)
   - توليد المتابعة (Follow Up Generation)
   - توليد الوسوم (Tags Generation)

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. انقر على **حفظ (Save)**، ثم عد إلى `http://localhost:8080`.
9. انقر على القائمة المنسدلة للنماذج — يجب أن ترى النماذج التي قمت بتنزيلها من Lemonade.

---

## الأنشطة الرئيسية

الآن، أصبح كل شيء جاهزًا. لنلقِ نظرة على ثلاثة أشياء مثيرة للاهتمام يمكنك القيام بها.

---

### النشاط 1: الدردشة مع نموذج لغوي محلي
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. انقر على القائمة المنسدلة في أعلى يسار الواجهة. سيعرض هذا نماذج Lemonade المثبتة لديك. اختر واحدًا للمتابعة. (مثال: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. أدخل رسالة إلى النموذج اللغوي وانقر على إرسال (أو اضغط Enter). سيستغرق النموذج اللغوي بضع ثوانٍ ليتم تحميله في الذاكرة، ثم سترى الاستجابة تتدفق.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. انقر على القائمة المنسدلة في أعلى يسار الواجهة. سيعرض هذا نماذج Lemonade المثبتة لديك. اختر واحدًا للمتابعة. (مثال: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. أدخل رسالة إلى النموذج اللغوي وانقر على إرسال (أو اضغط Enter). سيستغرق النموذج اللغوي بضع ثوانٍ ليتم تحميله في الذاكرة، ثم سترى الاستجابة تتدفق.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. سيستجيب النموذج في الدردشة.

4. في هذه الأثناء، افتح `Task Manager` على نظامك. ستلاحظ **استخدامًا عاليًا لوحدة معالجة الرسومات أو وحدة معالجة الشبكة العصبية (GPU أو NPU)** بناءً على ما إذا كان النموذج الذي اخترته من نوع **Hybrid** أو **NPU** على التوالي. باستخدام مدير المهام، يمكنك التأكد من أنك تشغّل النموذج محليًا.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. انقر على القائمة المنسدلة في أعلى يسار الواجهة. سيعرض هذا نماذج Lemonade المثبتة لديك. اختر واحدًا للمتابعة. (مثال: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. أدخل رسالة إلى النموذج اللغوي وانقر على إرسال (أو اضغط Enter). سيستغرق النموذج اللغوي بضع ثوانٍ ليتم تحميله في الذاكرة، ثم سترى الاستجابة تتدفق.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. سيستجيب النموذج في الدردشة.
<!-- @os:end -->

يؤكد هذا أن Open WebUI يمكنه إرسال الطلبات إلى Lemonade باستخدام نقطة نهاية الدردشة المتوافقة مع OpenAI.

---

### النشاط 2: تحميل صورة وطرح أسئلة عليها (الرؤية)

يتطلب هذا نموذجًا يدعم إدخال الصور (نموذج رؤية أو متعدد الوسائط).

1. انقر على أيقونة التصفية، اختر "حسب الفئة (By Category)"، ثم اختر نموذجًا من قسم **الرؤية (Vision)** (مثل `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. انقر على زر **`+`** في مربع الرسالة وقم بتحميل صورة
3. اطرح سؤالاً يستلزم فهمًا حقيقيًا للصورة: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. يجيب النموذج بناءً على محتوى الصورة، وليس نصًا عامًا.

يوضح هذا أن Open WebUI يمكنه إرسال طلبات متعددة الوسائط (نص + صورة) عبر الواجهة الخلفية (Lemonade) إلى نموذج رؤية.

---

<!-- @os:windows -->
### النشاط 3: توليد صورة من موجه نصي (Stable Diffusion)

نماذج Stable Diffusion لا تدعم توليد النصوص، فهي فقط تولّد الصور من خلال واجهة برمجة تطبيقات الصور (Images API).

#### الخطوة 1: تهيئة توليد الصور في Open WebUI

1. في واجهة Lemonade الرسومية (`http://localhost:13305`)، ابحث عن `SDXL-Turbo` (سريع) أو `SDXL-Base-1.0` (جودة أعلى) وقم بتنزيله.
2. اذهب إلى **إعدادات المسؤول ← الصور (Admin Settings → Images)** (http://localhost:8080/admin/settings/images)
3. اضبط:
   - **توليد الصور (Image Generation):** تشغيل (ON)
   - **محرك توليد الصور (Image Generation Engine):** الافتراضي (OpenAI)
   - **عنوان URL الأساسي لـ OpenAI API:** `http://localhost:13305/api/v1`
   - **مفتاح OpenAI API:** `-`
   - **النموذج (Model):** `SDXL-Turbo` أو `SDXL-Base-1.0`
4. إذا أردت إضافة المزيد من المعلمات، أضفها إلى حقل النص بصيغة JSON. على سبيل المثال: `{ "steps": 4, "cfg_scale": 1 }`. راجع المعلمات المتاحة على [توليد الصور (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. احفظ
#### الخطوة 2: السماح بتوليد الصور للنموذج
تضمن هذه الخطوة تفعيل توليد الصور كإحدى قدرات النموذج الخاص بك.
1. اذهب إلى **Admin Settings → Models** (http://localhost:8080/admin/settings/models) واختر نموذجك
2. فعّل `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### الخطوة 3: توليد صورة من شاشة الدردشة

1. عد إلى الدردشة على `http://localhost:8080`.
2. اختر **نموذج توليد نص (LLM)** من القائمة المنسدلة للنماذج (مثال: Qwen، Llama). **لا تختر نموذج Stable Diffusion** لأن هذا محدد نموذج الدردشة.
3. في منطقة الرسائل، انقر على **Integrations**، وفعّل خيار **Image**.
4. استخدم موجّهًا مثل: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. سيتم توليد صورة وستظهر في الدردشة.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

هذا يوضح أن Open WebUI يمكنه تنسيق سير عمل "من جزئين":
  - يساعد الـLLM في تحسين الموجّه
  - يتم توليد الصورة عبر نقطة نهاية Images الخاصة بـLemonade باستخدام Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### النشاط 3: توليد صورة من موجّه نصي (Stable Diffusion)

نماذج Stable Diffusion لا تدعم توليد النصوص، بل تولّد الصور فقط من خلال واجهة برمجة التطبيقات Images API.

#### الخطوة 1: تهيئة توليد الصور في Open WebUI

1. في واجهة Lemonade GUI (`http://localhost:13305`)، ابحث عن `SDXL-Turbo` (سريع) أو `SDXL-Base-1.0` (جودة أعلى) وقم بتنزيله.
2. اذهب إلى **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. اضبط الإعدادات التالية:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` أو `SDXL-Base-1.0`
4. إذا أردت إضافة المزيد من المعاملات، أضفها إلى الحقل النصي بصيغة JSON. على سبيل المثال: `{ "steps": 4, "cfg_scale": 1 }`. راجع المعاملات المتاحة في [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. احفظ


#### الخطوة 2: السماح بتوليد الصور للنموذج
تضمن هذه الخطوة تفعيل توليد الصور كإحدى قدرات النموذج الخاص بك.
1. اذهب إلى **Admin Settings → Models** (http://localhost:8080/admin/settings/models) واختر نموذجك
2. فعّل `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### الخطوة 3: توليد صورة من شاشة الدردشة

1. عد إلى الدردشة على `http://localhost:8080`.
2. اختر **نموذج توليد نص (LLM)** من القائمة المنسدلة للنماذج (مثال: Qwen، Llama). **لا تختر نموذج Stable Diffusion** لأن هذا محدد نموذج الدردشة.
3. في منطقة الرسائل، انقر على **Integrations**، وفعّل خيار **Image**.
4. استخدم موجّهًا مثل: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. سيتم توليد صورة وستظهر في الدردشة.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

هذا يوضح أن Open WebUI يمكنه تنسيق سير عمل "من جزئين":
  - يساعد الـLLM في تحسين الموجّه
  - يتم توليد الصورة عبر نقطة نهاية Images الخاصة بـLemonade باستخدام Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## استكشاف الأخطاء وإصلاحها

### "لا تظهر أي نماذج في Open WebUI"
- أولًا، تحقق من Lemonade: افتح `http://localhost:13305/api/v1/models` في المتصفح وتأكد من ظهور نماذجك وأنها تم تنزيلها
- بعد ذلك، تحقق من اتصال Open WebUI: اذهب إلى **Admin Settings → Connections** على `http://localhost:8080/admin/settings/connections` وتحقق من أن Base URL هو `http://localhost:13305/api/v1`

### رسالة الخطأ "This model does not support chat completion"
- لقد اخترت نموذج صور (SDXL-Turbo / SDXL-Base-1.0) من القائمة المنسدلة لنموذج الدردشة.
- **الحل**: اختر نموذج LLM للدردشة، واستخدم مفتاح تبديل Image وإعدادات Images للتوليد.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### أخطاء/انتهاء مهلة توليد الصور
- ابدأ بـ`SDXL-Turbo` أولًا (سريع، خطوات أقل)
- بمجرد أن يعمل بشكل جيد، انتقل إلى نموذج الصور `SDXL-Base-1.0` للحصول على جودة أعلى

---

## الخطوات التالية

أصبح لديك الآن **'حزمة ذكاء اصطناعي محلية'** عاملة، وهي واجهة مستخدم واحدة تتحكم في أنواع متعددة من النماذج عبر واجهة برمجة تطبيقات موحدة.

فيما يلي ثلاثة توسعات تفتح آفاقًا جديدة تمامًا لسير العمل:

### 1. تحويل الكلام إلى نص باستخدام Whisper

جرّب تحويل الصوت إلى نص باستخدام نموذج Whisper، ثم أدخله إلى LLM للتلخيص، أو استخراج بنود العمل، أو إعادة الصياغة. هذا هو الأساس لملاحظات الاجتماعات والمساعدين الصوتيين.

### 2. برمجة Python داخل Open WebUI

استخدم تجربة تنفيذ الأكواد المدمجة في Open WebUI لتشغيل مقاطع Python، وفحص المخرجات، والتكرار بشكل أسرع—دون مغادرة الواجهة. [مرجع](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. عرض HTML داخل Open WebUI

اعرض مخرجات HTML مباشرة في الواجهة. هذه ميزة قوية بشكل مفاجئ لبناء نماذج أولية سريعة، وتقارير منسّقة، ومقاطع تفاعلية. [مرجع](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## المراجع

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [وثائق Lemonade Server](https://lemonade-server.ai/docs)
- [واجهة سطر أوامر Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [دليل تكامل Lemonade مع Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [مواصفات واجهة برمجة تطبيقات Lemonade Server (نقاط النهاية)](https://lemonade-server.ai/docs/server/server_spec)
- [شرح مرئي (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [شرح مرئي (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)