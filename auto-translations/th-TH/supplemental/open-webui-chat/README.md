<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> เพลย์บุ๊กนี้ต้องการหน่วยความจำระบบขั้นต่ำ **32GB**
<!-- @device:end -->

## ภาพรวม

[Open WebUI](https://docs.openwebui.com) เป็นอินเทอร์เฟซแบบเบราว์เซอร์ที่โฮสต์เองได้ (self-hosted) ซึ่งมอบประสบการณ์การใช้งานแชทบอทที่คุ้นเคย ในขณะที่ทำหน้าที่เป็นฟรอนต์เอนด์สำหรับเซิร์ฟเวอร์โมเดล AI หนึ่งตัวหรือมากกว่า แทนที่จะผูกติดกับผู้ให้บริการเพียงรายเดียว Open WebUI สามารถเชื่อมต่อกับ **แบ็กเอนด์ใดก็ได้ที่เปิดให้ใช้งาน API ที่เข้ากันได้กับ OpenAI** ทำให้คุณสามารถสลับโมเดลและความสามารถต่าง ๆ ได้โดยไม่ต้องเปลี่ยน UI

ในเพลย์บุ๊กนี้ เราใช้ [**Lemonade**](https://lemonade-server.ai) เป็นแบ็กเอนด์ เนื่องจากมันเปิดให้ใช้งาน **เอนด์พอยต์ที่เข้ากันได้กับ OpenAI แบบรวมศูนย์เดียว** ซึ่งรองรับหลายรูปแบบข้อมูล (modalities):
- **Large Language Models (LLMs)** สำหรับการสร้างข้อความ
- **โมเดลวิชัน (Vision models)** สำหรับการทำความเข้าใจภาพ
- **Stable Diffusion** สำหรับการสร้างภาพ
- **โมเดลถอดเสียง (Audio transcription models)** สำหรับการแปลงเสียงพูดเป็นข้อความ

การตั้งค่านี้ช่วยให้คุณสามารถสำรวจ **เวิร์กโฟลว์แบบมัลติโมดัลทั้งหมดตั้งแต่ต้นจนจบ** ได้

---

## สิ่งที่คุณจะได้เรียนรู้

เมื่อจบเพลย์บุ๊กนี้ คุณจะสามารถ:

- เชื่อมต่อ Open WebUI กับแบ็กเอนด์ที่เข้ากันได้กับ OpenAI ในเครื่อง (Lemonade)
- แชทกับ LLM ในเครื่องผ่านเบราว์เซอร์ของคุณ
- อัปโหลดรูปภาพและถามคำถามเกี่ยวกับรูปภาพนั้นกับโมเดลวิชัน
- สร้างภาพจากพรอมต์ข้อความโดยใช้โมเดล Stable Diffusion (SDXL-Turbo / SDXL)
- เข้าใจโมเดลความคิด (mental model) เพื่อให้คุณสามารถใช้แบ็กเอนด์อื่น ๆ ได้ (Ollama, vLLM, llama.cpp server ฯลฯ)

---

## แนวคิดหลัก (โมเดลความคิด)

### สามองค์ประกอบหลัก

| ส่วนประกอบ | ทำหน้าที่อะไร | ตัวอย่าง |
|---|---|---|
| ฟรอนต์เอนด์ (UI) | เว็บแอปที่คุณโต้ตอบด้วย | Open WebUI |
| แบ็กเอนด์ (เซิร์ฟเวอร์โมเดล) | โฮสต์โมเดลและเปิดให้ใช้งานเอนด์พอยต์ HTTP | Lemonade, Ollama, vLLM, llama.cpp server, เซิร์ฟเวอร์ที่เข้ากันได้กับ OpenAI |
| โมเดล | LLM / วิชัน / ดิฟฟิวชัน / โมเดลเสียงตัวจริง | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### เหตุใด "API ที่เข้ากันได้กับ OpenAI" จึงสำคัญ

Open WebUI ถูกสร้างขึ้นโดยอิงตามเอนด์พอยต์มาตรฐานสไตล์ OpenAI เช่น:
  - แชท: `/chat/completions`
  - รายการโมเดล: `/models`
  - การสร้างภาพ: `/images/generations`
  - การถอดเสียง: `/audio/transcriptions`

Lemonade เปิดให้ใช้งานสิ่งเหล่านี้ภายใต้ `http://localhost:13305/api/v1/...`

หากแบ็กเอนด์รองรับเอนด์พอยต์เหล่านั้น Open WebUI ก็สามารถสื่อสารกับมันได้โดยแทบไม่ต้องตั้งค่าเพิ่มเติม นี่คือเหตุผลที่เราสามารถสลับแบ็กเอนด์ได้โดยไม่ต้องเปลี่ยนเวิร์กโฟลว์ของเรา

#### สองบริการ สองพอร์ต

ตลอดเพลย์บุ๊กนี้ คุณจะทำงานกับบริการแยกกันสองตัว:

| บริการ | URL | สิ่งที่คุณทำที่นั่น |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | เรียกดู ดาวน์โหลด และจัดการโมเดล |
| **Open WebUI** | `http://localhost:8080` | แชท อัปโหลดรูปภาพ สร้างภาพ — UI ที่ผู้ใช้โต้ตอบด้วย |

Lemonade รันโมเดลต่าง ๆ ส่วน Open WebUI คืออินเทอร์เฟซที่คุณโต้ตอบด้วย ใช้ Lemonade GUI เพื่อดาวน์โหลดโมเดลของคุณก่อน แล้วจึงนำมาใช้จาก Open WebUI

---

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การตั้งค่าครั้งแรก

เพลย์บุ๊กนี้ต้องการให้ Lemonade รันอยู่ในฐานะแบ็กเอนด์ และในระบบ Linux ต้องมีคอนเทนเนอร์เอนจิน (Podman) เพื่อรัน Open WebUI ตั้งค่าสิ่งเหล่านี้ก่อนติดตั้ง Open WebUI

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

## การดาวน์โหลดโมเดลใน Lemonade

ก่อนติดตั้ง Open WebUI ตรวจสอบให้แน่ใจว่าโมเดลที่คุณต้องการใช้ได้ถูกดาวน์โหลดและพร้อมใช้งานใน Lemonade แล้ว

1. เปิด Lemonade GUI ที่ `http://localhost:13305`
2. เรียกดูโมเดลที่มีให้ใช้งานและดาวน์โหลดโมเดลที่คุณต้องการใช้ (เช่น LLM สำหรับแชท โมเดลวิชัน และ/หรือโมเดล Stable Diffusion สำหรับการสร้างภาพ)
3. ยืนยันว่า API สามารถเข้าถึงได้โดยไปที่ `http://localhost:13305/api/v1/models` ในเบราว์เซอร์ของคุณ — คุณควรเห็นรายการโมเดลที่คุณดาวน์โหลดไว้

> โมเดลจะต้องถูกดาวน์โหลดใน **Lemonade** (`localhost:13305`) ก่อนที่จะปรากฏใน **Open WebUI** (`localhost:8080`) หากโมเดลไม่ปรากฏใน Open WebUI ในภายหลัง ให้กลับมาตรวจสอบที่ Lemonade ก่อน


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

## การติดตั้ง Open WebUI

<!-- @os:windows -->
### 1. ติดตั้ง Python 3.12

Open WebUI ต้องการ **Python 3.12** — จะไม่สามารถติดตั้งบน Python 3.13 ขึ้นไปได้ Windows Python Launcher (`py`) ช่วยให้คุณติดตั้ง 3.12 ควบคู่ไปกับ Python เวอร์ชันที่มีอยู่แล้วได้โดยไม่ขัดแย้งกัน

```powershell
winget install Python.Python.3.12
```

ปิดและเปิดเทอร์มินัลของคุณใหม่หลังจากติดตั้ง จากนั้นตรวจสอบ:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **หมายเหตุ:** ระบบของคุณมี Python 3.13 ติดตั้งมาให้ล่วงหน้า การติดตั้ง 3.12 จะไม่ส่งผลกระทบต่อสิ่งนี้ — `python` ยังคงใช้ 3.13 ต่อไป และ `py -3.12` จะเรียกใช้ 3.12 เฉพาะเมื่อคุณต้องการเท่านั้น
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

### 2. สร้างสภาพแวดล้อมเสมือน (virtual environment) และติดตั้ง Open WebUI

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
ตอนนี้เราจะใช้บริการ Podman เพื่อบรรจุการติดตั้ง Open WebUI ของเราในคอนเทนเนอร์

โปรดดาวน์โหลดไฟล์ต่อไปนี้ไปไว้ในไดเรกทอรีที่คุณเลือก: [compose.yml](assets/compose.yml)

ในไดเรกทอรีนั้น ให้รันคำสั่งต่อไปนี้:

```bash
podman compose up -d
```

คำสั่งนี้จะดึงอิมเมจของ Open WebUI มาและเขียนลงในที่จัดเก็บถาวร (persistent storage)

เปิดใช้งาน Open WebUI โดยพิมพ์ `localhost:8080` ในแถบที่อยู่ของเบราว์เซอร์ของคุณ

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

> **เคล็ดลับ**: Open WebUI ยังมีตัวเลือกการติดตั้งอื่น ๆ ให้ใช้งานบน [GitHub](https://github.com/open-webui/open-webui) ของพวกเขาด้วย
## Starting Open WebUI Server

<!-- @os:windows -->
- รันคำสั่งต่อไปนี้เพื่อเปิดเซิร์ฟเวอร์ HTTP ของ Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- ในเบราว์เซอร์ ให้ไปที่ `http://localhost:8080`
- Open WebUI จะขอให้คุณสร้างบัญชีผู้ดูแลระบบภายในเครื่อง เมื่อคุณลงชื่อเข้าใช้แล้ว คุณจะเห็นอินเทอร์เฟซแชท

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> เปิดหน้าต่างเทอร์มินัลทิ้งไว้ การปิดหน้าต่างนี้จะหยุดการทำงานของ Open WebUI
<!-- @os:end -->

<!-- @os:linux -->
> คอนเทนเนอร์จะทำงานอยู่เบื้องหลัง จากไดเรกทอรีที่มีไฟล์ `compose.yml` คุณสามารถจัดการได้ด้วย `podman compose down` (หยุด) และ `podman compose up -d` (เริ่ม) บัญชีและการตั้งค่าของคุณจะถูกเก็บไว้ในโวลุ่ม `open_webui_data`
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

## Connecting Open WebUI to Lemonade

เมื่อทั้งสองบริการทำงานอยู่แล้ว — Lemonade บน `localhost:13305` และ Open WebUI บน `localhost:8080` — ให้เชื่อมต่อทั้งสองเข้าด้วยกันเพื่อให้ Open WebUI สามารถใช้โมเดลของ Lemonade ได้

ใน Open WebUI:

1. คลิก **ไอคอนโปรไฟล์ผู้ใช้** ที่มุมขวาบน จากนั้นเลือก **Settings**

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. ในแผงการตั้งค่า คลิก **Admin Settings** ที่มุมล่างซ้าย

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. ในแถบด้านข้างของ Admin Settings คลิก **Connections** (หรือไปที่ `http://localhost:8080/admin/settings/connections` โดยตรง)

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. ภายใต้ **OpenAI API** เพิ่มการเชื่อมต่อใหม่:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (เครื่องหมายขีดตัวเดียวใช้ได้สำหรับการใช้งานภายในเครื่อง)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. ตรวจสอบให้แน่ใจว่าภายใต้ **"Manage OpenAI API Connections"** มีเพียง `http://localhost:13305/api/v1` เท่านั้นที่เปิดใช้งาน ปิดการเชื่อมต่ออื่น ๆ (เช่น การเชื่อมต่อ OpenAI เริ่มต้น)

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. คลิก **Save**

7. **(แนะนำ)** ปิดฟีเจอร์การสร้างเนื้อหาอัตโนมัติเพื่อให้ Open WebUI ตอบสนองได้ดีเมื่อใช้งานร่วมกับ LLM ในเครื่อง ไปที่ **Admin Settings → Settings → Interface** และปิด:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. คลิก **Save** จากนั้นกลับไปที่ `http://localhost:8080`
9. คลิกที่ดรอปดาวน์เลือกโมเดล — คุณควรเห็นโมเดลที่คุณดาวน์โหลดจาก Lemonade

---

## Main Activities

ตอนนี้คุณตั้งค่าทุกอย่างเรียบร้อยแล้ว มาดูสิ่งที่น่าสนใจสามอย่างที่สามารถทำได้กัน

---

### Activity 1: Chat with a Local LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. คลิกเมนูดรอปดาวน์ที่มุมซ้ายบนของอินเทอร์เฟซ ซึ่งจะแสดงโมเดล Lemonade ที่คุณติดตั้งไว้ เลือกโมเดลหนึ่งเพื่อดำเนินการต่อ (ตัวอย่าง: `Qwen3-4B-Hybrid`)

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. พิมพ์ข้อความถึง LLM แล้วคลิกส่ง (หรือกด Enter) LLM จะใช้เวลาสักครู่ในการโหลดเข้าสู่หน่วยความจำ จากนั้นคุณจะเห็นการตอบกลับแบบสตรีมเข้ามา

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. คลิกเมนูดรอปดาวน์ที่มุมซ้ายบนของอินเทอร์เฟซ ซึ่งจะแสดงโมเดล Lemonade ที่คุณติดตั้งไว้ เลือกโมเดลหนึ่งเพื่อดำเนินการต่อ (ตัวอย่าง: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. พิมพ์ข้อความถึง LLM แล้วคลิกส่ง (หรือกด Enter) LLM จะใช้เวลาสักครู่ในการโหลดเข้าสู่หน่วยความจำ จากนั้นคุณจะเห็นการตอบกลับแบบสตรีมเข้ามา

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. โมเดลจะตอบกลับในหน้าต่างแชท

4. ในขณะนี้ ให้เปิด `Task Manager` บนระบบของคุณ คุณจะเห็น **การใช้งาน GPU หรือ NPU ในระดับสูง** ขึ้นอยู่กับว่าโมเดลที่คุณเลือกเป็น **Hybrid** หรือ **NPU** ตามลำดับ การใช้ Task Manager จะช่วยยืนยันได้ว่าคุณกำลังรันโมเดลอยู่ในเครื่องของคุณเอง

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. คลิกเมนูดรอปดาวน์ที่มุมซ้ายบนของอินเทอร์เฟซ ซึ่งจะแสดงโมเดล Lemonade ที่คุณติดตั้งไว้ เลือกโมเดลหนึ่งเพื่อดำเนินการต่อ (ตัวอย่าง: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. พิมพ์ข้อความถึง LLM แล้วคลิกส่ง (หรือกด Enter) LLM จะใช้เวลาสักครู่ในการโหลดเข้าสู่หน่วยความจำ จากนั้นคุณจะเห็นการตอบกลับแบบสตรีมเข้ามา

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. โมเดลจะตอบกลับในหน้าต่างแชท
<!-- @os:end -->

การทำเช่นนี้ยืนยันว่า Open WebUI สามารถส่งคำขอไปยัง Lemonade ผ่านทาง endpoint การแชทที่รองรับ OpenAI-compatible ได้

---

### Activity 2: Upload an Image and Ask Questions (Vision)

การทำสิ่งนี้ต้องใช้โมเดลที่รองรับการป้อนภาพ (โมเดล Vision หรือ Multimodal)

1. คลิกไอคอนตัวกรอง เลือก "By Category" จากนั้นเลือกโมเดลจากหมวด **Vision** (เช่น `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. คลิกปุ่ม **`+`** ในกล่องข้อความและอัปโหลดรูปภาพ
3. ถามคำถามที่บังคับให้ต้องเข้าใจภาพจริง ๆ: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. โมเดลจะตอบโดยอ้างอิงจากเนื้อหาของภาพ ไม่ใช่ข้อความทั่วไป

สิ่งนี้แสดงให้เห็นว่า Open WebUI สามารถส่งคำขอแบบ multimodal (ข้อความ + ภาพ) ผ่านทางแบ็กเอนด์ (Lemonade) ไปยังโมเดล Vision ได้

---

<!-- @os:windows -->
### Activity 3: Generate an Image from a Text Prompt (Stable Diffusion)

โมเดล Stable Diffusion ไม่รองรับการสร้างข้อความ โมเดลเหล่านี้จะสร้างภาพผ่าน Images API เท่านั้น

#### Step 1: Configure Image Generation in Open WebUI

1. ใน Lemonade GUI (`http://localhost:13305`) ให้ค้นหา `SDXL-Turbo` (เร็ว) หรือ `SDXL-Base-1.0` (คุณภาพสูงกว่า) แล้วดาวน์โหลด
2. ไปที่ **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. ตั้งค่า:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` หรือ `SDXL-Base-1.0`
4. หากคุณต้องการเพิ่มพารามิเตอร์เพิ่มเติม ให้เพิ่มลงในช่องข้อความในรูปแบบ JSON ตัวอย่างเช่น: `{ "steps": 4, "cfg_scale": 1 }` ดูพารามิเตอร์ที่มีให้เพิ่มเติมได้ที่ [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. บันทึก
#### ขั้นตอนที่ 2: อนุญาตการสร้างภาพสำหรับโมเดล
ขั้นตอนนี้ช่วยให้มั่นใจว่าคุณเปิดใช้งานการสร้างภาพเป็นความสามารถของโมเดลของคุณ
1. ไปที่ **Admin Settings → Models** (http://localhost:8080/admin/settings/models) และเลือกโมเดลของคุณ
2. เปิดใช้งาน `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### ขั้นตอนที่ 3: สร้างภาพจากหน้าจอแชท

1. กลับไปที่หน้าแชทที่ `http://localhost:8080`
2. เลือก **Text Generation LLM** ในเมนูดรอปดาวน์ของโมเดล (ตัวอย่าง: Qwen, Llama) **อย่าเลือกโมเดล Stable Diffusion** เนื่องจากนี่คือตัวเลือกโมเดลสำหรับแชท
3. ในพื้นที่ข้อความ คลิกที่ **Integrations** แล้วเปิดสวิตช์ **Image**
4. ใช้พรอมต์เช่น: `A cinematic photo of heavy traffic at sunset, ultra detailed`
5. ภาพจะถูกสร้างขึ้นและปรากฏในแชท

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

สิ่งนี้แสดงให้เห็นว่า Open WebUI สามารถประสานงานเวิร์กโฟลว์แบบ "สองส่วน" ได้:
  - LLM ช่วยปรับปรุงพรอมต์ให้ดีขึ้น
  - ภาพถูกสร้างขึ้นผ่านทาง Images endpoint ของ Lemonade โดยใช้ Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### กิจกรรมที่ 3: สร้างภาพจากพรอมต์ข้อความ (Stable Diffusion)

โมเดล Stable Diffusion ไม่รองรับการสร้างข้อความ ทำได้เพียงสร้างภาพผ่าน Images API เท่านั้น

#### ขั้นตอนที่ 1: กำหนดค่าการสร้างภาพใน Open WebUI

1. ใน Lemonade GUI (`http://localhost:13305`) ค้นหา `SDXL-Turbo` (เร็ว) หรือ `SDXL-Base-1.0` (คุณภาพสูงกว่า) แล้วดาวน์โหลด
2. ไปที่ **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. ตั้งค่า:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` หรือ `SDXL-Base-1.0`
4. หากต้องการเพิ่มพารามิเตอร์เพิ่มเติม ให้เพิ่มลงในช่องข้อความในรูปแบบ JSON ตัวอย่างเช่น: `{ "steps": 4, "cfg_scale": 1 }` ดูพารามิเตอร์ที่ใช้ได้ที่ [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. บันทึก


#### ขั้นตอนที่ 2: อนุญาตการสร้างภาพสำหรับโมเดล
ขั้นตอนนี้ช่วยให้มั่นใจว่าคุณเปิดใช้งานการสร้างภาพเป็นความสามารถของโมเดลของคุณ
1. ไปที่ **Admin Settings → Models** (http://localhost:8080/admin/settings/models) และเลือกโมเดลของคุณ
2. เปิดใช้งาน `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### ขั้นตอนที่ 3: สร้างภาพจากหน้าจอแชท

1. กลับไปที่หน้าแชทที่ `http://localhost:8080`
2. เลือก **Text Generation LLM** ในเมนูดรอปดาวน์ของโมเดล (ตัวอย่าง: Qwen, Llama) **อย่าเลือกโมเดล Stable Diffusion** เนื่องจากนี่คือตัวเลือกโมเดลสำหรับแชท
3. ในพื้นที่ข้อความ คลิกที่ **Integrations** แล้วเปิดสวิตช์ **Image**
4. ใช้พรอมต์เช่น: `A cinematic photo of heavy traffic at sunset, ultra detailed`
5. ภาพจะถูกสร้างขึ้นและปรากฏในแชท

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

สิ่งนี้แสดงให้เห็นว่า Open WebUI สามารถประสานงานเวิร์กโฟลว์แบบ "สองส่วน" ได้:
  - LLM ช่วยปรับปรุงพรอมต์ให้ดีขึ้น
  - ภาพถูกสร้างขึ้นผ่านทาง Images endpoint ของ Lemonade โดยใช้ Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## การแก้ไขปัญหา

### "ไม่มีโมเดลแสดงขึ้นใน Open WebUI"
- ก่อนอื่น ให้ตรวจสอบ Lemonade: เปิด `http://localhost:13305/api/v1/models` ในเบราว์เซอร์และยืนยันว่าโมเดลของคุณถูกแสดงและดาวน์โหลดแล้ว
- จากนั้น ตรวจสอบการเชื่อมต่อ Open WebUI: ไปที่ **Admin Settings → Connections** ที่ `http://localhost:8080/admin/settings/connections` และตรวจสอบว่า Base URL คือ `http://localhost:13305/api/v1`

### ข้อความแสดงข้อผิดพลาด "This model does not support chat completion"
- คุณเลือกโมเดลภาพ (SDXL-Turbo / SDXL-Base-1.0) ในเมนูดรอปดาวน์ของโมเดลแชท
- **วิธีแก้ไข**: เลือก LLM สำหรับการแชท และใช้สวิตช์ Image พร้อมการตั้งค่า Images สำหรับการสร้างภาพ
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### ข้อผิดพลาด/การหมดเวลาในการสร้างภาพ
- เริ่มต้นด้วย `SDXL-Turbo` ก่อน (เร็ว ขั้นตอนน้อยกว่า)
- เมื่อใช้งานได้แล้ว ให้เปลี่ยนโมเดลภาพเป็น `SDXL-Base-1.0` เพื่อคุณภาพที่ดีขึ้น

---

## ขั้นตอนถัดไป

ตอนนี้คุณมี **'local AI stack'** ที่ใช้งานได้แล้ว ซึ่งเป็น UI เดียวที่ควบคุมโมเดลหลายประเภทผ่าน API มาตรฐาน

นี่คือการขยายผลสามอย่างที่จะปลดล็อกเวิร์กโฟลว์ใหม่ทั้งหมด:

### 1. Speech-to-Text ด้วย Whisper

ลองแปลงเสียงเป็นข้อความโดยใช้โมเดล Whisper จากนั้นป้อนเข้าสู่ LLM เพื่อสรุปเนื้อหา รายการสิ่งที่ต้องทำ หรือเขียนใหม่ นี่คือรากฐานสำหรับบันทึกการประชุมและผู้ช่วยที่ขับเคลื่อนด้วยเสียง

### 2. การเขียนโค้ด Python ภายใน Open WebUI

ใช้ประสบการณ์การรันโค้ดในตัวของ Open WebUI เพื่อรันสคริปต์ Python ตรวจสอบผลลัพธ์ และทำงานซ้ำได้เร็วขึ้น—โดยไม่ต้องออกจาก UI [ข้อมูลอ้างอิง](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. การแสดงผล HTML ภายใน Open WebUI

แสดงผลลัพธ์ HTML โดยตรงในอินเทอร์เฟซ นี่มีประสิทธิภาพอย่างน่าประหลาดใจสำหรับการสร้างต้นแบบอย่างรวดเร็ว รายงานที่จัดรูปแบบ และสนิปเพตแบบโต้ตอบ [ข้อมูลอ้างอิง](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## เอกสารอ้างอิง

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [เอกสาร Lemonade Server](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [คู่มือการผสานรวม Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [ข้อกำหนด API ของ Lemonade Server (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [วิดีโอสาธิต (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [วิดีโอสาธิต (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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