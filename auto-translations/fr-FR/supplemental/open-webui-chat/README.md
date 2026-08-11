<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ce playbook nécessite un minimum de **32 Go** de mémoire système.
<!-- @device:end -->

## Présentation

[Open WebUI](https://docs.openwebui.com) est une interface auto-hébergée basée sur navigateur qui offre une expérience de chatbot familière tout en agissant comme frontend pour un ou plusieurs serveurs de modèles d'IA. Plutôt que d'être lié à un seul fournisseur, Open WebUI peut se connecter à **n'importe quel backend exposant une API compatible OpenAI**, ce qui vous permet de changer de modèles et de fonctionnalités sans changer d'interface.

Dans ce playbook, nous utilisons [**Lemonade**](https://lemonade-server.ai) comme backend, car il expose un **point de terminaison unifié compatible OpenAI** prenant en charge plusieurs modalités :
- **Grands modèles de langage (LLM)** pour la génération de texte
- **Modèles de vision** pour la compréhension d'images
- **Stable Diffusion** pour la génération d'images
- **Modèles de transcription audio** pour la conversion de la parole en texte

Cette configuration vous permet d'explorer le **workflow multimodal complet de bout en bout**.

---

## Ce que vous allez apprendre

À la fin, vous serez capable de :

- Connecter Open WebUI à un backend local compatible OpenAI (Lemonade)
- Discuter avec un LLM local depuis votre navigateur
- Charger une image et poser des questions à un modèle de vision à son sujet
- Générer des images à partir de prompts textuels à l'aide de modèles Stable Diffusion (SDXL-Turbo / SDXL)
- Comprendre le modèle conceptuel afin de pouvoir utiliser d'autres backends (Ollama, vLLM, serveur llama.cpp, etc.)

---

## Concepts fondamentaux (modèle conceptuel)

### Les trois composants

| Élément | Ce qu'il fait | Exemples |
|---|---|---|
| Frontend (interface) | L'application web avec laquelle vous interagissez | Open WebUI |
| Backend (serveur de modèles) | Héberge les modèles et expose des points de terminaison HTTP | Lemonade, Ollama, vLLM, serveur llama.cpp, serveurs compatibles OpenAI |
| Modèles | Les modèles LLM / Vision / Diffusion / Audio proprement dits | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Pourquoi une « API compatible OpenAI » est importante

Open WebUI est conçu autour de points de terminaison standard de type OpenAI, tels que :
  - Chat : `/chat/completions`
  - Liste des modèles : `/models`
  - Génération d'images : `/images/generations`
  - Transcription audio : `/audio/transcriptions`

Lemonade expose ces points de terminaison sous `http://localhost:13305/api/v1/...`

Si un backend prend en charge ces points de terminaison, Open WebUI peut communiquer avec lui avec une configuration minimale. C'est pourquoi nous pouvons changer de backend sans modifier notre workflow.

#### Deux services, deux ports

Tout au long de ce playbook, vous travaillerez avec deux services distincts :

| Service | URL | Ce que vous y faites |
|---|---|---|
| **Lemonade** (interface graphique) | `http://localhost:13305` | Parcourir, télécharger et gérer les modèles |
| **Open WebUI** | `http://localhost:8080` | Discuter, charger des images, générer des images — l'interface utilisateur |

Lemonade exécute les modèles ; Open WebUI est l'interface avec laquelle vous interagissez. Utilisez d'abord l'interface graphique de Lemonade pour télécharger vos modèles, puis utilisez-les depuis Open WebUI.

---

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Configuration initiale

Ce playbook nécessite que Lemonade fonctionne comme backend et, sous Linux, un moteur de conteneurs (Podman) pour exécuter Open WebUI. Configurez ces éléments avant d'installer Open WebUI.

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

## Téléchargement des modèles dans Lemonade

Avant d'installer Open WebUI, assurez-vous que les modèles que vous souhaitez utiliser sont téléchargés et prêts dans Lemonade.

1. Ouvrez l'interface graphique de Lemonade à l'adresse `http://localhost:13305`.
2. Parcourez les modèles disponibles et téléchargez ceux que vous souhaitez utiliser (par exemple, un LLM pour le chat, un modèle de vision et/ou un modèle Stable Diffusion pour la génération d'images).
3. Vérifiez que l'API est accessible en visitant `http://localhost:13305/api/v1/models` dans votre navigateur — vous devriez voir la liste de vos modèles téléchargés.

> Les modèles doivent être téléchargés dans **Lemonade** (`localhost:13305`) avant de pouvoir apparaître dans **Open WebUI** (`localhost:8080`). Si un modèle n'apparaît pas plus tard dans Open WebUI, revenez ici et vérifiez d'abord Lemonade.


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

## Installation d'Open WebUI

<!-- @os:windows -->
### 1. Installer Python 3.12

Open WebUI nécessite **Python 3.12** — il ne s'installe pas sur Python 3.13 ou supérieur. Le lanceur Python de Windows (`py`) vous permet d'installer la version 3.12 en parallèle de toute version Python existante, sans conflit.

```powershell
winget install Python.Python.3.12
```

Fermez et rouvrez votre terminal après l'installation, puis vérifiez :

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Remarque :** Votre système est livré avec Python 3.13 préinstallé. L'installation de la version 3.12 ne l'affecte pas — `python` continue d'utiliser la version 3.13, et `py -3.12` cible la version 3.12 uniquement lorsque vous en avez besoin.
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

### 2. Créer un environnement virtuel et installer Open WebUI

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
Nous allons maintenant utiliser le service Podman pour containeriser notre installation d'Open WebUI.

Veuillez télécharger le fichier suivant dans un répertoire de votre choix : [compose.yml](assets/compose.yml)

Dans ce répertoire, exécutez la commande suivante :

```bash
podman compose up -d
```

Cette commande récupère l'image Open WebUI et l'écrit dans un stockage persistant.

Lancez Open WebUI en saisissant `localhost:8080` dans la barre d'adresse de votre navigateur.

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

> **Astuce** : Open WebUI propose également d'autres options d'installation sur leur [GitHub](https://github.com/open-webui/open-webui).
## Démarrage du serveur Open WebUI

<!-- @os:windows -->
- Exécutez la commande suivante pour lancer le serveur HTTP Open WebUI :
```bash
open-webui serve
```
<!-- @os:end -->

- Dans un navigateur, accédez à `http://localhost:8080`.
- Open WebUI vous demandera de créer un compte administrateur local. Une fois connecté, vous verrez l'interface de chat.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Gardez la fenêtre du terminal ouverte. La fermer arrête Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Le conteneur s'exécute en arrière-plan. Depuis le répertoire contenant `compose.yml`, gérez-le avec `podman compose down` (arrêt) et `podman compose up -d` (démarrage). Vos comptes et paramètres sont conservés dans le volume `open_webui_data`.
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

## Connexion d'Open WebUI à Lemonade

Maintenant que les deux services sont en cours d'exécution — Lemonade sur `localhost:13305` et Open WebUI sur `localhost:8080` — connectez-les pour qu'Open WebUI puisse utiliser les modèles de Lemonade.

Dans Open WebUI :

1. Cliquez sur l'**icône de profil utilisateur** dans le coin supérieur droit, puis sélectionnez **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Dans le panneau Settings, cliquez sur **Admin Settings** en bas à gauche.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Dans la barre latérale Admin Settings, cliquez sur **Connections** (ou accédez directement à `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Sous **OpenAI API**, ajoutez une nouvelle connexion :
   - **Base URL :** `http://localhost:13305/api/v1`
   - **API Key :** `-` (un simple tiret fonctionne en local)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Assurez-vous que sous **"Manage OpenAI API Connections"**, seule `http://localhost:13305/api/v1` est activée. Désactivez toute autre connexion (par exemple, celle par défaut d'OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Cliquez sur **Save**.

7. **(Recommandé)** Désactivez les fonctionnalités de génération automatique pour garder Open WebUI réactif avec les LLM locaux. Allez dans **Admin Settings → Settings → Interface** et désactivez :
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Cliquez sur **Save**, puis revenez à `http://localhost:8080`.
9. Cliquez sur le menu déroulant des modèles — vous devriez voir les modèles que vous avez téléchargés depuis Lemonade.

---

## Activités principales

Maintenant, tout est configuré. Examinons trois choses intéressantes à faire.

---

### Activité 1 : Discuter avec un LLM local
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Cliquez sur le menu déroulant en haut à gauche de l'interface. Cela affichera les modèles Lemonade que vous avez installés. Sélectionnez-en un pour continuer (exemple : `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Saisissez un message pour le LLM et cliquez sur envoyer (ou appuyez sur Entrée). Le LLM prendra quelques secondes pour se charger en mémoire, puis vous verrez la réponse s'afficher progressivement.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Cliquez sur le menu déroulant en haut à gauche de l'interface. Cela affichera les modèles Lemonade que vous avez installés. Sélectionnez-en un pour continuer (exemple : `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Saisissez un message pour le LLM et cliquez sur envoyer (ou appuyez sur Entrée). Le LLM prendra quelques secondes pour se charger en mémoire, puis vous verrez la réponse s'afficher progressivement.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Le modèle répondra dans le chat.

4. À ce moment, ouvrez le `Gestionnaire des tâches` sur votre système. Vous verrez une **utilisation élevée du GPU ou du NPU** selon que le modèle sélectionné est **Hybrid** ou **NPU** respectivement. Grâce au gestionnaire des tâches, vous pouvez confirmer que vous exécutez le modèle localement.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Cliquez sur le menu déroulant en haut à gauche de l'interface. Cela affichera les modèles Lemonade que vous avez installés. Sélectionnez-en un pour continuer (exemple : `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Saisissez un message pour le LLM et cliquez sur envoyer (ou appuyez sur Entrée). Le LLM prendra quelques secondes pour se charger en mémoire, puis vous verrez la réponse s'afficher progressivement.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Le modèle répondra dans le chat.
<!-- @os:end -->

Cela valide qu'Open WebUI peut envoyer des requêtes à Lemonade en utilisant le point de terminaison de chat compatible OpenAI.

---

### Activité 2 : Téléverser une image et poser des questions (Vision)

Cela nécessite un modèle prenant en charge l'entrée d'images (un modèle Vision ou Multimodal).

1. Cliquez sur l'icône de filtre, sélectionnez « By Category », puis choisissez un modèle dans la section **Vision** (par exemple, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Cliquez sur le bouton **`+`** dans la zone de message et téléversez une image
3. Posez une question qui force une véritable compréhension de l'image : `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Le modèle répond en se basant sur le contenu de l'image, et non sur un texte générique.

Cela démontre qu'Open WebUI peut envoyer des requêtes multimodales (texte + image) via le backend (Lemonade) à un modèle de vision.

---

<!-- @os:windows -->
### Activité 3 : Générer une image à partir d'une invite textuelle (Stable Diffusion)

Les modèles Stable Diffusion ne prennent pas en charge la génération de texte, ils génèrent uniquement des images via l'API Images.

#### Étape 1 : Configurer la génération d'images dans Open WebUI

1. Dans l'interface graphique Lemonade (`http://localhost:13305`), recherchez `SDXL-Turbo` (rapide) ou `SDXL-Base-1.0` (meilleure qualité) et téléchargez-le.
2. Allez dans **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Définissez :
   - **Image Generation :** ON
   - **Image Generation Engine :** Default (OpenAI)
   - **OpenAI API Base URL :** `http://localhost:13305/api/v1`
   - **OpenAI API Key :** `-`
   - **Model :** `SDXL-Turbo` ou `SDXL-Base-1.0`
4. Si vous souhaitez ajouter davantage de paramètres, ajoutez-les dans le champ texte au format JSON. Par exemple : `{ "steps": 4, "cfg_scale": 1 }`. Consultez les paramètres disponibles sur [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Enregistrez
#### Étape 2 : Autoriser la génération d'images pour le modèle
Cette étape permet d'activer la génération d'images en tant que capacité de votre modèle.
1. Allez dans **Admin Settings → Models** (http://localhost:8080/admin/settings/models) et choisissez votre modèle
2. Activez `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Étape 3 : Générer une image depuis l'écran de discussion

1. Retournez à la discussion sur `http://localhost:8080`.
2. Sélectionnez un **LLM de génération de texte** dans le menu déroulant des modèles (exemple : Qwen, Llama). **Ne sélectionnez pas un modèle Stable Diffusion**, car il s'agit d'un sélecteur de modèle de discussion.
3. Dans la zone de message, cliquez sur **Integrations**, puis activez **Image**.
4. Utilisez une invite comme : `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Une image est générée et apparaît dans la discussion.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Cela établit qu'Open WebUI peut coordonner un flux de travail « en deux parties » :
  - Le LLM aide à affiner l'invite
  - L'image est générée via le point de terminaison Images de Lemonade en utilisant Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Activité 3 : Générer une image à partir d'une invite textuelle (Stable Diffusion)

Les modèles Stable Diffusion ne prennent pas en charge la génération de texte ; ils génèrent uniquement des images via l'API Images. 

#### Étape 1 : Configurer la génération d'images dans Open WebUI

1. Dans l'interface graphique de Lemonade (`http://localhost:13305`), recherchez `SDXL-Turbo` (rapide) ou `SDXL-Base-1.0` (meilleure qualité) et téléchargez-le.
2. Allez dans **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Définissez :
   - **Image Generation :** ON
   - **Image Generation Engine :** Default (OpenAI)
   - **OpenAI API Base URL :** `http://localhost:13305/api/v1`
   - **OpenAI API Key :** `-`
   - **Model :** `SDXL-Turbo` ou `SDXL-Base-1.0`
4. Si vous souhaitez ajouter d'autres paramètres, ajoutez-les dans le champ de texte au format JSON. Par exemple : `{ "steps": 4, "cfg_scale": 1 }`. Consultez les paramètres disponibles sur [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Enregistrez


#### Étape 2 : Autoriser la génération d'images pour le modèle
Cette étape permet d'activer la génération d'images en tant que capacité de votre modèle.
1. Allez dans **Admin Settings → Models** (http://localhost:8080/admin/settings/models) et choisissez votre modèle
2. Activez `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Étape 3 : Générer une image depuis l'écran de discussion

1. Retournez à la discussion sur `http://localhost:8080`.
2. Sélectionnez un **LLM de génération de texte** dans le menu déroulant des modèles (exemple : Qwen, Llama). **Ne sélectionnez pas un modèle Stable Diffusion**, car il s'agit d'un sélecteur de modèle de discussion.
3. Dans la zone de message, cliquez sur **Integrations**, puis activez **Image**.
4. Utilisez une invite comme : `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Une image est générée et apparaît dans la discussion.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Cela établit qu'Open WebUI peut coordonner un flux de travail « en deux parties » :
  - Le LLM aide à affiner l'invite
  - L'image est générée via le point de terminaison Images de Lemonade en utilisant Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Dépannage

### « Aucun modèle n'apparaît dans Open WebUI »
- Vérifiez d'abord Lemonade : ouvrez `http://localhost:13305/api/v1/models` dans un navigateur et confirmez que vos modèles sont listés et téléchargés
- Vérifiez ensuite la connexion à Open WebUI : allez dans **Admin Settings → Connections** sur `http://localhost:8080/admin/settings/connections` et vérifiez que l'URL de base est `http://localhost:13305/api/v1`

### Message d'erreur « This model does not support chat completion »
- Vous avez sélectionné un modèle d'image (SDXL-Turbo / SDXL-Base-1.0) dans le menu déroulant du modèle de discussion.
- **Solution** : sélectionnez un LLM pour la discussion, et utilisez le bouton Image + les paramètres Images pour la génération.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Erreurs/délais d'attente de génération d'images
- Commencez d'abord par `SDXL-Turbo` (rapide, moins d'étapes)
- Une fois cela fonctionnel, passez au modèle d'image `SDXL-Base-1.0` pour une meilleure qualité

---

## Prochaines étapes

Vous disposez désormais d'une **« pile IA locale »** fonctionnelle, une interface unique contrôlant plusieurs types de modèles via une API standard.

Voici trois extensions qui débloquent des flux de travail entièrement nouveaux :

### 1. Reconnaissance vocale avec Whisper

Essayez de convertir de l'audio en texte à l'aide d'un modèle Whisper, puis transmettez-le à un LLM pour le résumer, en extraire des actions à mener, ou le reformuler. C'est la base des comptes rendus de réunion et des assistants vocaux.

### 2. Codage Python dans Open WebUI

Utilisez l'expérience d'exécution de code intégrée d'Open WebUI pour exécuter des extraits Python, inspecter les résultats et itérer plus rapidement, sans quitter l'interface. [Référence](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Rendu HTML dans Open WebUI

Affichez directement les sorties HTML dans l'interface. C'est étonnamment puissant pour créer des prototypes rapides, des rapports mis en forme et des extraits interactifs. [Référence](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Références

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Documentation Lemonade Server](https://lemonade-server.ai/docs)
- [CLI de Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Guide d'intégration Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Spécification de l'API Lemonade Server (points de terminaison)](https://lemonade-server.ai/docs/server/server_spec)
- [Présentation vidéo (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Présentation vidéo (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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