<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Bu playbook, en az **32 GB** sistem belleği gerektirir.
<!-- @device:end -->

## Genel Bakış

[Open WebUI](https://docs.openwebui.com), tanıdık bir sohbet botu deneyimi sunarken bir veya daha fazla yapay zeka model sunucusu için ön uç görevi gören, kendi kendine barındırılan, tarayıcı tabanlı bir arayüzdür. Tek bir sağlayıcıya bağlı kalmak yerine Open WebUI, **OpenAI uyumlu bir API sunan herhangi bir arka uca** bağlanabilir; böylece kullanıcı arayüzünü değiştirmeden modelleri ve yetenekleri değiştirebilirsiniz.

Bu playbook'ta, **birleşik bir OpenAI uyumlu uç nokta** sunduğu için arka uç olarak [**Lemonade**](https://lemonade-server.ai) kullanıyoruz. Bu uç nokta birden fazla modaliteyi destekler:
- Metin üretimi için **Büyük Dil Modelleri (LLM)**
- Görüntü anlama için **Görü modelleri**
- Görüntü üretimi için **Stable Diffusion**
- Konuşmadan metne dönüştürme için **Ses transkripsiyon modelleri**

Bu kurulum, **uçtan uca eksiksiz çok modlu iş akışını** keşfetmenizi sağlar.

---

## Neler Öğreneceksiniz

Bu playbook'un sonunda şunları yapabileceksiniz:

- Open WebUI'yi yerel bir OpenAI uyumlu arka uca (Lemonade) bağlamak
- Tarayıcınızdan yerel bir LLM ile sohbet etmek
- Bir görüntü yükleyip görü modeline bu görüntüyle ilgili sorular sormak
- Stable Diffusion modelleri (SDXL-Turbo / SDXL) kullanarak metin istemlerinden görüntü üretmek
- Diğer arka uçları (Ollama, vLLM, llama.cpp server vb.) kullanabilmek için zihinsel modeli anlamak

---

## Temel Kavramlar (Zihinsel Model)

### Üç Bileşen

| Parça | Ne işe yarar | Örnekler |
|---|---|---|
| Ön Uç (UI) | Etkileşimde bulunduğunuz web uygulaması | Open WebUI |
| Arka Uç (Model Sunucusu) | Modelleri barındırır ve HTTP uç noktaları sunar | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI uyumlu sunucular |
| Modeller | Gerçek LLM / Görü / Diffusion / Ses modelleri | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### "OpenAI uyumlu API" neden önemlidir

Open WebUI, aşağıdaki gibi standart OpenAI tarzı uç noktalar üzerine inşa edilmiştir:
  - Sohbet: `/chat/completions`
  - Model listesi: `/models`
  - Görüntü üretimi: `/images/generations`
  - Ses transkripsiyonu: `/audio/transcriptions`

Lemonade bunları `http://localhost:13305/api/v1/...` altında sunar.

Bir arka uç bu uç noktaları destekliyorsa Open WebUI, minimum kurulumla onunla iletişim kurabilir. Bu nedenle iş akışımızı değiştirmeden arka uçları değiştirebiliriz.

#### İki hizmet, iki port

Bu playbook boyunca iki ayrı hizmetle çalışacaksınız:

| Hizmet | URL | Orada ne yaparsınız |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modellere göz atın, indirin ve yönetin |
| **Open WebUI** | `http://localhost:8080` | Sohbet edin, görüntü yükleyin, görüntü üretin — kullanıcıya yönelik UI |

Lemonade modelleri çalıştırır; Open WebUI ise etkileşimde bulunduğunuz arayüzdür. Önce modellerinizi indirmek için Lemonade GUI'yi kullanın, ardından bunları Open WebUI üzerinden kullanın.

---

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @require:software-update -->
<!-- @device:end -->

## Tek Seferlik Kurulum

Bu playbook, arka uç olarak çalışan Lemonade'e ve Linux'ta Open WebUI'yi çalıştırmak için bir konteyner motoruna (Podman) ihtiyaç duyar. Open WebUI'yi kurmadan önce bunları ayarlayın.

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

## Lemonade'de Model İndirme

Open WebUI'yi kurmadan önce, kullanmak istediğiniz modellerin Lemonade'de indirilmiş ve hazır olduğundan emin olun.

1. `http://localhost:13305` adresinden Lemonade GUI'yi açın.
2. Mevcut modellere göz atın ve kullanmak istediklerinizi indirin (örn. sohbet için bir LLM, bir görü modeli ve/veya görüntü üretimi için bir Stable Diffusion modeli).
3. Tarayıcınızda `http://localhost:13305/api/v1/models` adresini ziyaret ederek API'nin erişilebilir olduğunu doğrulayın — indirilen modellerinizin listelendiğini görmelisiniz.

> Modellerin **Open WebUI**'de (`localhost:8080`) görünebilmesi için önce **Lemonade**'de (`localhost:13305`) indirilmiş olması gerekir. Bir model daha sonra Open WebUI'de görünmüyorsa buraya geri dönün ve önce Lemonade'i kontrol edin.


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

## Open WebUI'yi Kurma

<!-- @os:windows -->
### 1. Python 3.12'yi Kurun

Open WebUI, **Python 3.12** gerektirir — Python 3.13 ve üzerinde kurulmaz. Windows Python Başlatıcısı (`py`), mevcut Python sürümleriyle çakışma olmadan 3.12'yi yan yana kurmanıza olanak tanır.

```powershell
winget install Python.Python.3.12
```

Kurulumdan sonra terminalinizi kapatıp yeniden açın, ardından doğrulayın:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Not:** Sisteminizde önceden Python 3.13 kurulu olarak gelir. 3.12'yi kurmak bunu etkilemez — `python` 3.13'ü kullanmaya devam eder ve `py -3.12` yalnızca ihtiyaç duyduğunuzda 3.12'yi hedefler.
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

### 2. Sanal ortam oluşturun ve Open WebUI'yi kurun

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
Open WebUI kurulumumuzu konteynerize etmek için Podman hizmetini kullanacağız.

Lütfen aşağıdaki dosyayı istediğiniz bir dizine indirin: [compose.yml](assets/compose.yml)

O dizinde aşağıdaki komutu çalıştırın:

```bash
podman compose up -d
```

Bu işlem Open WebUI imajını çeker ve kalıcı depolamaya yazar.

Tarayıcınızın adres çubuğuna `localhost:8080` yazarak Open WebUI'yi başlatın.

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

> **İpucu**: Open WebUI, [GitHub](https://github.com/open-webui/open-webui) sayfasında başka kurulum seçenekleri de sunmaktadır.

## Open WebUI Sunucusunu Başlatma

<!-- @os:windows -->
- Open WebUI HTTP sunucusunu başlatmak için aşağıdaki komutu çalıştırın:
```bash
open-webui serve
```
<!-- @os:end -->

- Bir tarayıcıda `http://localhost:8080` adresine gidin.
- Open WebUI sizden yerel bir yönetici hesabı oluşturmanızı isteyecektir. Oturum açtıktan sonra sohbet arayüzünü göreceksiniz.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Terminal penceresini açık tutun. Kapatırsanız Open WebUI durur.
<!-- @os:end -->

<!-- @os:linux -->
> Konteyner arka planda çalışır. `compose.yml` dosyasını içeren dizinden `podman compose down` (durdur) ve `podman compose up -d` (başlat) komutlarıyla yönetin. Hesaplarınız ve ayarlarınız `open_webui_data` biriminde kalıcı olarak saklanır.
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

## Open WebUI'yi Lemonade'e Bağlama

Her iki hizmet de çalışır durumdayken — Lemonade `localhost:13305`'te ve Open WebUI `localhost:8080`'de — Open WebUI'nin Lemonade modellerini kullanabilmesi için bunları birbirine bağlayın.

Open WebUI'de:

1. Sağ üst köşedeki **kullanıcı profili simgesine** tıklayın, ardından **Ayarlar**'ı seçin.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Ayarlar panelinde, sol alttaki **Yönetici Ayarları**'na tıklayın.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Yönetici Ayarları kenar çubuğunda **Bağlantılar**'a tıklayın (veya doğrudan `http://localhost:8080/admin/settings/connections` adresine gidin).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. **OpenAI API** altında yeni bir bağlantı ekleyin:
   - **Temel URL:** `http://localhost:13305/api/v1`
   - **API Anahtarı:** `-` (yerel kullanım için tek tire yeterlidir)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. **"OpenAI API Bağlantılarını Yönet"** altında yalnızca `http://localhost:13305/api/v1`'in etkin olduğundan emin olun. Diğer bağlantıları (örn. varsayılan OpenAI bağlantısı) devre dışı bırakın.

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. **Kaydet**'e tıklayın.

7. **(Önerilen)** Open WebUI'nin yerel LLM'lerle duyarlı kalması için otomatik üretim özelliklerini devre dışı bırakın. **Yönetici Ayarları → Ayarlar → Arayüz** bölümüne gidin ve şunları kapatın:
   - Başlık Üretimi
   - Takip Sorusu Üretimi
   - Etiket Üretimi

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. **Kaydet**'e tıklayın, ardından `http://localhost:8080` adresine geri dönün.
9. Model açılır menüsüne tıklayın — Lemonade'den indirdiğiniz modelleri görmelisiniz.

---

## Ana Etkinlikler

Artık her şey hazır. Yapabileceğiniz üç ilginç şeye bakalım.

---

### Etkinlik 1: Yerel Bir LLM ile Sohbet Etme
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Arayüzün sol üst köşesindeki açılır menüye tıklayın. Bu, kurulu Lemonade modellerinizi görüntüler. Devam etmek için birini seçin. (örnek: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. LLM'e bir mesaj girin ve gönder'e tıklayın (veya Enter'a basın). LLM'nin belleğe yüklenmesi birkaç saniye sürecek, ardından yanıtın aktığını göreceksiniz.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Arayüzün sol üst köşesindeki açılır menüye tıklayın. Bu, kurulu Lemonade modellerinizi görüntüler. Devam etmek için birini seçin. (örnek: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLM'e bir mesaj girin ve gönder'e tıklayın (veya Enter'a basın). LLM'nin belleğe yüklenmesi birkaç saniye sürecek, ardından yanıtın aktığını göreceksiniz.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model sohbette yanıt verecektir.

4. Bu sırada sisteminizde `Görev Yöneticisi`'ni açın. Seçtiğiniz modelin **Hybrid** veya **NPU** olmasına bağlı olarak sırasıyla **yüksek GPU veya NPU kullanımı** göreceksiniz. Görev yöneticisini kullanarak modeli yerel olarak çalıştırdığınızı doğrulayabilirsiniz.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Arayüzün sol üst köşesindeki açılır menüye tıklayın. Bu, kurulu Lemonade modellerinizi görüntüler. Devam etmek için birini seçin. (örnek: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLM'e bir mesaj girin ve gönder'e tıklayın (veya Enter'a basın). LLM'nin belleğe yüklenmesi birkaç saniye sürecek, ardından yanıtın aktığını göreceksiniz.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model sohbette yanıt verecektir.
<!-- @os:end -->

Bu, Open WebUI'nin OpenAI uyumlu sohbet uç noktasını kullanarak Lemonade'e istek gönderip gönderemediğini doğrular.

---

### Etkinlik 2: Görüntü Yükleme ve Soru Sorma (Görü)

Bu, görüntü girişini destekleyen bir model (Görü veya Çok Modlu model) gerektirir.

1. Filtre simgesine tıklayın, "Kategoriye Göre"yi seçin, ardından **Görü** bölümünden bir model seçin (örn. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Mesaj kutusundaki **`+`** düğmesine tıklayın ve bir görüntü yükleyin
3. Gerçek görüntü anlayışını zorlayan bir şey sorun: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model, genel metin yerine görüntü içeriğine dayanarak yanıt verir.

Bu, Open WebUI'nin arka uç (Lemonade) aracılığıyla bir görü modeline çok modlu istekler (metin + görüntü) gönderip gönderemediğini gösterir.

---

<!-- @os:windows -->
### Etkinlik 3: Metin İsteminden Görüntü Üretme (Stable Diffusion)

Stable Diffusion modelleri metin üretimini desteklemez; yalnızca Images API aracılığıyla görüntü üretir.

#### Adım 1: Open WebUI'de Görüntü Üretimini Yapılandırma

1. Lemonade GUI'de (`http://localhost:13305`), `SDXL-Turbo` (hızlı) veya `SDXL-Base-1.0` (daha yüksek kalite) arayın ve indirin.
2. **Yönetici Ayarları → Görüntüler** bölümüne gidin (http://localhost:8080/admin/settings/images)
3. Şunları ayarlayın:
   - **Görüntü Üretimi:** AÇIK
   - **Görüntü Üretim Motoru:** Varsayılan (OpenAI)
   - **OpenAI API Temel URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Anahtarı:** `-`
   - **Model:** `SDXL-Turbo` veya `SDXL-Base-1.0`
4. Daha fazla parametre eklemek istiyorsanız bunları metin alanına JSON olarak ekleyin. Örneğin: `{ "steps": 4, "cfg_scale": 1 }`. Mevcut parametreleri [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html) adresinde görebilirsiniz.

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Kaydedin


#### Adım 2: Model için Görüntü Üretimine İzin Verme
Bu adım, modeliniz için Görüntü Üretimini bir yetenek olarak etkinleştirmenizi sağlar.
1. **Yönetici Ayarları → Modeller** bölümüne gidin (http://localhost:8080/admin/settings/models) ve modelinizi seçin
2. `Image Generation` seçeneğini açın

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Adım 3: Sohbet ekranından görüntü üretme

1. `http://localhost:8080` adresindeki sohbete geri dönün.
2. Model açılır menüsünden bir **Metin Üretimi LLM'i** seçin (örnek: Qwen, Llama). Bu bir sohbet modeli seçicisi olduğundan **Stable Diffusion modeli seçmeyin**.
3. Mesaj alanında **Entegrasyonlar**'a tıklayın ve **Görüntü**'yü AÇIK konuma getirin.
4. Şu gibi bir istem kullanın: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Bir görüntü üretilir ve sohbette görünür.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Bu, Open WebUI'nin "iki aşamalı" bir iş akışını koordine edebildiğini ortaya koyar:
  - LLM istemi iyileştirmeye yardımcı olur
  - Görüntü, Stable Diffusion kullanılarak Lemonade'in Images uç noktası aracılığıyla üretilir
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Etkinlik 3: Metin İsteminden Görüntü Üretme (Stable Diffusion)

Stable Diffusion modelleri metin üretimini desteklemez; yalnızca Images API aracılığıyla görüntü üretir.

#### Adım 1: Open WebUI'de Görüntü Üretimini Yapılandırma

1. Lemonade GUI'de (`http://localhost:13305`), `SDXL-Turbo` (hızlı) veya `SDXL-Base-1.0` (daha yüksek kalite) arayın ve indirin.
2. **Yönetici Ayarları → Görüntüler** bölümüne gidin (http://localhost:8080/admin/settings/images)
3. Şunları ayarlayın:
   - **Görüntü Üretimi:** AÇIK
   - **Görüntü Üretim Motoru:** Varsayılan (OpenAI)
   - **OpenAI API Temel URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Anahtarı:** `-`
   - **Model:** `SDXL-Turbo` veya `SDXL-Base-1.0`
4. Daha fazla parametre eklemek istiyorsanız bunları metin alanına JSON olarak ekleyin. Örneğin: `{ "steps": 4, "cfg_scale": 1 }`. Mevcut parametreleri [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html) adresinde görebilirsiniz.

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Kaydedin


#### Adım 2: Model için Görüntü Üretimine İzin Verme
Bu adım, modeliniz için Görüntü Üretimini bir yetenek olarak etkinleştirmenizi sağlar.
1. **Yönetici Ayarları → Modeller** bölümüne gidin (http://localhost:8080/admin/settings/models) ve modelinizi seçin
2. `Image Generation` seçeneğini açın

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Adım 3: Sohbet ekranından görüntü üretme

1. `http://localhost:8080` adresindeki sohbete geri dönün.
2. Model açılır menüsünden bir **Metin Üretimi LLM'i** seçin (örnek: Qwen, Llama). Bu bir sohbet modeli seçicisi olduğundan **Stable Diffusion modeli seçmeyin**.
3. Mesaj alanında **Entegrasyonlar**'a tıklayın ve **Görüntü**'yü AÇIK konuma getirin.
4. Şu gibi bir istem kullanın: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Bir görüntü üretilir ve sohbette görünür.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Bu, Open WebUI'nin "iki aşamalı" bir iş akışını koordine edebildiğini ortaya koyar:
  - LLM istemi iyileştirmeye yardımcı olur
  - Görüntü, Stable Diffusion kullanılarak Lemonade'in Images uç noktası aracılığıyla üretilir
<!-- @device:end -->
<!-- @os:end -->

---

## Sorun Giderme

### "Open WebUI'de hiç model görünmüyor"
- Önce Lemonade'i kontrol edin: tarayıcınızda `http://localhost:13305/api/v1/models` adresini açın ve modellerinizin listelenip indirildiğini doğrulayın
- Ardından Open WebUI bağlantısını kontrol edin: `http://localhost:8080/admin/settings/connections` adresindeki **Yönetici Ayarları → Bağlantılar** bölümüne gidin ve Temel URL'nin `http://localhost:13305/api/v1` olduğunu doğrulayın

### "Bu model sohbet tamamlamayı desteklemiyor" hata mesajı
- Sohbet modeli açılır menüsünde bir görüntü modeli (SDXL-Turbo / SDXL-Base-1.0) seçtiniz.
- **Düzeltme**: Sohbet için bir LLM seçin ve üretim için Görüntü geçişini ile Görüntüler ayarlarını kullanın.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Görüntü üretimi hataları/zaman aşımları
- Önce `SDXL-Turbo` ile başlayın (hızlı, daha az adım)
- Çalışmaya başladıktan sonra kalite için görüntü modelini `SDXL-Base-1.0` olarak değiştirin

---

## Sonraki Adımlar

Artık çalışan bir **'yerel yapay zeka yığını'**na sahipsiniz; standart bir API aracılığıyla birden fazla model türünü kontrol eden tek bir UI.

Tamamen yeni iş akışlarının kilidini açan üç genişleme seçeneği:

### 1. Whisper ile Konuşmadan Metne