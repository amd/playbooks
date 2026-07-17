<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa etiquetas especiales que GitHub no puede renderizar. Por favor visita [amd.com/playbooks](https://amd.com/playbooks) para previsualizar este contenido correctamente.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requiere un mínimo de **32GB** de memoria del sistema.
<!-- @device:end -->

## Descripción general

[Open WebUI](https://docs.openwebui.com) es una interfaz basada en navegador y autoalojada que proporciona una experiencia de chatbot familiar, actuando como frontend para uno o más servidores de modelos de IA. En lugar de estar atado a un proveedor, Open WebUI puede conectarse a **cualquier backend que exponga una API compatible con OpenAI**, por lo que puedes cambiar modelos y capacidades sin cambiar de interfaz.

En este playbook, usamos [**Lemonade**](https://lemonade-server.ai) como backend porque expone un **endpoint unificado compatible con OpenAI** que admite múltiples modalidades:
- **Modelos de lenguaje grande (LLMs)** para generación de texto
- **Modelos de visión** para comprensión de imágenes
- **Stable Diffusion** para generación de imágenes
- **Modelos de transcripción de audio** para conversión de voz a texto

Esta configuración te permite explorar el **flujo de trabajo multimodal completo de extremo a extremo**.

---

## Lo que aprenderás

Al finalizar, podrás:

- Conectar Open WebUI a un backend local compatible con OpenAI (Lemonade)
- Chatear con un LLM local desde tu navegador
- Subir una imagen y hacerle preguntas a un modelo de visión sobre ella
- Generar imágenes a partir de indicaciones de texto usando modelos Stable Diffusion (SDXL-Turbo / SDXL)
- Comprender el modelo mental para que puedas usar otros backends (Ollama, vLLM, llama.cpp server, etc.)

---

## Conceptos fundamentales (modelo mental)

### Los tres componentes

| Componente | Qué hace | Ejemplos |
|---|---|---|
| Frontend (UI) | La aplicación web con la que interactúas | Open WebUI |
| Backend (servidor de modelos) | Aloja modelos y expone endpoints HTTP | Lemonade, Ollama, vLLM, llama.cpp server, servidores compatibles con OpenAI |
| Modelos | Los modelos reales de LLM / Visión / Difusión / Audio | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Por qué importa la "API compatible con OpenAI"

Open WebUI está construido alrededor de endpoints estándar al estilo OpenAI, como:
  - Chat: `/chat/completions`
  - Lista de modelos: `/models`
  - Generación de imágenes: `/images/generations`
  - Transcripción de audio: `/audio/transcriptions`

Lemonade los expone bajo `http://localhost:13305/api/v1/...`

Si un backend admite esos endpoints, Open WebUI puede comunicarse con él con una configuración mínima. Por eso podemos cambiar de backend sin modificar nuestro flujo de trabajo.

#### Dos servicios, dos puertos

A lo largo de este playbook trabajarás con dos servicios separados:

| Servicio | URL | Qué haces ahí |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Explorar, descargar y gestionar modelos |
| **Open WebUI** | `http://localhost:8080` | Chatear, subir imágenes, generar imágenes — la UI orientada al usuario |

Lemonade ejecuta los modelos; Open WebUI es la interfaz con la que interactúas. Usa la GUI de Lemonade para descargar tus modelos primero y luego úsalos desde Open WebUI.

---

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Configuración inicial (una sola vez)

Este playbook necesita que Lemonade esté ejecutándose como backend y, en Linux, un motor de contenedores (Podman) para ejecutar Open WebUI. Configura estos elementos antes de instalar Open WebUI.

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

## Descarga de modelos en Lemonade

Antes de instalar Open WebUI, asegúrate de que los modelos que deseas usar estén descargados y listos en Lemonade.

1. Abre la GUI de Lemonade en `http://localhost:13305`.
2. Explora los modelos disponibles y descarga los que deseas usar (por ejemplo, un LLM para chat, un modelo de visión y/o un modelo Stable Diffusion para generación de imágenes).
3. Confirma que la API es accesible visitando `http://localhost:13305/api/v1/models` en tu navegador — deberías ver tus modelos descargados en la lista.

> Los modelos deben descargarse en **Lemonade** (`localhost:13305`) antes de que puedan aparecer en **Open WebUI** (`localhost:8080`). Si un modelo no aparece en Open WebUI más adelante, regresa aquí y verifica Lemonade primero.


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

## Instalación de Open WebUI

<!-- @os:windows -->
### 1. Instalar Python 3.12

Open WebUI requiere **Python 3.12** — no se instala en Python 3.13+. El Lanzador de Python para Windows (`py`) te permite instalar 3.12 junto con cualquier versión de Python existente sin conflictos.

```powershell
winget install Python.Python.3.12
```

Cierra y vuelve a abrir tu terminal después de instalar, luego verifica:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Nota:** Tu sistema viene con Python 3.13 preinstalado. Instalar 3.12 no lo afecta — `python` continúa usando 3.13, y `py -3.12` apunta a 3.12 solo cuando lo necesitas.
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

### 2. Crear un entorno virtual e instalar Open WebUI

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
Ahora vamos a usar el servicio Podman para contenerizar nuestra instalación de Open WebUI.

Por favor descarga lo siguiente en un directorio de tu elección: [compose.yml](assets/compose.yml)

En ese directorio, ejecuta el siguiente comando:

```bash
podman compose up -d
```

Esto descarga la imagen de Open WebUI y escribe en almacenamiento persistente.

Inicia Open WebUI escribiendo `localhost:8080` en la barra de direcciones de tu navegador.

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

> **Consejo**: Open WebUI también ofrece otras opciones de instalación en su [GitHub](https://github.com/open-webui/open-webui).

## Inicio del servidor de Open WebUI

<!-- @os:windows -->
- Ejecuta el siguiente comando para iniciar el servidor HTTP de Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- En un navegador, navega a `http://localhost:8080`.
- Open WebUI te pedirá que crees una cuenta de administrador local. Una vez que hayas iniciado sesión, verás la interfaz de chat.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Mantén la ventana de terminal abierta. Cerrarla detiene Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> El contenedor se ejecuta en segundo plano. Desde el directorio que contiene `compose.yml`, adminístralo con `podman compose down` (detener) y `podman compose up -d` (iniciar). Tus cuentas y configuraciones persisten en el volumen `open_webui_data`.
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

## Conexión de Open WebUI a Lemonade

Ahora que ambos servicios están en ejecución — Lemonade en `localhost:13305` y Open WebUI en `localhost:8080` — conéctalos para que Open WebUI pueda usar los modelos de Lemonade.

En Open WebUI:

1. Haz clic en el **ícono de perfil de usuario** en la esquina superior derecha y selecciona **Configuración**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. En el panel de Configuración, haz clic en **Configuración de administrador** en la parte inferior izquierda.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. En la barra lateral de Configuración de administrador, haz clic en **Conexiones** (o navega directamente a `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. En **OpenAI API**, agrega una nueva conexión:
   - **URL base:** `http://localhost:13305/api/v1`
   - **Clave API:** `-` (un guion simple funciona para uso local)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Asegúrate de que en **"Administrar conexiones de OpenAI API"**, solo `http://localhost:13305/api/v1` esté habilitado. Deshabilita cualquier otra conexión (por ejemplo, la de OpenAI predeterminada).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Haz clic en **Guardar**.

7. **(Recomendado)** Deshabilita las funciones de generación automática para mantener Open WebUI responsivo con LLMs locales. Ve a **Configuración de administrador → Configuración → Interfaz** y desactiva:
   - Generación de título
   - Generación de seguimiento
   - Generación de etiquetas

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Haz clic en **Guardar**, luego regresa a `http://localhost:8080`.
9. Haz clic en el menú desplegable de modelos — deberías ver los modelos que descargaste desde Lemonade.

---

## Actividades principales

Ahora estás listo. Veamos tres cosas interesantes que puedes hacer.

---

### Actividad 1: Chatear con un LLM local
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Haz clic en el menú desplegable en la parte superior izquierda de la interfaz. Esto mostrará los modelos de Lemonade que tienes instalados. Selecciona uno para continuar. (ejemplo: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Escribe un mensaje al LLM y haz clic en enviar (o presiona Enter). El LLM tardará unos segundos en cargarse en memoria y luego verás la respuesta aparecer en tiempo real.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Haz clic en el menú desplegable en la parte superior izquierda de la interfaz. Esto mostrará los modelos de Lemonade que tienes instalados. Selecciona uno para continuar. (ejemplo: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Escribe un mensaje al LLM y haz clic en enviar (o presiona Enter). El LLM tardará unos segundos en cargarse en memoria y luego verás la respuesta aparecer en tiempo real.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. El modelo responderá en el chat.

4. En este momento, abre el `Administrador de tareas` en tu sistema. Verás **alta utilización de GPU o NPU** según si el modelo que seleccionaste es **Hybrid** o **NPU** respectivamente. Usando el administrador de tareas, puedes confirmar que estás ejecutando el modelo localmente.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Haz clic en el menú desplegable en la parte superior izquierda de la interfaz. Esto mostrará los modelos de Lemonade que tienes instalados. Selecciona uno para continuar. (ejemplo: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Escribe un mensaje al LLM y haz clic en enviar (o presiona Enter). El LLM tardará unos segundos en cargarse en memoria y luego verás la respuesta aparecer en tiempo real.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. El modelo responderá en el chat.
<!-- @os:end -->

Esto valida que Open WebUI puede enviar solicitudes a Lemonade usando el endpoint de chat compatible con OpenAI.

---

### Actividad 2: Subir una imagen y hacer preguntas (Visión)

Esto requiere un modelo que admita entrada de imágenes (un modelo de Visión o Multimodal).

1. Haz clic en el ícono de filtro, selecciona "Por categoría" y luego elige un modelo de la sección **Visión** (por ejemplo, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Haz clic en el botón **`+`** en el cuadro de mensaje y sube una imagen
3. Haz una pregunta que requiera una comprensión real de la imagen: `¿Crees que esta es una GUI bien diseñada?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. El modelo responde basándose en el contenido de la imagen, no en texto genérico.

Esto demuestra que Open WebUI puede enviar solicitudes multimodales (texto + imagen) a través del backend (Lemonade) a un modelo de visión.

---

<!-- @os:windows -->
### Actividad 3: Generar una imagen a partir de una indicación de texto (Stable Diffusion)

Los modelos Stable Diffusion no admiten generación de texto; solo generan imágenes a través de la API de imágenes.

#### Paso 1: Configurar la generación de imágenes en Open WebUI

1. En la GUI de Lemonade (`http://localhost:13305`), busca `SDXL-Turbo` (rápido) o `SDXL-Base-1.0` (mayor calidad) y descárgalo.
2. Ve a **Configuración de administrador → Imágenes** (http://localhost:8080/admin/settings/images)
3. Configura:
   - **Generación de imágenes:** ACTIVADO
   - **Motor de generación de imágenes:** Predeterminado (OpenAI)
   - **URL base de OpenAI API:** `http://localhost:13305/api/v1`
   - **Clave de OpenAI API:** `-`
   - **Modelo:** `SDXL-Turbo` o `SDXL-Base-1.0`
4. Si deseas agregar más parámetros, agrégalos al campo de texto como JSON. Por ejemplo: `{ "steps": 4, "cfg_scale": 1 }`. Consulta los parámetros disponibles en [Generación de imágenes (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Guardar


#### Paso 2: Habilitar la generación de imágenes para el modelo
Este paso garantiza que habilites la generación de imágenes como capacidad para tu modelo.
1. Ve a **Configuración de administrador → Modelos** (http://localhost:8080/admin/settings/models) y elige tu modelo
2. Activa `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Paso 3: Generar una imagen desde la pantalla de chat

1. Regresa al chat en `http://localhost:8080`.
2. Selecciona un **LLM de generación de texto** en el menú desplegable de modelos (ejemplo: Qwen, Llama). **No selecciones un modelo Stable Diffusion** ya que este es un selector de modelos de chat.
3. En el área de mensajes, haz clic en **Integraciones** y activa **Imagen**.
4. Usa una indicación como: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Se genera una imagen y aparece en el chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Esto establece que Open WebUI puede coordinar un flujo de trabajo de "dos partes":
  - El LLM ayuda a refinar la indicación
  - La imagen se genera a través del endpoint de imágenes de Lemonade usando Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Actividad 3: Generar una imagen a partir de una indicación de texto (Stable Diffusion)

Los modelos Stable Diffusion no admiten generación de texto; solo generan imágenes a través de la API de imágenes.

#### Paso 1: Configurar la generación de imágenes en Open WebUI

1. En la GUI de Lemonade (`http://localhost:13305`), busca `SDXL-Turbo` (rápido) o `SDXL-Base-1.0` (mayor calidad) y descárgalo.
2. Ve a **Configuración de administrador → Imágenes** (http://localhost:8080/admin/settings/images)
3. Configura:
   - **Generación de imágenes:** ACTIVADO
   - **Motor de generación de imágenes:** Predeterminado (OpenAI)
   - **URL base de OpenAI API:** `http://localhost:13305/api/v1`
   - **Clave de OpenAI API:** `-`
   - **Modelo:** `SDXL-Turbo` o `SDXL-Base-1.0`
4. Si deseas agregar más parámetros, agrégalos al campo de texto como JSON. Por ejemplo: `{ "steps": 4, "cfg_scale": 1 }`. Consulta los parámetros disponibles en [Generación de imágenes (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Guardar


#### Paso 2: Habilitar la generación de imágenes para el modelo
Este paso garantiza que habilites la generación de imágenes como capacidad para tu modelo.
1. Ve a **Configuración de administrador → Modelos** (http://localhost:8080/admin/settings/models) y elige tu modelo
2. Activa `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Paso 3: Generar una imagen desde la pantalla de chat

1. Regresa al chat en `http://localhost:8080`.
2. Selecciona un **LLM de generación de texto** en el menú desplegable de modelos (ejemplo: Qwen, Llama). **No selecciones un modelo Stable Diffusion** ya que este es un selector de modelos de chat.
3. En el área de mensajes, haz clic en **Integraciones** y activa **Imagen**.
4. Usa una indicación como: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Se genera una imagen y aparece en el chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Esto establece que Open WebUI puede coordinar un flujo de trabajo de "dos partes":
  - El LLM ayuda a refinar la indicación
  - La imagen se genera a través del endpoint de imágenes de Lemonade usando Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Solución de problemas

### "No aparecen modelos en Open WebUI"
- Primero, verifica Lemonade: abre `http://localhost:13305/api/v1/models` en un navegador y confirma que tus modelos están listados y descargados
- Luego, verifica la conexión de Open WebUI: ve a **Configuración de administrador → Conexiones** en `http://localhost:8080/admin/settings/connections` y verifica que la URL base sea `http://localhost:13305/api/v1`

### Mensaje de error "Este modelo no admite completado de chat"
- Seleccionaste un modelo de imagen (SDXL-Turbo / SDXL-Base-1.0) en el menú desplegable de modelos de chat.
- **Solución**: selecciona un LLM para el chat y usa el interruptor de Imagen + la configuración de Imágenes para la generación.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Errores o tiempos de espera en la generación de imágenes
- Comienza con `SDXL-Turbo` primero (rápido, menos pasos)
- Una vez que funcione, cambia el modelo de imagen a `SDXL-Base-1.0` para mayor calidad

---

## Próximos pasos

Ahora tienes una **'pila de IA local'** funcional, una sola interfaz que controla múltiples tipos de modelos a través de una API estándar.

Aquí hay tres expansiones que desbloquean flujos de trabajo completamente nuevos:

### 1. Conversión de voz a texto con Whisper

Prueba convertir audio en texto usando un modelo Whisper y luego aliméntalo a un LLM para resumir, extraer elementos de acción o reescribir. Esta es la base para notas de reuniones y asistentes controlados por voz.

### 2. Programación en Python dentro de Open WebUI

Usa la experiencia de ejecución de código integrada de Open WebUI para ejecutar fragmentos de Python, inspeccionar resultados e iterar más rápido, sin salir de la interfaz. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Renderizado de HTML dentro de Open WebUI

Renderiza salidas HTML directamente en la interfaz. Esto es sorprendentemente poderoso para crear prototipos rápidos, informes con formato y fragmentos interactivos. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referencias

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Documentación de Lemonade Server](https://lemonade-server.ai/docs)
- [CLI de Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Guía de integración Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Especificación de la API de Lemonade Server (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Video tutorial (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video tutorial (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)