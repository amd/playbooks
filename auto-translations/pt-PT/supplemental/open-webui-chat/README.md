<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este manual de instruções requer, no mínimo, **32 GB** de memória do sistema.
<!-- @device:end -->

## Visão Geral

O [Open WebUI](https://docs.openwebui.com) é uma interface auto-hospedada, baseada em navegador, que proporciona uma experiência de chatbot familiar, funcionando como frontend para um ou mais servidores de modelos de IA. Em vez de estar limitado a um único fornecedor, o Open WebUI pode ligar-se a **qualquer backend que exponha uma API compatível com OpenAI**, permitindo trocar modelos e capacidades sem mudar de interface.

Neste manual de instruções, utilizamos o [**Lemonade**](https://lemonade-server.ai) como backend, pois este expõe um **endpoint unificado compatível com OpenAI**, com suporte para várias modalidades:
- **Modelos de Linguagem de Grande Escala (LLMs)** para geração de texto
- **Modelos de visão** para compreensão de imagens
- **Stable Diffusion** para geração de imagens
- **Modelos de transcrição de áudio** para conversão de fala em texto

Esta configuração permite explorar o **fluxo de trabalho multimodal completo, de ponta a ponta**.

---

## O Que Vai Aprender

No final, será capaz de:

- Ligar o Open WebUI a um backend local compatível com OpenAI (Lemonade)
- Conversar com um LLM local a partir do seu navegador
- Carregar uma imagem e fazer perguntas a um modelo de visão sobre a mesma
- Gerar imagens a partir de comandos de texto utilizando modelos Stable Diffusion (SDXL-Turbo / SDXL)
- Compreender o modelo mental para poder utilizar outros backends (Ollama, vLLM, servidor llama.cpp, etc.)

---

## Conceitos Fundamentais (Modelo Mental)

### Os Três Componentes

| Componente | O que faz | Exemplos |
|---|---|---|
| Frontend (UI) | A aplicação web com a qual interage | Open WebUI |
| Backend (Servidor de Modelos) | Aloja modelos e expõe endpoints HTTP | Lemonade, Ollama, vLLM, servidor llama.cpp, servidores compatíveis com OpenAI |
| Modelos | Os modelos reais de LLM / Visão / Difusão / Áudio | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Por que motivo a "API compatível com OpenAI" é importante

O Open WebUI foi concebido em torno de endpoints padrão no estilo OpenAI, tais como:
  - Chat: `/chat/completions`
  - Lista de modelos: `/models`
  - Geração de imagens: `/images/generations`
  - Transcrição de áudio: `/audio/transcriptions`

O Lemonade expõe estes endpoints em `http://localhost:13305/api/v1/...`

Se um backend suportar estes endpoints, o Open WebUI consegue comunicar com o mesmo com uma configuração mínima. É por isso que podemos trocar de backend sem alterar o nosso fluxo de trabalho.

#### Dois serviços, duas portas

Ao longo deste manual de instruções, irá trabalhar com dois serviços distintos:

| Serviço | URL | O que faz aqui |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Explorar, descarregar e gerir modelos |
| **Open WebUI** | `http://localhost:8080` | Conversar, carregar imagens, gerar imagens — a interface voltada para o utilizador |

O Lemonade executa os modelos; o Open WebUI é a interface com a qual interage. Utilize a GUI do Lemonade para descarregar primeiro os seus modelos e, depois, utilize-os a partir do Open WebUI.

---

## Configurar a Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Configuração Única

Este manual de instruções necessita que o Lemonade esteja em execução como backend e, no Linux, de um motor de contentores (Podman) para executar o Open WebUI. Configure estes elementos antes de instalar o Open WebUI.

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

## Descarregar Modelos no Lemonade

Antes de instalar o Open WebUI, certifique-se de que os modelos que pretende utilizar estão descarregados e prontos no Lemonade.

1. Abra a GUI do Lemonade em `http://localhost:13305`.
2. Explore os modelos disponíveis e descarregue os que pretende utilizar (por exemplo, um LLM para chat, um modelo de visão e/ou um modelo Stable Diffusion para geração de imagens).
3. Confirme que a API está acessível visitando `http://localhost:13305/api/v1/models` no seu navegador — deverá ver os modelos descarregados listados.

> Os modelos têm de ser descarregados no **Lemonade** (`localhost:13305`) antes de poderem aparecer no **Open WebUI** (`localhost:8080`). Se um modelo não aparecer mais tarde no Open WebUI, volte aqui e verifique primeiro no Lemonade.


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

## Instalar o Open WebUI

<!-- @os:windows -->
### 1. Instalar o Python 3.12

O Open WebUI requer **Python 3.12** — não é instalado no Python 3.13+. O Iniciador do Python do Windows (`py`) permite instalar o 3.12 lado a lado com qualquer versão existente do Python, sem conflitos.

```powershell
winget install Python.Python.3.12
```

Feche e reabra o seu terminal após a instalação e, depois, verifique:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Nota:** O seu sistema vem com o Python 3.13 pré-instalado. A instalação do 3.12 não o afeta — o `python` continua a utilizar o 3.13, e o `py -3.12` visa apenas o 3.12 quando necessário.
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

### 2. Criar um ambiente virtual e instalar o Open WebUI

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
Vamos agora utilizar o serviço Podman para colocar em contentor a nossa instalação do Open WebUI.

Descarregue o seguinte ficheiro para um diretório à sua escolha: [compose.yml](assets/compose.yml)

Nesse diretório, execute o seguinte comando:

```bash
podman compose up -d
```

Isto obtém a imagem do Open WebUI e grava-a em armazenamento persistente.

Inicie o Open WebUI digitando `localhost:8080` na barra de endereço do seu navegador.

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

> **Dica**: O Open WebUI oferece também outras opções de instalação no seu [GitHub](https://github.com/open-webui/open-webui).
## Iniciar o servidor Open WebUI

<!-- @os:windows -->
- Execute o seguinte comando para iniciar o servidor HTTP do Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- Num browser, navegue até `http://localhost:8080`.
- O Open WebUI irá pedir-lhe para criar uma conta de administrador local. Assim que tiver sessão iniciada, verá a interface de chat.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Mantenha a janela do terminal aberta. Se a fechar, o Open WebUI para de funcionar.
<!-- @os:end -->

<!-- @os:linux -->
> O contentor é executado em segundo plano. A partir do diretório que contém `compose.yml`, faça a gestão com `podman compose down` (parar) e `podman compose up -d` (iniciar). As suas contas e definições são mantidas no volume `open_webui_data`.
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

## Ligar o Open WebUI ao Lemonade

Agora que ambos os serviços estão em execução — o Lemonade em `localhost:13305` e o Open WebUI em `localhost:8080` — ligue-os para que o Open WebUI possa utilizar os modelos do Lemonade.

No Open WebUI:

1. Clique no **ícone de perfil de utilizador** no canto superior direito e, em seguida, selecione **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. No painel Settings, clique em **Admin Settings** no canto inferior esquerdo.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Na barra lateral de Admin Settings, clique em **Connections** (ou navegue diretamente para `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Em **OpenAI API**, adicione uma nova ligação:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (um único traço funciona para uso local)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Certifique-se de que, em **"Manage OpenAI API Connections"**, apenas `http://localhost:13305/api/v1` está ativado. Desative quaisquer outras ligações (por exemplo, a ligação predefinida da OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Clique em **Save**.

7. **(Recomendado)** Desative as funcionalidades de geração automática para manter o Open WebUI responsivo com LLMs locais. Vá a **Admin Settings → Settings → Interface** e desative:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Clique em **Save** e, em seguida, volte a `http://localhost:8080`.
9. Clique na lista pendente de modelos — deverá ver os modelos que descarregou a partir do Lemonade.

---

## Atividades principais

Agora está tudo configurado. Vejamos três atividades interessantes para fazer.

---

### Atividade 1: Conversar com um LLM local
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Clique no menu pendente no canto superior esquerdo da interface. Isto irá mostrar os modelos do Lemonade que tem instalados. Selecione um para continuar (exemplo: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Introduza uma mensagem para o LLM e clique em enviar (ou prima Enter). O LLM demorará alguns segundos a carregar para a memória e, em seguida, verá a resposta a ser transmitida.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Clique no menu pendente no canto superior esquerdo da interface. Isto irá mostrar os modelos do Lemonade que tem instalados. Selecione um para continuar (exemplo: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Introduza uma mensagem para o LLM e clique em enviar (ou prima Enter). O LLM demorará alguns segundos a carregar para a memória e, em seguida, verá a resposta a ser transmitida.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. O modelo irá responder no chat.

4. Nesta altura, abra o `Task Manager` no seu sistema. Verá uma **utilização elevada de GPU ou NPU**, consoante o modelo selecionado seja **Hybrid** ou **NPU**, respetivamente. Utilizando o Gestor de Tarefas, pode confirmar que está a executar o modelo localmente.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Clique no menu pendente no canto superior esquerdo da interface. Isto irá mostrar os modelos do Lemonade que tem instalados. Selecione um para continuar (exemplo: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Introduza uma mensagem para o LLM e clique em enviar (ou prima Enter). O LLM demorará alguns segundos a carregar para a memória e, em seguida, verá a resposta a ser transmitida.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. O modelo irá responder no chat.
<!-- @os:end -->

Isto valida que o Open WebUI consegue enviar pedidos ao Lemonade utilizando o endpoint de chat compatível com OpenAI.

---

### Atividade 2: Carregar uma imagem e fazer perguntas (Visão)

Isto requer um modelo que suporte entrada de imagem (um modelo Vision ou Multimodal).

1. Clique no ícone de filtro, selecione "By Category" e, em seguida, escolha um modelo da secção **Vision** (por exemplo, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Clique no botão **`+`** na caixa de mensagem e carregue uma imagem
3. Faça uma pergunta que exija uma verdadeira compreensão da imagem: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. O modelo responde com base no conteúdo da imagem, e não com texto genérico.

Isto demonstra que o Open WebUI consegue enviar pedidos multimodais (texto + imagem) através do backend (Lemonade) para um modelo de visão.

---

<!-- @os:windows -->
### Atividade 3: Gerar uma imagem a partir de um comando de texto (Stable Diffusion)

Os modelos Stable Diffusion não suportam geração de texto, apenas geram imagens através da Images API. 

#### Passo 1: Configurar a geração de imagens no Open WebUI

1. Na GUI do Lemonade (`http://localhost:13305`), procure por `SDXL-Turbo` (rápido) ou `SDXL-Base-1.0` (maior qualidade) e descarregue-o.
2. Vá a **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Defina:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ou `SDXL-Base-1.0`
4. Se quiser adicionar mais parâmetros, adicione-os ao campo de texto em formato JSON. Por exemplo: `{ "steps": 4, "cfg_scale": 1 }`. Consulte os parâmetros disponíveis em [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Guarde
#### Passo 2: Ativar a Geração de Imagens para o modelo
Este passo garante que ativa a Geração de Imagens como uma funcionalidade do seu modelo.
1. Vá a **Admin Settings → Models** (http://localhost:8080/admin/settings/models) e escolha o seu modelo
2. Ative `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Passo 3: Gerar uma imagem a partir do ecrã de chat

1. Volte ao chat em `http://localhost:8080`.
2. Selecione um **Text Generation LLM** na lista pendente de modelos (exemplo: Qwen, Llama). **Não selecione um modelo Stable Diffusion**, pois este é um seletor de modelo de chat.
3. Na área de mensagem, clique em **Integrations** e ative a opção **Image**.
4. Utilize um prompt como: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. É gerada uma imagem que aparece no chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Isto estabelece que o Open WebUI consegue coordenar um fluxo de trabalho em "duas partes":
  - O LLM ajuda a refinar o prompt
  - A imagem é gerada através do endpoint Images do Lemonade, usando Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Atividade 3: Gerar uma Imagem a partir de um Prompt de Texto (Stable Diffusion)

Os modelos Stable Diffusion não suportam geração de texto, apenas geram imagens através da API de Images.

#### Passo 1: Configurar a Geração de Imagens no Open WebUI

1. Na GUI do Lemonade (`http://localhost:13305`), procure por `SDXL-Turbo` (rápido) ou `SDXL-Base-1.0` (maior qualidade) e faça o download.
2. Vá a **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Defina:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ou `SDXL-Base-1.0`
4. Se quiser adicionar mais parâmetros, adicione-os ao campo de texto em formato JSON. Por exemplo: `{ "steps": 4, "cfg_scale": 1 }`. Consulte os parâmetros disponíveis em [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Guardar


#### Passo 2: Ativar a Geração de Imagens para o modelo
Este passo garante que ativa a Geração de Imagens como uma funcionalidade do seu modelo.
1. Vá a **Admin Settings → Models** (http://localhost:8080/admin/settings/models) e escolha o seu modelo
2. Ative `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Passo 3: Gerar uma imagem a partir do ecrã de chat

1. Volte ao chat em `http://localhost:8080`.
2. Selecione um **Text Generation LLM** na lista pendente de modelos (exemplo: Qwen, Llama). **Não selecione um modelo Stable Diffusion**, pois este é um seletor de modelo de chat.
3. Na área de mensagem, clique em **Integrations** e ative a opção **Image**.
4. Utilize um prompt como: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. É gerada uma imagem que aparece no chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Isto estabelece que o Open WebUI consegue coordenar um fluxo de trabalho em "duas partes":
  - O LLM ajuda a refinar o prompt
  - A imagem é gerada através do endpoint Images do Lemonade, usando Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Resolução de Problemas

### "No models show up in Open WebUI"
- Primeiro, verifique o Lemonade: abra `http://localhost:13305/api/v1/models` num browser e confirme que os seus modelos aparecem listados e foram descarregados
- Em seguida, verifique a ligação do Open WebUI: vá a **Admin Settings → Connections** em `http://localhost:8080/admin/settings/connections` e confirme que o Base URL é `http://localhost:13305/api/v1`

### Mensagem de erro "This model does not support chat completion"
- Selecionou um modelo de imagem (SDXL-Turbo / SDXL-Base-1.0) na lista pendente de modelo de chat.
- **Correção**: selecione um LLM para chat e utilize o botão Image + as definições de Images para a geração.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Erros/tempos de espera na geração de imagens
- Comece por usar o `SDXL-Turbo` (rápido, menos passos)
- Assim que estiver a funcionar, mude o modelo de imagem para `SDXL-Base-1.0` para maior qualidade

---

## Próximos Passos

Agora tem uma **'pilha de IA local'** funcional, uma única interface a controlar múltiplos tipos de modelos através de uma API padrão.

Aqui estão três expansões que desbloqueiam fluxos de trabalho totalmente novos:

### 1. Voz-para-Texto com Whisper

Experimente converter áudio em texto utilizando um modelo Whisper e, depois, introduza-o num LLM para resumo, itens de ação ou reescrita. Esta é a base para notas de reuniões e assistentes controlados por voz.

### 2. Programação em Python dentro do Open WebUI

Utilize a experiência de execução de código integrada no Open WebUI para executar excertos de Python, inspecionar resultados e iterar mais rapidamente—sem sair da interface. [Referência](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Renderização de HTML dentro do Open WebUI

Renderize resultados HTML diretamente na interface. Isto é surpreendentemente poderoso para criar protótipos rápidos, relatórios formatados e excertos interativos. [Referência](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referências

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)
- [CLI do Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Guia de integração Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Especificação da API do Lemonade Server (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Vídeo demonstrativo (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Vídeo demonstrativo (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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