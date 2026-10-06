<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este guia requer no mínimo **32GB** de memória do sistema.
<!-- @device:end -->

## Visão Geral

[Open WebUI](https://docs.openwebui.com) é uma interface auto-hospedada, baseada em navegador, que oferece uma experiência familiar de chatbot ao mesmo tempo em que atua como frontend para um ou mais servidores de modelos de IA. Em vez de ficar vinculada a um único provedor, o Open WebUI pode se conectar a **qualquer backend que exponha uma API compatível com OpenAI**, permitindo trocar modelos e recursos sem mudar de interface.

Neste guia, usamos o [**Lemonade**](https://lemonade-server.ai) como backend porque ele expõe um **endpoint unificado compatível com OpenAI** com suporte a múltiplas modalidades:
- **Modelos de Linguagem de Grande Porte (LLMs)** para geração de texto
- **Modelos de visão** para compreensão de imagens
- **Stable Diffusion** para geração de imagens
- **Modelos de transcrição de áudio** para conversão de fala em texto

Essa configuração permite que você explore o **fluxo de trabalho multimodal completo, de ponta a ponta**.

---

## O Que Você Vai Aprender

Ao final, você será capaz de:

- Conectar o Open WebUI a um backend local compatível com OpenAI (Lemonade)
- Conversar com um LLM local pelo navegador
- Enviar uma imagem e fazer perguntas sobre ela usando um modelo de visão
- Gerar imagens a partir de prompts de texto usando modelos Stable Diffusion (SDXL-Turbo / SDXL)
- Entender o modelo mental para que você possa usar outros backends (Ollama, vLLM, llama.cpp server, etc.)

---

## Conceitos Fundamentais (Modelo Mental)

### Os Três Componentes

| Peça | O que faz | Exemplos |
|---|---|---|
| Frontend (UI) | O aplicativo web com o qual você interage | Open WebUI |
| Backend (Servidor de Modelos) | Hospeda modelos e expõe endpoints HTTP | Lemonade, Ollama, vLLM, llama.cpp server, servidores compatíveis com OpenAI |
| Modelos | Os LLMs / modelos de Visão / Difusão / Áudio reais | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Por que "API compatível com OpenAI" é importante

O Open WebUI foi construído em torno de endpoints padrão no estilo OpenAI, como:
  - Chat: `/chat/completions`
  - Lista de modelos: `/models`
  - Geração de imagens: `/images/generations`
  - Transcrição de áudio: `/audio/transcriptions`

O Lemonade expõe esses endpoints em `http://localhost:13305/api/v1/...`

Se um backend oferece suporte a esses endpoints, o Open WebUI pode se comunicar com ele com configuração mínima. É por isso que podemos trocar de backend sem alterar nosso fluxo de trabalho.

#### Dois serviços, duas portas

Ao longo deste guia, você trabalhará com dois serviços separados:

| Serviço | URL | O que você faz lá |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Navegar, baixar e gerenciar modelos |
| **Open WebUI** | `http://localhost:8080` | Conversar, enviar imagens, gerar imagens — a interface voltada ao usuário |

O Lemonade executa os modelos; o Open WebUI é a interface com a qual você interage. Use a GUI do Lemonade para baixar seus modelos primeiro e, depois, use-os a partir do Open WebUI.

---

<!-- @device:halo_box,halo,stx,krk -->
## Configurando a Memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Configuração Única

Este guia precisa que o Lemonade esteja em execução como backend e, no Linux, de um mecanismo de contêiner (Podman) para executar o Open WebUI. Configure esses itens antes de instalar o Open WebUI.

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

## Baixando Modelos no Lemonade

Antes de instalar o Open WebUI, certifique-se de que os modelos que você deseja usar estejam baixados e prontos no Lemonade.

1. Abra a GUI do Lemonade em `http://localhost:13305`.
2. Navegue pelos modelos disponíveis e baixe os que deseja usar (por exemplo, um LLM para chat, um modelo de visão e/ou um modelo Stable Diffusion para geração de imagens).
3. Confirme se a API está acessível visitando `http://localhost:13305/api/v1/models` no seu navegador — você deve ver os modelos baixados listados.

> Os modelos precisam ser baixados no **Lemonade** (`localhost:13305`) antes de poderem aparecer no **Open WebUI** (`localhost:8080`). Se um modelo não aparecer no Open WebUI mais tarde, volte aqui e verifique primeiro no Lemonade.


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

## Instalando o Open WebUI

<!-- @os:windows -->
### 1. Instale o Python 3.12

O Open WebUI requer **Python 3.12** — ele não é instalado em Python 3.13+. O Windows Python Launcher (`py`) permite instalar o 3.12 lado a lado com qualquer versão existente do Python sem conflitos.

```powershell
winget install Python.Python.3.12
```

Feche e reabra seu terminal após a instalação e, em seguida, verifique:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Observação:** Seu sistema vem com o Python 3.13 pré-instalado. Instalar o 3.12 não afeta isso — o `python` continua usando o 3.13, e o `py -3.12` direciona para o 3.12 apenas quando você precisar.
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

### 2. Crie um ambiente virtual e instale o Open WebUI

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
Agora vamos usar o serviço Podman para conteinerizar nossa instalação do Open WebUI.

Baixe o seguinte arquivo em um diretório à sua escolha: [compose.yml](assets/compose.yml)

Nesse diretório, execute o seguinte comando:

```bash
podman compose up -d
```

Isso baixa a imagem do Open WebUI e grava em armazenamento persistente.

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

> **Dica**: O Open WebUI também oferece outras opções de instalação em seu [GitHub](https://github.com/open-webui/open-webui).
## Iniciando o Servidor Open WebUI

<!-- @os:windows -->
- Execute o seguinte comando para iniciar o servidor HTTP do Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- Em um navegador, navegue até `http://localhost:8080`.
- O Open WebUI solicitará que você crie uma conta de administrador local. Depois de fazer login, você verá a interface de chat.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Mantenha a janela do terminal aberta. Fechá-la interrompe o Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> O contêiner é executado em segundo plano. A partir do diretório que contém `compose.yml`, gerencie-o com `podman compose down` (parar) e `podman compose up -d` (iniciar). Suas contas e configurações persistem no volume `open_webui_data`.
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

## Conectando o Open WebUI ao Lemonade

Agora que ambos os serviços estão em execução — Lemonade em `localhost:13305` e Open WebUI em `localhost:8080` — conecte-os para que o Open WebUI possa usar os modelos do Lemonade.

No Open WebUI:

1. Clique no **ícone de perfil de usuário** no canto superior direito e, em seguida, selecione **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. No painel Settings, clique em **Admin Settings** na parte inferior esquerda.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Na barra lateral do Admin Settings, clique em **Connections** (ou navegue diretamente para `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Em **OpenAI API**, adicione uma nova conexão:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (um único traço funciona para uso local)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Certifique-se de que, em **"Manage OpenAI API Connections"**, apenas `http://localhost:13305/api/v1` esteja habilitado. Desabilite quaisquer outras conexões (por exemplo, a conexão padrão da OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Clique em **Save**.

7. **(Recomendado)** Desabilite os recursos de geração automática para manter o Open WebUI responsivo com LLMs locais. Vá para **Admin Settings → Settings → Interface** e desative:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Clique em **Save** e, em seguida, retorne para `http://localhost:8080`.
9. Clique no menu suspenso de modelos — você deverá ver os modelos que baixou do Lemonade.

---

## Principais Atividades

Agora você está tudo configurado. Vamos ver três coisas interessantes para fazer.

---

### Atividade 1: Converse com um LLM Local
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Clique no menu suspenso no canto superior esquerdo da interface. Isso exibirá os modelos do Lemonade que você instalou. Selecione um para continuar (exemplo: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Digite uma mensagem para o LLM e clique em enviar (ou pressione Enter). O LLM levará alguns segundos para carregar na memória e, em seguida, você verá a resposta sendo transmitida.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Clique no menu suspenso no canto superior esquerdo da interface. Isso exibirá os modelos do Lemonade que você instalou. Selecione um para continuar (exemplo: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Digite uma mensagem para o LLM e clique em enviar (ou pressione Enter). O LLM levará alguns segundos para carregar na memória e, em seguida, você verá a resposta sendo transmitida.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. O modelo responderá no chat.

4. Neste momento, abra o `Task Manager` no seu sistema. Você verá **alta utilização de GPU ou NPU** dependendo se o modelo selecionado é **Hybrid** ou **NPU**, respectivamente. Usando o gerenciador de tarefas, você pode confirmar que está executando o modelo localmente.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Clique no menu suspenso no canto superior esquerdo da interface. Isso exibirá os modelos do Lemonade que você instalou. Selecione um para continuar (exemplo: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Digite uma mensagem para o LLM e clique em enviar (ou pressione Enter). O LLM levará alguns segundos para carregar na memória e, em seguida, você verá a resposta sendo transmitida.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. O modelo responderá no chat.
<!-- @os:end -->

Isso valida que o Open WebUI pode enviar solicitações ao Lemonade usando o endpoint de chat compatível com OpenAI.

---

### Atividade 2: Carregue uma Imagem e Faça Perguntas (Visão)

Isso requer um modelo que suporte entrada de imagem (um modelo de Visão ou Multimodal).

1. Clique no ícone de filtro, selecione "By Category" e, em seguida, escolha um modelo da seção **Vision** (por exemplo, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Clique no botão **`+`** na caixa de mensagem e carregue uma imagem
3. Pergunte algo que exija compreensão real da imagem: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. O modelo responde com base no conteúdo da imagem, não em texto genérico.

Isso demonstra que o Open WebUI pode enviar solicitações multimodais (texto + imagem) através do backend (Lemonade) para um modelo de visão.

---

<!-- @os:windows -->
### Atividade 3: Gere uma Imagem a partir de um Prompt de Texto (Stable Diffusion)

Os modelos Stable Diffusion não suportam geração de texto, eles apenas geram imagens através da Images API. 

#### Passo 1: Configure a Geração de Imagens no Open WebUI

1. Na GUI do Lemonade (`http://localhost:13305`), procure por `SDXL-Turbo` (rápido) ou `SDXL-Base-1.0` (maior qualidade) e baixe-o.
2. Vá para **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Defina:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ou `SDXL-Base-1.0`
4. Se você quiser adicionar mais parâmetros, adicione-os ao campo de texto como JSON. Por exemplo: `{ "steps": 4, "cfg_scale": 1 }`. Veja os parâmetros disponíveis em [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Salve
#### Etapa 2: Permitir a Geração de Imagens para o modelo
Esta etapa garante que você habilite a Geração de Imagens como uma capacidade do seu modelo.
1. Vá para **Admin Settings → Models** (http://localhost:8080/admin/settings/models) e escolha seu modelo
2. Ative `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Etapa 3: Gerar uma imagem a partir da tela de chat

1. Volte para o chat em `http://localhost:8080`.
2. Selecione um **LLM de Geração de Texto** no menu suspenso de modelos (exemplo: Qwen, Llama). **Não selecione um modelo Stable Diffusion**, pois este é um seletor de modelo de chat.
3. Na área de mensagens, clique em **Integrations** e ative a opção **Image**.
4. Use um prompt como: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Uma imagem é gerada e aparece no chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Isso estabelece que o Open WebUI pode coordenar um fluxo de trabalho "em duas partes":
  - O LLM ajuda a refinar o prompt
  - A imagem é gerada por meio do endpoint Images do Lemonade usando Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Atividade 3: Gerar uma Imagem a partir de um Prompt de Texto (Stable Diffusion)

Os modelos Stable Diffusion não suportam geração de texto; eles apenas geram imagens por meio da Images API. 

#### Etapa 1: Configurar a Geração de Imagens no Open WebUI

1. Na interface do Lemonade (`http://localhost:13305`), procure por `SDXL-Turbo` (rápido) ou `SDXL-Base-1.0` (maior qualidade) e faça o download.
2. Vá para **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Defina:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ou `SDXL-Base-1.0`
4. Se quiser adicionar mais parâmetros, inclua-os no campo de texto como JSON. Por exemplo: `{ "steps": 4, "cfg_scale": 1 }`. Veja os parâmetros disponíveis em [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Salve


#### Etapa 2: Permitir a Geração de Imagens para o modelo
Esta etapa garante que você habilite a Geração de Imagens como uma capacidade do seu modelo.
1. Vá para **Admin Settings → Models** (http://localhost:8080/admin/settings/models) e escolha seu modelo
2. Ative `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Etapa 3: Gerar uma imagem a partir da tela de chat

1. Volte para o chat em `http://localhost:8080`.
2. Selecione um **LLM de Geração de Texto** no menu suspenso de modelos (exemplo: Qwen, Llama). **Não selecione um modelo Stable Diffusion**, pois este é um seletor de modelo de chat.
3. Na área de mensagens, clique em **Integrations** e ative a opção **Image**.
4. Use um prompt como: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Uma imagem é gerada e aparece no chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Isso estabelece que o Open WebUI pode coordenar um fluxo de trabalho "em duas partes":
  - O LLM ajuda a refinar o prompt
  - A imagem é gerada por meio do endpoint Images do Lemonade usando Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Solução de problemas

### "Nenhum modelo aparece no Open WebUI"
- Primeiro, verifique o Lemonade: abra `http://localhost:13305/api/v1/models` em um navegador e confirme que seus modelos estão listados e baixados
- Em seguida, verifique a conexão do Open WebUI: vá para **Admin Settings → Connections** em `http://localhost:8080/admin/settings/connections` e verifique se a Base URL é `http://localhost:13305/api/v1`

### Mensagem de erro "This model does not support chat completion"
- Você selecionou um modelo de imagem (SDXL-Turbo / SDXL-Base-1.0) no menu suspenso de modelo de chat.
- **Correção**: selecione um LLM para o chat e use o botão de alternância Image + as configurações de Images para geração.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Erros/tempos limite na geração de imagens
- Comece com `SDXL-Turbo` primeiro (rápido, menos etapas)
- Depois que estiver funcionando, mude o modelo de imagem para `SDXL-Base-1.0` para obter mais qualidade

---

## Próximos Passos

Agora você tem uma **'pilha de IA local'** funcional, uma única interface controlando múltiplos tipos de modelos por meio de uma API padrão.

Aqui estão três expansões que desbloqueiam fluxos de trabalho totalmente novos:

### 1. Fala-para-Texto com Whisper

Experimente transformar áudio em texto usando um modelo Whisper e, em seguida, alimentá-lo em um LLM para resumos, itens de ação ou reescrita. Esta é a base para anotações de reuniões e assistentes controlados por voz.

### 2. Programação em Python dentro do Open WebUI

Use a experiência integrada de execução de código do Open WebUI para rodar trechos de Python, inspecionar saídas e iterar mais rápido, sem sair da interface. [Referência](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Renderização de HTML dentro do Open WebUI

Renderize saídas HTML diretamente na interface. Isso é surpreendentemente poderoso para criar protótipos rápidos, relatórios formatados e trechos interativos. [Referência](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referências

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)
- [CLI do Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Guia de integração Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Especificação da API do Lemonade Server (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Vídeo explicativo (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Vídeo explicativo (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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