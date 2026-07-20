<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHubがレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには最低 **32GB** のシステムメモリが必要です。
<!-- @device:end -->

## 概要

[Open WebUI](https://docs.openwebui.com) は、セルフホスト型のブラウザベースインターフェースであり、おなじみのチャットボット体験を提供しながら、1つまたは複数のAIモデルサーバーのフロントエンドとして機能します。特定のプロバイダーに縛られるのではなく、Open WebUIは**OpenAI互換APIを公開する任意のバックエンド**に接続できるため、UIを切り替えることなくモデルや機能を入れ替えることができます。

このプレイブックでは、バックエンドとして[**Lemonade**](https://lemonade-server.ai)を使用します。これは、複数のモダリティをサポートする**統一されたOpenAI互換エンドポイント**を公開するためです。
- テキスト生成のための**大規模言語モデル（LLM）**
- 画像理解のための**ビジョンモデル**
- 画像生成のための**Stable Diffusion**
- 音声認識のための**音声書き起こしモデル**

このセットアップにより、**完全なマルチモーダルワークフローをエンドツーエンドで**探索できます。

---

## このプレイブックで学べること

このプレイブックを終える頃には、以下ができるようになります。

- Open WebUIをローカルのOpenAI互換バックエンド（Lemonade）に接続する
- ブラウザからローカルLLMとチャットする
- 画像をアップロードし、ビジョンモデルに画像について質問する
- Stable Diffusionモデル（SDXL-Turbo / SDXL）を使用してテキストプロンプトから画像を生成する
- 他のバックエンド（Ollama、vLLM、llama.cpp serverなど）を使用できるよう、メンタルモデルを理解する

---

## 基本概念（メンタルモデル）

### 3つのコンポーネント

| 要素 | 役割 | 例 |
|---|---|---|
| フロントエンド（UI） | ユーザーが操作するWebアプリ | Open WebUI |
| バックエンド（モデルサーバー） | モデルをホストし、HTTPエンドポイントを公開する | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI互換サーバー |
| モデル | 実際のLLM／ビジョン／拡散／音声モデル | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### 「OpenAI互換API」が重要な理由

Open WebUIは、以下のような標準的なOpenAIスタイルのエンドポイントを中心に構築されています。
  - チャット: `/chat/completions`
  - モデル一覧: `/models`
  - 画像生成: `/images/generations`
  - 音声書き起こし: `/audio/transcriptions`

Lemonadeはこれらを`http://localhost:13305/api/v1/...`の下で公開しています。

バックエンドがこれらのエンドポイントをサポートしていれば、Open WebUIは最小限のセットアップでそのバックエンドと通信できます。そのため、ワークフローを変更することなくバックエンドを切り替えることができます。

#### 2つのサービス、2つのポート

このプレイブック全体を通して、2つの別々のサービスを扱います。

| サービス | URL | そこで行うこと |
|---|---|---|
| **Lemonade**（GUI） | `http://localhost:13305` | モデルの閲覧、ダウンロード、管理 |
| **Open WebUI** | `http://localhost:8080` | チャット、画像のアップロード、画像生成 — ユーザー向けのUI |

Lemonadeはモデルを実行し、Open WebUIはユーザーが操作するインターフェースです。まずLemonade GUIを使ってモデルをダウンロードし、その後Open WebUIからそれらを使用してください。

---

## メモリ設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新確認

<!-- @require:software-update -->
<!-- @device:end -->

## 初回セットアップ

このプレイブックでは、バックエンドとしてLemonadeを実行し、Linuxの場合はOpen WebUIを実行するためのコンテナエンジン（Podman）が必要です。Open WebUIをインストールする前に、これらをセットアップしてください。

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

## Lemonadeでのモデルのダウンロード

Open WebUIをインストールする前に、使用したいモデルがLemonadeでダウンロードされ、準備が整っていることを確認してください。

1. `http://localhost:13305`でLemonade GUIを開きます。
2. 利用可能なモデルを閲覧し、使用したいものをダウンロードします（例：チャット用のLLM、ビジョンモデル、および／または画像生成用のStable Diffusionモデル）。
3. ブラウザで`http://localhost:13305/api/v1/models`にアクセスし、APIが到達可能であることを確認します — ダウンロードしたモデルが一覧表示されるはずです。

> モデルは**Open WebUI**（`localhost:8080`）に表示される前に、**Lemonade**（`localhost:13305`）でダウンロードしておく必要があります。後でモデルがOpen WebUIに表示されない場合は、ここに戻ってまずLemonadeを確認してください。


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

## Open WebUIのインストール

<!-- @os:windows -->
### 1. Python 3.12のインストール

Open WebUIには**Python 3.12**が必要です — Python 3.13以降ではインストールできません。Windows Python Launcher（`py`）を使用すると、既存のPythonバージョンと競合することなく、3.12を並行してインストールできます。

```powershell
winget install Python.Python.3.12
```

インストール後、ターミナルを閉じて再度開き、以下で確認します。

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **注:** お使いのシステムにはPython 3.13が事前にインストールされています。3.12をインストールしてもそれには影響しません — `python`は引き続き3.13を使用し、`py -3.12`は必要なときにのみ3.12を対象とします。
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

### 2. 仮想環境の作成とOpen WebUIのインストール

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
ここでは、Podmanサービスを使用してOpen WebUIのインストールをコンテナ化します。

以下のファイルを任意のディレクトリにダウンロードしてください: [compose.yml](assets/compose.yml)

そのディレクトリで、次のコマンドを実行します。

```bash
podman compose up -d
```

これによりOpen WebUIイメージがプルされ、永続ストレージに書き込まれます。

ブラウザのアドレスバーに`localhost:8080`と入力してOpen WebUIを起動します。

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

> **ヒント**: Open WebUIは、[GitHub](https://github.com/open-webui/open-webui)でも他のインストールオプションを提供しています。
## Open WebUI サーバーの起動

<!-- @os:windows -->
- 次のコマンドを実行して、Open WebUI HTTP サーバーを起動します。
```bash
open-webui serve
```
<!-- @os:end -->

- ブラウザで `http://localhost:8080` にアクセスします。
- Open WebUI からローカル管理者アカウントの作成を求められます。サインインすると、チャットインターフェースが表示されます。

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> ターミナルウィンドウは開いたままにしておいてください。閉じると Open WebUI が停止します。
<!-- @os:end -->

<!-- @os:linux -->
> コンテナはバックグラウンドで実行されます。`compose.yml` を含むディレクトリから、`podman compose down`（停止）と `podman compose up -d`（起動）で管理できます。アカウントや設定は `open_webui_data` ボリュームに保存されます。
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

## Open WebUI と Lemonade の接続

これで、Lemonade が `localhost:13305` で、Open WebUI が `localhost:8080` でそれぞれ実行されている状態になりました。これらを接続して、Open WebUI が Lemonade のモデルを使用できるようにします。

Open WebUI で以下を行います。

1. 右上の**ユーザープロフィールアイコン**をクリックし、**Settings** を選択します。

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Settings パネルで、左下の **Admin Settings** をクリックします。

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Admin Settings のサイドバーで **Connections** をクリックします（または `http://localhost:8080/admin/settings/connections` に直接アクセスします）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. **OpenAI API** の下で、新しい接続を追加します。
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-`（ローカルではダッシュ1つで機能します）

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. **「Manage OpenAI API Connections」**の下で、`http://localhost:13305/api/v1` のみが有効になっていることを確認します。他の接続（デフォルトの OpenAI 接続など）は無効にしてください。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. **Save** をクリックします。

7. **（推奨）** ローカル LLM で Open WebUI の応答性を保つため、自動生成機能を無効にします。**Admin Settings → Settings → Interface** に移動し、以下をオフにします。
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. **Save** をクリックし、`http://localhost:8080` に戻ります。
9. モデルのドロップダウンをクリックします。Lemonade からダウンロードしたモデルが表示されるはずです。

---

## 主なアクティビティ

これで準備は完了です。ここからは、試してみる価値のある3つの興味深い操作を紹介します。

---

### アクティビティ1：ローカル LLM とのチャット
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. インターフェースの左上にあるドロップダウンメニューをクリックします。インストール済みの Lemonade モデルが表示されます。使用するモデルを選択して進みます（例：`Qwen3-4B-Hybrid`）。

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. LLM にメッセージを入力し、送信をクリックします（または Enter キーを押します）。LLM がメモリに読み込まれるまで数秒かかった後、応答がストリーミングで表示されます。

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. インターフェースの左上にあるドロップダウンメニューをクリックします。インストール済みの Lemonade モデルが表示されます。使用するモデルを選択して進みます（例：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLM にメッセージを入力し、送信をクリックします（または Enter キーを押します）。LLM がメモリに読み込まれるまで数秒かかった後、応答がストリーミングで表示されます。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. モデルがチャットで応答します。

4. このとき、システムの `Task Manager` を開いてください。選択したモデルが **Hybrid** か **NPU** かに応じて、**GPU またはNPU使用率が高くなる**のが確認できます。タスクマネージャーを使用することで、モデルがローカルで実行されていることを確認できます。

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. インターフェースの左上にあるドロップダウンメニューをクリックします。インストール済みの Lemonade モデルが表示されます。使用するモデルを選択して進みます（例：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLM にメッセージを入力し、送信をクリックします（または Enter キーを押します）。LLM がメモリに読み込まれるまで数秒かかった後、応答がストリーミングで表示されます。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. モデルがチャットで応答します。
<!-- @os:end -->

これにより、Open WebUI が OpenAI 互換のチャットエンドポイントを使用して Lemonade にリクエストを送信できることが確認できます。

---

### アクティビティ2：画像をアップロードして質問する（Vision）

これには、画像入力に対応したモデル（Vision または Multimodal モデル）が必要です。

1. フィルターアイコンをクリックし、「By Category」を選択して、**Vision** セクションからモデルを選びます（例：`Qwen3.5-4B-GGUF`）

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. メッセージボックスの **`+`** ボタンをクリックし、画像をアップロードします
3. 実際に画像の理解が必要になるような質問をしてみます：`Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. モデルは画像の内容に基づいて回答します。汎用的なテキストではありません。

これにより、Open WebUI がバックエンド（Lemonade）を経由して、Vision モデルにマルチモーダルなリクエスト（テキスト + 画像）を送信できることが確認できます。

---

<!-- @os:windows -->
### アクティビティ3：テキストプロンプトから画像を生成する（Stable Diffusion）

Stable Diffusion モデルはテキスト生成には対応しておらず、Images API を通じて画像のみを生成します。

#### ステップ1：Open WebUI で画像生成を設定する

1. Lemonade の GUI（`http://localhost:13305`）で `SDXL-Turbo`（高速）または `SDXL-Base-1.0`（高品質）を検索し、ダウンロードします。
2. **Admin Settings → Images**（http://localhost:8080/admin/settings/images）に移動します
3. 以下を設定します。
   - **Image Generation:** ON
   - **Image Generation Engine:** Default（OpenAI）
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` または `SDXL-Base-1.0`
4. パラメーターを追加したい場合は、テキストフィールドに JSON として追加します。例：`{ "steps": 4, "cfg_scale": 1 }`。使用可能なパラメーターについては、[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html) を参照してください。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存します
#### ステップ2: モデルの画像生成を許可する
この手順により、モデルの機能として画像生成が有効になります。
1. **管理者設定 → モデル** (http://localhost:8080/admin/settings/models) に移動し、モデルを選択します
2. `Image Generation` をオンにします

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### ステップ3: チャット画面から画像を生成する

1. `http://localhost:8080` のチャットに戻ります。
2. モデルのドロップダウンで**テキスト生成LLM**（例: Qwen、Llama）を選択します。これはチャットモデルセレクターであるため、**Stable Diffusionモデルは選択しないでください**。
3. メッセージ入力エリアで**Integrations**をクリックし、**Image**をONに切り替えます。
4. `A cinematic photo of heavy traffic at sunset, ultra detailed` のようなプロンプトを使用します。
5. 画像が生成され、チャットに表示されます。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

これにより、Open WebUIが「二部構成」のワークフローを調整できることが実証されます。
  - LLMがプロンプトの改善を支援する
  - Stable Diffusionを使用してLemonadeのImagesエンドポイント経由で画像が生成される
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### アクティビティ3: テキストプロンプトから画像を生成する（Stable Diffusion）

Stable Diffusionモデルはテキスト生成をサポートしておらず、Images API経由で画像のみを生成します。

#### ステップ1: Open WebUIで画像生成を設定する

1. Lemonade GUI (`http://localhost:13305`) で、`SDXL-Turbo`（高速）または`SDXL-Base-1.0`（高品質）を検索し、ダウンロードします。
2. **管理者設定 → 画像** (http://localhost:8080/admin/settings/images) に移動します
3. 以下を設定します:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` または `SDXL-Base-1.0`
4. パラメータをさらに追加したい場合は、JSONとしてテキストフィールドに追加します。例: `{ "steps": 4, "cfg_scale": 1 }`。使用可能なパラメータについては[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)を参照してください。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存する


#### ステップ2: モデルの画像生成を許可する
この手順により、モデルの機能として画像生成が有効になります。
1. **管理者設定 → モデル** (http://localhost:8080/admin/settings/models) に移動し、モデルを選択します
2. `Image Generation` をオンにします

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### ステップ3: チャット画面から画像を生成する

1. `http://localhost:8080` のチャットに戻ります。
2. モデルのドロップダウンで**テキスト生成LLM**（例: Qwen、Llama）を選択します。これはチャットモデルセレクターであるため、**Stable Diffusionモデルは選択しないでください**。
3. メッセージ入力エリアで**Integrations**をクリックし、**Image**をONに切り替えます。
4. `A cinematic photo of heavy traffic at sunset, ultra detailed` のようなプロンプトを使用します。
5. 画像が生成され、チャットに表示されます。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

これにより、Open WebUIが「二部構成」のワークフローを調整できることが実証されます。
  - LLMがプロンプトの改善を支援する
  - Stable Diffusionを使用してLemonadeのImagesエンドポイント経由で画像が生成される
<!-- @device:end -->
<!-- @os:end -->

---

## トラブルシューティング

### 「Open WebUIにモデルが表示されない」
- まず、Lemonadeを確認します。ブラウザで`http://localhost:13305/api/v1/models`を開き、モデルがリストされていてダウンロード済みであることを確認します
- 次に、Open WebUIの接続を確認します。`http://localhost:8080/admin/settings/connections`の**管理者設定 → 接続**に移動し、Base URLが`http://localhost:13305/api/v1`になっていることを確認します

### 「This model does not support chat completion」というエラーメッセージ
- チャットモデルのドロップダウンで画像モデル（SDXL-Turbo / SDXL-Base-1.0）を選択しています。
- **修正方法**: チャット用にLLMを選択し、生成にはImageトグル＋Images設定を使用してください。
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### 画像生成エラー/タイムアウト
- まずは`SDXL-Turbo`（高速で少ないステップ数）から始めてください
- 動作を確認できたら、画質向上のために画像モデルを`SDXL-Base-1.0`に切り替えてください

---

## 次のステップ

これで、標準APIを通じて複数のモデルタイプを制御する単一のUIである、動作する「ローカルAIスタック」が完成しました。

まったく新しいワークフローを実現する3つの拡張機能を紹介します。

### 1. Whisperによる音声からテキストへの変換

Whisperモデルを使用して音声をテキストに変換し、それをLLMに入力して要約、アクションアイテムの抽出、書き直しを行ってみてください。これは、会議メモや音声駆動アシスタントの基盤となります。

### 2. Open WebUI内でのPythonコーディング

Open WebUIに組み込まれたコード実行機能を使用して、UIを離れることなくPythonのスニペットを実行し、出力を確認し、より速く反復作業を行うことができます。[参照](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Open WebUI内でのHTMLレンダリング

インターフェース内で直接HTM出力をレンダリングします。これは、簡易プロトタイプ、フォーマット済みレポート、インタラクティブなスニペットを構築する際に驚くほど強力です。[参照](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## 参考資料

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Serverドキュメント](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI統合ガイド](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API仕様（エンドポイント）](https://lemonade-server.ai/docs/server/server_spec)
- [動画解説（Lemonade）](https://www.youtube.com/watch?v=mcf7dDybUco)
- [動画解説（Open WebUI + Lemonade）](https://www.youtube.com/watch?v=yZs-Yzl736E)