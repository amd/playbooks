<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> يتطلب هذا الدليل حدًا أدنى من ذاكرة النظام يبلغ **32 جيجابايت**.
<!-- @device:end -->

## نظرة عامة

[Open WebUI](https://docs.openwebui.com) هي واجهة ذاتية الاستضافة تعمل عبر المتصفح، وتوفر تجربة روبوت محادثة مألوفة مع العمل كواجهة أمامية لخادم واحد أو أكثر من خوادم نماذج الذكاء الاصطناعي. وبدلاً من الارتباط بمزود واحد، يمكن لـ Open WebUI الاتصال بـ **أي واجهة خلفية تعرض واجهة برمجة تطبيقات متوافقة مع OpenAI**، مما يتيح لك تبديل النماذج والإمكانيات دون تغيير الواجهات.

في هذا الدليل، نستخدم [**Lemonade**](https://lemonade-server.ai) كواجهة خلفية لأنها تعرض **نقطة نهاية موحدة متوافقة مع OpenAI** تدعم أنماطًا متعددة:
- **النماذج اللغوية الكبيرة (LLMs)** لتوليد النصوص
- **نماذج الرؤية** لفهم الصور
- **Stable Diffusion** لتوليد الصور
- **نماذج نسخ الصوت** لتحويل الكلام إلى نص

يتيح لك هذا الإعداد استكشاف **سير العمل متعدد الوسائط الكامل من البداية إلى النهاية**.

---

## ما ستتعلمه

بنهاية هذا الدليل، ستكون قادرًا على:

- ربط Open WebUI بواجهة خلفية محلية متوافقة مع OpenAI (Lemonade)
- الدردشة مع نموذج لغوي كبير محلي من متصفحك
- رفع صورة وطرح أسئلة عليها باستخدام نموذج رؤية
- توليد صور من موجهات نصية باستخدام نماذج Stable Diffusion (SDXL-Turbo / SDXL)
- فهم النموذج الذهني بحيث يمكنك استخدام واجهات خلفية أخرى (Ollama، vLLM، خادم llama.cpp، إلخ)

---

## المفاهيم الأساسية (النموذج الذهني)

### المكونات الثلاثة

| المكون | ما يقوم به | أمثلة |
|---|---|---|
| الواجهة الأمامية (UI) | تطبيق الويب الذي تتفاعل معه | Open WebUI |
| الواجهة الخلفية (خادم النماذج) | يستضيف النماذج ويعرض نقاط نهاية HTTP | Lemonade، Ollama، vLLM، خادم llama.cpp، خوادم متوافقة مع OpenAI |
| النماذج | نماذج LLM / الرؤية / Diffusion / الصوت الفعلية | CodeLlama، DeepSeek، Gemma-MM، SDXL، SD-Turbo، Whisper |

#### لماذا تُعد "واجهة برمجة التطبيقات المتوافقة مع OpenAI" مهمة

تم بناء Open WebUI حول نقاط نهاية قياسية بأسلوب OpenAI، مثل:
  - المحادثة: `/chat/completions`
  - قائمة النماذج: `/models`
  - توليد الصور: `/images/generations`
  - نسخ الصوت: `/audio/transcriptions`

تعرض Lemonade هذه النقاط تحت `http://localhost:13305/api/v1/...`

إذا كانت الواجهة الخلفية تدعم هذه النقاط، يمكن لـ Open WebUI التواصل معها بأدنى قدر من الإعداد. لهذا السبب يمكننا تبديل الواجهات الخلفية دون تغيير سير عملنا.

#### خدمتان، منفذان

خلال هذا الدليل، ستعمل مع خدمتين منفصلتين:

| الخدمة | الرابط | ما تفعله هناك |
|---|---|---|
| **Lemonade** (واجهة رسومية) | `http://localhost:13305` | تصفح النماذج وتنزيلها وإدارتها |
| **Open WebUI** | `http://localhost:8080` | الدردشة، رفع الصور، توليد الصور — الواجهة الموجهة للمستخدم |

تقوم Lemonade بتشغيل النماذج؛ بينما Open WebUI هي الواجهة التي تتفاعل معها. استخدم واجهة Lemonade الرسومية لتنزيل نماذجك أولاً، ثم استخدمها من خلال Open WebUI.

---

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## الإعداد لمرة واحدة

يتطلب هذا الدليل تشغيل Lemonade كواجهة خلفية، وعلى نظام Linux، محرك حاويات (Podman) لتشغيل Open WebUI. قم بإعداد هذه المتطلبات قبل تثبيت Open WebUI.

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

قبل تثبيت Open WebUI، تأكد من أن النماذج التي تريد استخدامها قد تم تنزيلها وهي جاهزة في Lemonade.

1. افتح واجهة Lemonade الرسومية على `http://localhost:13305`.
2. تصفح النماذج المتاحة ونزّل التي تريد استخدامها (مثل نموذج لغوي كبير للدردشة، ونموذج رؤية، و/أو نموذج Stable Diffusion لتوليد الصور).
3. تأكد من إمكانية الوصول إلى واجهة برمجة التطبيقات بزيارة `http://localhost:13305/api/v1/models` في متصفحك — يجب أن ترى النماذج التي قمت بتنزيلها مدرجة.

> يجب تنزيل النماذج في **Lemonade** (`localhost:13305`) قبل أن تظهر في **Open WebUI** (`localhost:8080`). إذا لم يظهر نموذج ما في Open WebUI لاحقًا، عد إلى هنا وتحقق من Lemonade أولاً.


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

## تثبيت Open WebUI

<!-- @os:windows -->
### 1. تثبيت Python 3.12

يتطلب Open WebUI **Python 3.12** — ولا يتم تثبيته على Python 3.13 أو أحدث. يتيح لك مُطلق Python الخاص بـ Windows (`py`) تثبيت الإصدار 3.12 جنبًا إلى جنب مع أي إصدار Python موجود دون تعارضات.

```powershell
winget install Python.Python.3.12
```

أغلق الطرفية وأعد فتحها بعد التثبيت، ثم تحقق:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **ملاحظة:** يأتي نظامك مع Python 3.13 مثبتًا مسبقًا. لا يؤثر تثبيت 3.12 عليه — يستمر `python` في استخدام 3.13، بينما يستهدف `py -3.12` الإصدار 3.12 فقط عند الحاجة إليه.
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
سنقوم الآن باستخدام خدمة Podman لتحويل تثبيت Open WebUI إلى حاوية.

يرجى تنزيل الملف التالي إلى دليل من اختيارك: [compose.yml](assets/compose.yml)

في ذلك الدليل، شغّل الأمر التالي:

```bash
podman compose up -d
```

يقوم هذا بسحب صورة Open WebUI والكتابة إلى وحدة تخزين دائمة.

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

> **نصيحة**: يوفر Open WebUI أيضًا خيارات تثبيت أخرى على [GitHub](https://github.com/open-webui/open-webui) الخاص به.
## بدء تشغيل خادم Open WebUI

<!-- @os:windows -->
- شغّل الأمر التالي لبدء تشغيل خادم Open WebUI HTTP:
```bash
open-webui serve
```
<!-- @os:end -->

- في المتصفح، انتقل إلى `http://localhost:8080`.
- سيطلب منك Open WebUI إنشاء حساب مسؤول محلي. بمجرد تسجيل الدخول، سترى واجهة الدردشة.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> أبقِ نافذة الطرفية مفتوحة. إغلاقها يوقف Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> يعمل الحاوية في الخلفية. من الدليل الذي يحتوي على `compose.yml`، أدره باستخدام `podman compose down` (للإيقاف) و`podman compose up -d` (للتشغيل). تبقى حساباتك وإعداداتك محفوظة في وحدة التخزين `open_webui_data`.
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

الآن بعد أن أصبحت كلتا الخدمتين قيد التشغيل — Lemonade على `localhost:13305` و Open WebUI على `localhost:8080` — قم بربطهما ليتمكن Open WebUI من استخدام نماذج Lemonade.

في Open WebUI:

1. انقر على **أيقونة الملف الشخصي للمستخدم** في الزاوية العلوية اليمنى، ثم اختر **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. في لوحة الإعدادات، انقر على **Admin Settings** في أسفل اليسار.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. في الشريط الجانبي لـ Admin Settings، انقر على **Connections** (أو انتقل مباشرة إلى `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. تحت **OpenAI API**، أضف اتصالاً جديداً:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (شرطة واحدة تعمل للاستخدام المحلي)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. تأكد من أنه ضمن **"Manage OpenAI API Connections"**، يكون `http://localhost:13305/api/v1` هو الوحيد المفعّل. عطّل أي اتصالات أخرى (مثل اتصال OpenAI الافتراضي).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. انقر على **Save**.

7. **(موصى به)** عطّل ميزات التوليد التلقائي لإبقاء Open WebUI سريع الاستجابة مع نماذج LLM المحلية. اذهب إلى **Admin Settings → Settings → Interface** وأوقف تشغيل:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. انقر على **Save**، ثم عد إلى `http://localhost:8080`.
9. انقر على قائمة النماذج المنسدلة — يجب أن ترى النماذج التي قمت بتنزيلها من Lemonade.

---

## الأنشطة الرئيسية

الآن، أصبح كل شيء جاهزاً. لنلقِ نظرة على ثلاثة أشياء مثيرة للاهتمام يمكنك القيام بها.

---

### النشاط 1: الدردشة مع نموذج LLM محلي
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. انقر على القائمة المنسدلة في الزاوية العلوية اليسرى من الواجهة. سيؤدي هذا إلى عرض نماذج Lemonade المثبتة لديك. اختر واحداً للمتابعة. (مثال: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. أدخل رسالة إلى نموذج LLM وانقر على إرسال (أو اضغط على Enter). سيستغرق نموذج LLM بضع ثوانٍ ليتم تحميله في الذاكرة ثم سترى الاستجابة تتدفق.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. انقر على القائمة المنسدلة في الزاوية العلوية اليسرى من الواجهة. سيؤدي هذا إلى عرض نماذج Lemonade المثبتة لديك. اختر واحداً للمتابعة. (مثال: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. أدخل رسالة إلى نموذج LLM وانقر على إرسال (أو اضغط على Enter). سيستغرق نموذج LLM بضع ثوانٍ ليتم تحميله في الذاكرة ثم سترى الاستجابة تتدفق.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. سيستجيب النموذج في الدردشة.

4. في هذا الوقت، افتح `Task Manager` على نظامك. سترى **استخداماً عالياً لوحدة GPU أو NPU** بناءً على ما إذا كان النموذج الذي اخترته **Hybrid** أو **NPU** على التوالي. باستخدام مدير المهام، يمكنك التأكد من أنك تقوم بتشغيل النموذج محلياً.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. انقر على القائمة المنسدلة في الزاوية العلوية اليسرى من الواجهة. سيؤدي هذا إلى عرض نماذج Lemonade المثبتة لديك. اختر واحداً للمتابعة. (مثال: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. أدخل رسالة إلى نموذج LLM وانقر على إرسال (أو اضغط على Enter). سيستغرق نموذج LLM بضع ثوانٍ ليتم تحميله في الذاكرة ثم سترى الاستجابة تتدفق.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. سيستجيب النموذج في الدردشة.
<!-- @os:end -->

هذا يثبت أن Open WebUI يمكنه إرسال الطلبات إلى Lemonade باستخدام نقطة نهاية الدردشة المتوافقة مع OpenAI.

---

### النشاط 2: تحميل صورة وطرح أسئلة (الرؤية)

يتطلب هذا نموذجاً يدعم إدخال الصور (نموذج Vision أو Multimodal).

1. انقر على أيقونة التصفية، اختر "By Category"، ثم اختر نموذجاً من قسم **Vision** (مثال: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. انقر على زر **`+`** في مربع الرسالة وقم بتحميل صورة
3. اطرح شيئاً يفرض فهماً حقيقياً للصورة: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. يجيب النموذج بناءً على محتوى الصورة، وليس نصاً عاماً.

هذا يوضح أن Open WebUI يمكنه إرسال طلبات متعددة الوسائط (نص + صورة) عبر الخلفية (Lemonade) إلى نموذج رؤية.

---

<!-- @os:windows -->
### النشاط 3: توليد صورة من نص وصفي (Stable Diffusion)

نماذج Stable Diffusion لا تدعم توليد النصوص، بل تولّد الصور فقط عبر واجهة Images API.

#### الخطوة 1: تهيئة توليد الصور في Open WebUI

1. في واجهة Lemonade الرسومية (`http://localhost:13305`)، ابحث عن `SDXL-Turbo` (سريع) أو `SDXL-Base-1.0` (جودة أعلى) وقم بتنزيله.
2. اذهب إلى **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. اضبط:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` أو `SDXL-Base-1.0`
4. إذا كنت تريد إضافة المزيد من المعلمات، أضفها إلى حقل النص بصيغة JSON. على سبيل المثال: `{ "steps": 4, "cfg_scale": 1 }`. راجع المعلمات المتاحة على [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. احفظ
#### الخطوة 2: تفعيل توليد الصور للنموذج
تضمن هذه الخطوة تفعيل توليد الصور كإحدى قدرات النموذج.
1. اذهب إلى **إعدادات المسؤول → النماذج** (http://localhost:8080/admin/settings/models) واختر نموذجك
2. فعّل `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### الخطوة 3: توليد صورة من شاشة الدردشة

1. عد إلى الدردشة على `http://localhost:8080`.
2. اختر **نموذج توليد نصوص (LLM)** من القائمة المنسدلة للنماذج (مثال: Qwen، Llama). **لا تختر نموذج Stable Diffusion** لأن هذا محدد لنموذج الدردشة.
3. في منطقة الرسالة، انقر على **Integrations**، وفعّل خيار **Image**.
4. استخدم موجّهًا مثل: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. يتم توليد صورة وتظهر في الدردشة.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

يُثبت هذا أن Open WebUI يمكنه تنسيق سير عمل "ثنائي الجزء":
  - يساعد النموذج اللغوي في تحسين الموجّه
  - يتم توليد الصورة عبر نقطة نهاية الصور الخاصة بـ Lemonade باستخدام Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### النشاط 3: توليد صورة من موجّه نصي (Stable Diffusion)

لا تدعم نماذج Stable Diffusion توليد النصوص، فهي تولّد الصور فقط عبر واجهة برمجة تطبيقات الصور (Images API).

#### الخطوة 1: إعداد توليد الصور في Open WebUI

1. في واجهة Lemonade الرسومية (`http://localhost:13305`)، ابحث عن `SDXL-Turbo` (سريع) أو `SDXL-Base-1.0` (جودة أعلى) وقم بتنزيله.
2. اذهب إلى **إعدادات المسؤول → الصور** (http://localhost:8080/admin/settings/images)
3. اضبط الإعدادات التالية:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` أو `SDXL-Base-1.0`
4. إذا رغبت في إضافة مزيد من المعاملات، أضفها في حقل النص بصيغة JSON. على سبيل المثال: `{ "steps": 4, "cfg_scale": 1 }`. راجع المعاملات المتاحة في [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. احفظ الإعدادات


#### الخطوة 2: تفعيل توليد الصور للنموذج
تضمن هذه الخطوة تفعيل توليد الصور كإحدى قدرات النموذج.
1. اذهب إلى **إعدادات المسؤول → النماذج** (http://localhost:8080/admin/settings/models) واختر نموذجك
2. فعّل `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### الخطوة 3: توليد صورة من شاشة الدردشة

1. عد إلى الدردشة على `http://localhost:8080`.
2. اختر **نموذج توليد نصوص (LLM)** من القائمة المنسدلة للنماذج (مثال: Qwen، Llama). **لا تختر نموذج Stable Diffusion** لأن هذا محدد لنموذج الدردشة.
3. في منطقة الرسالة، انقر على **Integrations**، وفعّل خيار **Image**.
4. استخدم موجّهًا مثل: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. يتم توليد صورة وتظهر في الدردشة.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

يُثبت هذا أن Open WebUI يمكنه تنسيق سير عمل "ثنائي الجزء":
  - يساعد النموذج اللغوي في تحسين الموجّه
  - يتم توليد الصورة عبر نقطة نهاية الصور الخاصة بـ Lemonade باستخدام Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## استكشاف الأخطاء وإصلاحها

### "لا تظهر أي نماذج في Open WebUI"
- أولًا، تحقق من Lemonade: افتح `http://localhost:13305/api/v1/models` في متصفح وتأكد من إدراج نماذجك وتنزيلها
- بعد ذلك، تحقق من اتصال Open WebUI: اذهب إلى **إعدادات المسؤول → الاتصالات** على `http://localhost:8080/admin/settings/connections` وتحقق من أن Base URL هو `http://localhost:13305/api/v1`

### رسالة الخطأ "This model does not support chat completion"
- لقد اخترت نموذج صور (SDXL-Turbo / SDXL-Base-1.0) في القائمة المنسدلة لنموذج الدردشة.
- **الحل**: اختر نموذج توليد نصوص (LLM) للدردشة، واستخدم مفتاح Image وإعدادات الصور للتوليد.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### أخطاء/انقطاعات مهلة في توليد الصور
- ابدأ أولًا بـ `SDXL-Turbo` (سريع، خطوات أقل)
- بمجرد أن يعمل بنجاح، بدّل نموذج الصور إلى `SDXL-Base-1.0` للحصول على جودة أعلى

---

## الخطوات التالية

الآن أصبح لديك **"مجموعة ذكاء اصطناعي محلية"** عاملة، واجهة مستخدم واحدة تتحكم في أنواع متعددة من النماذج عبر واجهة برمجة تطبيقات موحدة.

فيما يلي ثلاثة توسعات تفتح سير عمل جديد تمامًا:

### 1. تحويل الكلام إلى نص باستخدام Whisper

جرّب تحويل الصوت إلى نص باستخدام نموذج Whisper، ثم غذّه إلى نموذج لغوي للتلخيص أو استخراج المهام أو إعادة الصياغة. هذا هو الأساس لملاحظات الاجتماعات والمساعدين الصوتيين.

### 2. برمجة Python داخل Open WebUI

استخدم تجربة تنفيذ الكود المدمجة في Open WebUI لتشغيل مقتطفات Python، وفحص المخرجات، والتكرار بشكل أسرع—دون مغادرة الواجهة. [مرجع](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. عرض HTML داخل Open WebUI

اعرض مخرجات HTML مباشرة في الواجهة. هذا قوي بشكل مفاجئ لبناء نماذج أولية سريعة، وتقارير منسّقة، ومقتطفات تفاعلية. [مرجع](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## المراجع

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [وثائق Lemonade Server](https://lemonade-server.ai/docs)
- [واجهة سطر أوامر Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [دليل تكامل Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [مواصفات واجهة برمجة تطبيقات Lemonade Server (نقاط النهاية)](https://lemonade-server.ai/docs/server/server_spec)
- [شرح مرئي (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [شرح مرئي (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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