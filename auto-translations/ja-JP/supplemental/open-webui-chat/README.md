<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには最低 **32GB** のシステムメモリが必要です。
<!-- @device:end -->

## 概要

[Open WebUI](https://docs.openwebui.com) は、セルフホスト型のブラウザベースインターフェースで、使い慣れたチャットボット体験を提供しながら、1つまたは複数のAIモデルサーバーのフロントエンドとして機能します。特定のプロバイダーに縛られることなく、Open WebUI は **OpenAI互換APIを公開するあらゆるバックエンド** に接続できるため、UIを切り替えることなくモデルや機能を入れ替えることができます。

このプレイブックでは、バックエンドとして [**Lemonade**](https://lemonade-server.ai) を使用します。これは複数のモダリティをサポートする **統一されたOpenAI互換エンドポイント** を公開しているためです。
- テキスト生成のための **大規模言語モデル (LLM)**
- 画像理解のための **ビジョンモデル**
- 画像生成のための **Stable Diffusion**
- 音声認識のための **音声書き起こしモデル**

この構成により、**完全なマルチモーダルワークフローをエンドツーエンド** で体験できます。

---

## このプレイブックで学べること

本プレイブックの終了時には、以下ができるようになります：

- Open WebUI をローカルの OpenAI互換バックエンド (Lemonade) に接続する
- ブラウザからローカル LLM とチャットする
- 画像をアップロードし、ビジョンモデルにその内容について質問する
- Stable Diffusion モデル (SDXL-Turbo / SDXL) を使用してテキストプロンプトから画像を生成する
- 他のバックエンド (Ollama、vLLM、llama.cpp server など) にも応用できるよう、全体像を理解する

---

## 基本コンセプト（概念モデル）

### 3つの構成要素

| 要素 | 役割 | 例 |
|---|---|---|
| フロントエンド (UI) | ユーザーが操作するWebアプリ | Open WebUI |
| バックエンド (モデルサーバー) | モデルをホストし、HTTPエンドポイントを公開 | Lemonade、Ollama、vLLM、llama.cpp server、OpenAI互換サーバー |
| モデル | 実際の LLM / ビジョン / 拡散 / 音声モデル | CodeLlama、DeepSeek、Gemma-MM、SDXL、SD-Turbo、Whisper |

#### 「OpenAI互換API」が重要な理由

Open WebUI は、以下のような標準的な OpenAI スタイルのエンドポイントを前提に構築されています：
  - チャット: `/chat/completions`
  - モデル一覧: `/models`
  - 画像生成: `/images/generations`
  - 音声書き起こし: `/audio/transcriptions`

Lemonade はこれらを `http://localhost:13305/api/v1/...` の下で公開しています。

バックエンドがこれらのエンドポイントをサポートしていれば、Open WebUI は最小限の設定でそのバックエンドと通信できます。そのため、ワークフローを変更することなくバックエンドを切り替えることができます。

#### 2つのサービス、2つのポート

このプレイブックを通して、2つの別々のサービスを扱うことになります：

| サービス | URL | そこで行うこと |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | モデルの閲覧、ダウンロード、管理 |
| **Open WebUI** | `http://localhost:8080` | チャット、画像のアップロード、画像生成 — ユーザー向けUI |

Lemonade はモデルを実行し、Open WebUI はあなたが操作するインターフェースです。まず Lemonade GUI を使ってモデルをダウンロードし、その後 Open WebUI からそれらを使用してください。

---

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## 初回セットアップ

このプレイブックでは、バックエンドとして Lemonade を実行し、Linux の場合は Open WebUI を実行するためのコンテナエンジン (Podman) が必要です。Open WebUI をインストールする前に、これらをセットアップしてください。

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

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:lemonade-models-qwen3-4b,lemonade-models-sdxl-turbo -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## Lemonade でのモデルのダウンロード

Open WebUI をインストールする前に、使用したいモデルが Lemonade でダウンロード済みであり、利用可能な状態になっていることを確認してください。

1. `http://localhost:13305` で Lemonade GUI を開きます。
2. 利用可能なモデルを閲覧し、使用したいものをダウンロードします（例：チャット用のLLM、ビジョンモデル、画像生成用の Stable Diffusion モデルなど）。
3. ブラウザで `http://localhost:13305/api/v1/models` にアクセスして API に到達可能であることを確認してください — ダウンロードしたモデルが一覧表示されるはずです。

> モデルは **Open WebUI** (`localhost:8080`) に表示される前に **Lemonade** (`localhost:13305`) でダウンロードしておく必要があります。後で Open WebUI にモデルが表示されない場合は、まずここに戻って Lemonade を確認してください。


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

## Open WebUI のインストール

<!-- @os:windows -->
### 1. Python 3.12 のインストール

Open WebUI には **Python 3.12** が必要です — Python 3.13以降ではインストールできません。Windows の Python ランチャー (`py`) を使用すると、既存の Python バージョンと競合することなく 3.12 を併用してインストールできます。

```powershell
winget install Python.Python.3.12
```

インストール後、ターミナルを閉じて再度開き、以下で確認してください：

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **注:** お使いのシステムには Python 3.13 があらかじめインストールされています。3.12 をインストールしてもこれには影響しません — `python` は引き続き 3.13 を使用し、`py -3.12` は必要なときにのみ 3.12 を対象とします。
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

### 2. 仮想環境の作成と Open WebUI のインストール

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
ここからは Podman サービスを使用して Open WebUI のインストールをコンテナ化します。

以下を任意のディレクトリにダウンロードしてください: [compose.yml](assets/compose.yml)

そのディレクトリで、以下のコマンドを実行します：

```bash
podman compose up -d
```

これにより Open WebUI イメージがプルされ、永続ストレージに書き込まれます。

ブラウザのアドレスバーに `localhost:8080` と入力して Open WebUI を起動してください。

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

> **ヒント**: Open WebUI は他のインストール方法も [GitHub](https://github.com/open-webui/open-webui) で提供しています。
## Open WebUIサーバーの起動

<!-- @os:windows -->
- 次のコマンドを実行して、Open WebUI HTTPサーバーを起動します:
```bash
open-webui serve
```
<!-- @os:end -->

- ブラウザで `http://localhost:8080` にアクセスします。
- Open WebUIはローカル管理者アカウントの作成を求めます。サインインが完了すると、チャットインターフェースが表示されます。

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> ターミナルウィンドウは開いたままにしておいてください。閉じるとOpen WebUIが停止します。
<!-- @os:end -->

<!-- @os:linux -->
> コンテナはバックグラウンドで実行されます。`compose.yml` を含むディレクトリから、`podman compose down`（停止）と `podman compose up -d`（起動）で管理できます。アカウントや設定は `open_webui_data` ボリュームに保持されます。
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

## Open WebUIとLemonadeの接続

Lemonadeが `localhost:13305` で、Open WebUIが `localhost:8080` でそれぞれ稼働している状態になったので、両者を接続してOpen WebUIがLemonadeのモデルを利用できるようにします。

Open WebUIで次の操作を行います：

1. 右上の**ユーザープロフィールアイコン**をクリックし、**Settings** を選択します。

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Settingsパネルで、左下の **Admin Settings** をクリックします。

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Admin Settingsのサイドバーで **Connections** をクリックします（または `http://localhost:8080/admin/settings/connections` に直接アクセスします）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. **OpenAI API** の下で、新しい接続を追加します:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-`（ローカル利用の場合はダッシュ1つでOKです）

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. **"Manage OpenAI API Connections"** の下で、`http://localhost:13305/api/v1` のみが有効になっていることを確認します。それ以外の接続（デフォルトのOpenAIなど）は無効にしてください。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. **Save** をクリックします。

7. **（推奨）** ローカルLLMでOpen WebUIの応答性を維持するために、自動生成機能を無効にします。**Admin Settings → Settings → Interface** に移動し、次の項目をオフにします:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. **Save** をクリックし、`http://localhost:8080` に戻ります。
9. モデルのドロップダウンをクリックします — Lemonadeからダウンロードしたモデルが表示されているはずです。

---

## 主な作業内容

これで準備が整いました。ここでは試してみたい3つの興味深い項目を紹介します。

---

### 作業1: ローカルLLMとのチャット
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. インターフェース左上のドロップダウンメニューをクリックします。インストール済みのLemonadeモデルが表示されるので、いずれかを選択します（例: `Qwen3-4B-Hybrid`）。

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. LLMにメッセージを入力し、送信をクリックします（またはEnterキーを押します）。LLMがメモリに読み込まれるまで数秒かかり、その後応答がストリーム表示されます。

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. インターフェース左上のドロップダウンメニューをクリックします。インストール済みのLemonadeモデルが表示されるので、いずれかを選択します（例: `Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLMにメッセージを入力し、送信をクリックします（またはEnterキーを押します）。LLMがメモリに読み込まれるまで数秒かかり、その後応答がストリーム表示されます。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. モデルがチャット上で応答します。

4. このタイミングでシステムの `Task Manager` を開いてください。選択したモデルが**Hybrid**か**NPU**かに応じて、**高いGPUまたはNPU使用率**が確認できます。タスクマネージャーを使えば、モデルがローカルで実行されていることを確認できます。

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. インターフェース左上のドロップダウンメニューをクリックします。インストール済みのLemonadeモデルが表示されるので、いずれかを選択します（例: `Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLMにメッセージを入力し、送信をクリックします（またはEnterキーを押します）。LLMがメモリに読み込まれるまで数秒かかり、その後応答がストリーム表示されます。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. モデルがチャット上で応答します。
<!-- @os:end -->

これにより、Open WebUIがOpenAI互換のチャットエンドポイントを使ってLemonadeにリクエストを送信できることが確認できます。

---

### 作業2: 画像をアップロードして質問する（Vision）

これには画像入力をサポートするモデル（VisionまたはMultimodalモデル）が必要です。

1. フィルターアイコンをクリックし、「By Category」を選択してから、**Vision** セクションからモデルを選びます（例: `Qwen3.5-4B-GGUF`）

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. メッセージボックスの **`+`** ボタンをクリックして画像をアップロードします
3. 真に画像理解を必要とする質問をします: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. モデルは一般的なテキストではなく、画像の内容に基づいて回答します。

これにより、Open WebUIがバックエンド（Lemonade）を通じてマルチモーダルリクエスト（テキスト＋画像）をVisionモデルに送信できることが分かります。

---

<!-- @os:windows -->
### 作業3: テキストプロンプトから画像を生成する（Stable Diffusion）

Stable Diffusionモデルはテキスト生成をサポートせず、Images APIを通じて画像のみを生成します。

#### ステップ1: Open WebUIで画像生成を設定する

1. Lemonade GUI（`http://localhost:13305`）で `SDXL-Turbo`（高速）または `SDXL-Base-1.0`（高品質）を検索し、ダウンロードします。
2. **Admin Settings → Images**（http://localhost:8080/admin/settings/images）に移動します
3. 次のように設定します:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` または `SDXL-Base-1.0`
4. さらにパラメータを追加したい場合は、テキストフィールドにJSON形式で追加します。例: `{ "steps": 4, "cfg_scale": 1 }`。利用可能なパラメータについては[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)を参照してください。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存します
#### ステップ2: モデルで画像生成を許可する
このステップでは、モデルの機能として画像生成を有効にします。
1. **Admin Settings → Models**（http://localhost:8080/admin/settings/models）に移動し、モデルを選択します
2. `Image Generation` をオンにします

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### ステップ3: チャット画面から画像を生成する

1. `http://localhost:8080` のチャットに戻ります。
2. モデルドロップダウンで**テキスト生成LLM**（例: Qwen、Llama）を選択します。これはチャットモデルの選択肢なので、**Stable Diffusionモデルは選択しないでください**。
3. メッセージエリアで**Integrations**をクリックし、**Image**をONに切り替えます。
4. `A cinematic photo of heavy traffic at sunset, ultra detailed` のようなプロンプトを使用します。
5. 画像が生成され、チャットに表示されます。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

これにより、Open WebUIが「2部構成」のワークフローを調整できることが確認できます。
  - LLMがプロンプトの改良を支援する
  - 画像はStable Diffusionを使用したLemonadeのImagesエンドポイント経由で生成される
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### アクティビティ3: テキストプロンプトから画像を生成する（Stable Diffusion）

Stable Diffusionモデルはテキスト生成をサポートしておらず、Images APIを通じて画像のみを生成します。

#### ステップ1: Open WebUIで画像生成を設定する

1. Lemonade GUI（`http://localhost:13305`）で、`SDXL-Turbo`（高速）または`SDXL-Base-1.0`（高品質）を検索してダウンロードします。
2. **Admin Settings → Images**（http://localhost:8080/admin/settings/images）に移動します
3. 以下を設定します:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` または `SDXL-Base-1.0`
4. 他のパラメータを追加したい場合は、テキストフィールドにJSONとして追加します。例: `{ "steps": 4, "cfg_scale": 1 }`。利用可能なパラメータについては[Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)を参照してください。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存します


#### ステップ2: モデルで画像生成を許可する
このステップでは、モデルの機能として画像生成を有効にします。
1. **Admin Settings → Models**（http://localhost:8080/admin/settings/models）に移動し、モデルを選択します
2. `Image Generation` をオンにします

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### ステップ3: チャット画面から画像を生成する

1. `http://localhost:8080` のチャットに戻ります。
2. モデルドロップダウンで**テキスト生成LLM**（例: Qwen、Llama）を選択します。これはチャットモデルの選択肢なので、**Stable Diffusionモデルは選択しないでください**。
3. メッセージエリアで**Integrations**をクリックし、**Image**をONに切り替えます。
4. `A cinematic photo of heavy traffic at sunset, ultra detailed` のようなプロンプトを使用します。
5. 画像が生成され、チャットに表示されます。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

これにより、Open WebUIが「2部構成」のワークフローを調整できることが確認できます。
  - LLMがプロンプトの改良を支援する
  - 画像はStable Diffusionを使用したLemonadeのImagesエンドポイント経由で生成される
<!-- @device:end -->
<!-- @os:end -->

---

## トラブルシューティング

### 「Open WebUIにモデルが表示されない」場合
- まず、Lemonadeを確認します: ブラウザで `http://localhost:13305/api/v1/models` を開き、モデルがリストされダウンロード済みであることを確認します
- 次に、Open WebUIの接続を確認します: `http://localhost:8080/admin/settings/connections` で**Admin Settings → Connections**に移動し、Base URLが`http://localhost:13305/api/v1`になっていることを確認します

### 「This model does not support chat completion」というエラーメッセージ
- チャットモデルのドロップダウンで画像モデル（SDXL-Turbo / SDXL-Base-1.0）を選択しています。
- **修正方法**: チャット用にLLMを選択し、生成にはImageトグルとImages設定を使用してください。
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### 画像生成のエラー/タイムアウト
- まずは`SDXL-Turbo`（高速、ステップ数が少ない）から始めてください
- 動作を確認できたら、品質向上のために画像モデルを`SDXL-Base-1.0`に切り替えてください

---

## 次のステップ

これで、動作する**「ローカルAIスタック」**が手に入りました。標準APIを通じて複数のモデルタイプを制御する単一のUIです。

まったく新しいワークフローを実現する3つの拡張機能を紹介します。

### 1. Whisperによる音声からテキストへの変換

Whisperモデルを使って音声をテキストに変換し、それをLLMに渡して要約、アクションアイテムの抽出、書き換えなどを試してみてください。これは、会議の議事録や音声駆動型アシスタントの基盤となります。

### 2. Open WebUI内でのPythonコーディング

Open WebUIに組み込まれたコード実行機能を使って、UIを離れることなくPythonスニペットを実行し、出力を確認し、より速く反復作業を行いましょう。[参考資料](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Open WebUI内でのHTMLレンダリング

HTML出力をインターフェース内で直接レンダリングできます。これは、クイックプロトタイプ、書式付きレポート、インタラクティブなスニペットの作成に驚くほど強力です。[参考資料](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## 参考資料

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Serverドキュメント](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI統合ガイド](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server APIスペック（エンドポイント）](https://lemonade-server.ai/docs/server/server_spec)
- [動画解説 (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [動画解説 (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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