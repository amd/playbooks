<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Resumen

Los desarrolladores dedican mucho tiempo a pequeños ciclos recurrentes: revisar solicitudes de incorporación de cambios (pull requests) etiquetadas, responder comentarios de GitHub, clasificar nuevos issues, convertir hilos de Slack en notas de standup o seguimientos de incidentes, y hacer seguimiento de señales de lanzamientos o investigación.
Cada ciclo es familiar, pero igualmente requiere criterio: reunir el contexto correcto, decidir qué es importante y publicar una actualización clara donde el equipo ya trabaja.

Las [automatizaciones de OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) convierten esos ciclos en conversaciones de agentes programadas o activadas por eventos: ejecuciones en las que un agente de software de IA puede leer contexto, invocar herramientas y producir una actualización.
Las plantillas de automatización compartidas en el catálogo de extensiones de OpenHands siguen este patrón para revisión de pull requests de GitHub, monitoreo de repositorios, clasificación de issues de Linear, retrospectivas de incidentes, resúmenes de standup en Slack y reportes de investigación: una automatización se activa, usa integraciones configuradas como GitHub o Slack para obtener contexto, razona sobre ese contexto con un modelo de lenguaje grande (LLM) y escribe un resultado.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) es el plano de control local para construir y probar esas automatizaciones.
En esta guía, ejecuta un OpenHands Agent Server, el proceso backend que ejecuta las conversaciones de agentes, y conecta al agente con servicios externos como GitHub y Slack.

Para mantener el flujo de trabajo en tu sistema AMD, el agente se comunica con un modelo local servido por Lemonade Server.
Lemonade expone ese modelo a través de una API compatible con OpenAI, de modo que Agent Canvas puede configurarlo como un endpoint remoto de estilo OpenAI, mientras que el modelo, el prompt y el contexto del flujo de trabajo permanecen locales.

En esta guía, construirás una automatización concreta: un resumen programado de desarrollo de GitHub a Slack.
Utiliza GitHub para inspeccionar la actividad reciente del repositorio, Slack para publicar el resumen, llamadas a la API de Agent Canvas para configurar y probar la automatización, y Lemonade para ejecutar el LLM localmente.

![Diagrama de arquitectura que muestra GitHub MCP, automatización de OpenHands, Lemonade Server y Slack MCP](assets/00-architecture-overview.png)

## Qué aprenderás

- Cómo iniciar Lemonade Server y verificar que un modelo local responda solicitudes de chat
- Cómo lanzar Agent Canvas y apuntar su Agent Server a un LLM local
- Cómo instalar servidores de Model Context Protocol (MCP) de GitHub y Slack a través de la API de Agent Server
- Cómo crear y disparar una automatización programada de OpenHands que publique un resumen de desarrollo en Slack
- Cómo solucionar los problemas más comunes de modelos locales y automatizaciones

## Conceptos principales

| Concepto | Qué es | Dónde encaja en esta guía |
| --- | --- | --- |
| Lemonade Server | Una plataforma local de servicio de LLM creada para hardware AMD que expone una API compatible con OpenAI. Tus datos nunca salen de tu máquina. | Ejecuta el modelo que impulsa al agente. |
| OpenHands Agent Server | El proceso backend que ejecuta las conversaciones de agentes de OpenHands. | Aloja al agente, su perfil de LLM y sus servidores MCP. |
| Agent Canvas | El plano de control local para OpenHands que ejecuta Agent Server y una interfaz de usuario para inspeccionar las ejecuciones del agente. | Lanza los backends y proporciona la API que invocas. |
| Servidor MCP | Un servidor de Model Context Protocol que le da a un agente herramientas para un servicio externo como GitHub o Slack. | Permite que el agente lea GitHub y escriba en Slack. |
| Automatización de OpenHands | Una conversación de agente programada o activada por eventos que obtiene contexto, razona sobre él y escribe un resultado en algún lugar. | El resumen de GitHub a Slack que construyes aquí. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Los flujos de trabajo de agentes de programación se benefician de un modelo y una ventana de contexto más grandes.
> Usa al menos 32 GB de memoria del sistema, y prefiere 64 GB o más para modelos GGUF más grandes.
<!-- @device:end -->

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificación de actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Requisitos previos

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Necesitas:

- Lemonade Server instalado siguiendo la [guía de instalación de Lemonade](https://lemonade-server.ai/docs/guide/install/) estándar.

<!-- @os:linux -->
- Node.js 22.12 o posterior y `npm`, usados para instalar el CLI publicado de Agent Canvas y ejecutar servidores MCP con `npx`.
- `uv`, el administrador de paquetes de Python que Agent Canvas utiliza para construir el entorno de Agent Server. Si aún no está instalado, instálalo desde la [guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).
- Un paquete publicado reciente de `@openhands/agent-canvas` con configuración de agente basada en esquemas, `LLMSummarizingCondenserSettings.max_tokens` y soporte de `custom_tokenizer` para LLM.
- El paquete de Python `transformers` disponible en el entorno de Agent Server. Es necesario para el conteo de tokens de plantillas de chat cuando se configura `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/), instalado y en ejecución. En Windows, la pila de Agent Canvas se ejecuta desde la imagen Docker publicada, que incluye Node.js, `uv`, `transformers` y el paquete `@openhands/agent-canvas`, por lo que no es necesario instalarlos en el host.
<!-- @os:end -->

- Un token de GitHub con acceso de lectura al repositorio que quieres resumir.
- Un token de bot de Slack (`xoxb-...`) con `chat:write` y acceso de lectura a canales.
- Un ID de equipo de Slack (`T...`).
- Un ID de canal de Slack (`C...`) donde debe publicarse el resumen.

Invita a la aplicación de Slack al canal de destino antes de probar la automatización.
## Variables Usadas en Este Playbook

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Estas dos variables son usadas por los comandos de verificación a continuación.
El modelo, el tokenizador y otras configuraciones de LLM se ingresan directamente en la interfaz de usuario de Agent Canvas en pasos posteriores, por lo que sus valores literales se muestran en línea donde los necesites.

Los siguientes valores se ingresan en la interfaz de usuario de Agent Canvas en pasos posteriores.
Configúralos aquí para que puedas copiarlos:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Usa un valor explícito de `owner/repo` para `GITHUB_REPO_FILTER`.
Los comodines de organización amplios pueden devolver demasiado contexto MCP para los modelos locales.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Iniciar el Servidor Lemonade

Inicia el modelo desde el CLI de Lemonade:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Elige un modelo que se ajuste a tu hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) es un modelo sólido para este flujo de trabajo, pero necesita un pool de memoria grande.
> Si tu dispositivo tiene memoria o VRAM de GPU limitada, elige un modelo GGUF más pequeño de la librería de modelos de Lemonade y usa ese ID de modelo (y su tokenizador correspondiente) a lo largo de este playbook.

> **Nota:** El primer `lemonade run` descarga el modelo si aún no está presente, lo cual puede tomar un tiempo dependiendo del tamaño del modelo y tu conexión.

Lemonade expone una API compatible con OpenAI en:

```text
http://127.0.0.1:13305/api/v1
```

Opcional: si Agent Canvas o el ejecutor de automatización no están en la misma máquina, publica el endpoint de Lemonade a través de un túnel seguro y usa la URL HTTPS como la URL base del LLM.
[ngrok](https://ngrok.com/) expone un puerto local a internet a través de una URL HTTPS segura; requiere una cuenta gratuita de ngrok, y reemplazas `YOUR_NGROK_DOMAIN.ngrok-free.dev` con tu propio dominio reservado:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificar el Modelo Local

Confirma que Lemonade puede servir el modelo seleccionado:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Luego envía una pequeña solicitud de chat:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Luego envía una pequeña solicitud de chat:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Si esto devuelve un arreglo `choices`, Lemonade está listo para Agent Canvas.

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
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
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Iniciar Agent Canvas

<!-- @os:linux -->
Instala el paquete publicado de Agent Canvas e inicia la pila completa:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Si la instalación global de npm falla con un error de permisos, consulta la entrada de solución de problemas de permisos de npm a continuación.

Por defecto, Agent Canvas se inicia en `http://localhost:8000`.
Abre esa URL en tu navegador.
El puerto no es especial—si el 8000 ya está en uso, pasa cualquier puerto libre con `--port` (o `-p`).
El backend local predeterminado debería mostrarse como saludable en la pantalla de inicio.

> **Nota:** El primer inicio construye el entorno Python administrado por `uv` del Agent Server, por lo que puede tomar algunos minutos antes de que el backend reporte estar saludable.

El comando `agent-canvas` inicia el servidor de agentes, el backend de automatización y el frontend web juntos.
Solo necesitas este único comando para ejecutar OpenHands localmente.
El resto de este playbook configura todo a través de la interfaz de usuario de Agent Canvas en tu navegador.
<!-- @os:end -->

<!-- @os:windows -->
En Windows, ejecuta la imagen de contenedor publicada de Agent Canvas con Docker Desktop.
La imagen incluye el Agent Server, el backend de automatización y el frontend web, por lo que no necesitas instalar Node.js, `uv`, ni el CLI en el host.

Primero, crea las carpetas de configuración y espacio de trabajo que monta el contenedor:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Descarga la imagen publicada (aproximadamente 6 GB; es pública, así que no se requiere iniciar sesión):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Luego inicia la pila:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Abre `http://localhost:8000/canvas` en tu navegador.
Si el puerto 8000 ya está en uso, mapea un puerto de host diferente, por ejemplo `-p 8080:8000`, y abre `http://localhost:8080/canvas` en su lugar.

> **Nota:** El primer inicio construye el entorno del Agent Server dentro del contenedor, por lo que puede tomar algunos minutos antes de que el backend reporte estar saludable.

El montaje `.openhands` conserva tu perfil de LLM, servidores MCP y automatizaciones entre reinicios del contenedor.
El resto de este playbook configura todo a través de la interfaz de usuario de Agent Canvas en tu navegador en `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. Configurar el LLM local en la interfaz de usuario

En el primer inicio, Agent Canvas abre un flujo de incorporación.
En ese flujo:

1. Mantén **OpenHands** seleccionado como el agente y haz clic en **Next**.
2. En **Set up your LLM**, selecciona **Advanced**.
3. Mantén **Authentication** configurado como **API key**.
4. Configura **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Configura **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Para **API Key**, ingresa cualquier marcador de posición no vacío, como `lemonade-local`. Lemonade no requiere una clave real, pero el cliente de OpenHands necesita un valor para enviar.

<!-- @os:windows -->
> **Windows (Docker):** el Agent Server se ejecuta dentro del contenedor, así que configura **Base URL** como `http://host.docker.internal:13305/api/v1` en lugar de `http://127.0.0.1:13305/api/v1`.
> Desde dentro del contenedor, `127.0.0.1` es el propio contenedor; `host.docker.internal` llega a Lemonade que se ejecuta en el host Windows, y Docker Desktop proporciona ese nombre de host automáticamente.
<!-- @os:end -->

Los campos de conexión deben verse así.
El campo de clave de API está enmascarado por la interfaz de usuario.

![Configuración avanzada del LLM de Agent Canvas en el primer uso, con el modelo de Lemonade y la URL base local](assets/01-llm-advanced-settings.png)

Luego selecciona **All** y configura los campos adicionales del modelo local:

1. Desplázate hasta **Custom Tokenizer** y configúralo como `Qwen/Qwen3.6-35B-A3B`.
2. Desplázate hasta **LiteLLM Extra Body** y configúralo como `{"enable_thinking": true}`.
3. Haz clic en **Next**.

![Pestaña All del LLM de Agent Canvas en el primer uso, con el tokenizador personalizado de Qwen](assets/02-llm-all-tokenizer-settings.png)

![Pestaña All del LLM de Agent Canvas en el primer uso, con el cuerpo adicional de LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

La configuración del LLM debería mostrar lo siguiente:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

El prefijo `openai/` le indica a LiteLLM que use el formato de solicitud compatible con OpenAI contra el endpoint de Lemonade.
El tokenizador personalizado es el tokenizador original de Hugging Face para el modelo GGUF; permite que OpenHands cuente los mismos tokens de la plantilla de chat que ve el servidor del modelo local.
El formulario actual del LLM de primer uso no muestra configuraciones de condensador.
Si tu compilación de Agent Canvas expone configuraciones de condensador más adelante en **Settings > LLM**, usa `llm_summarizing` y configura el máximo de tokens por debajo de la ventana de contexto de Lemonade, por ejemplo `56000`.

## 5. Instalar los servidores MCP de GitHub y Slack

En la interfaz de usuario de Agent Canvas, abre **Customize** (o **Settings > MCP**) para agregar los servidores MCP que le dan al agente herramientas para GitHub y Slack.
Los valores de los tokens se envían únicamente a tu Agent Server local y se conservan como configuraciones cifradas.

<!-- @os:windows -->
> **Windows (Docker):** los comandos del servidor MCP de `npx` a continuación se ejecutan dentro del contenedor, que ya incluye Node.js, por lo que no se instala nada adicional en el host.
> Debido a que `.openhands` está montado, los servidores MCP y sus tokens persisten entre reinicios del contenedor.
<!-- @os:end -->

### Servidor MCP de GitHub

Agrega un nuevo servidor MCP con esta configuración:

| Campo | Valor |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = tu token de GitHub |

Usa un token de GitHub con acceso de lectura al repositorio que quieras resumir.

### Servidor MCP de Slack

Agrega un segundo servidor MCP con esta configuración:

| Campo | Valor |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = el ID de tu canal de resumen |

Configura `SLACK_CHANNEL_IDS` con el ID del canal de resumen (el mismo valor que `SLACK_DIGEST_CHANNEL`) para que el agente no necesite recorrer todos los canales de Slack.

Después de agregar ambos servidores, usa el botón **Test** en cada uno para confirmar que se conecta y anuncia sus herramientas.
El servidor de GitHub debería listar herramientas de GitHub, y el servidor de Slack debería listar herramientas de Slack.

![Página de MCP de Agent Canvas con los servidores de GitHub y Slack instalados](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Crear la automatización del resumen

En la interfaz de usuario de Agent Canvas, abre la página **Automations** y crea una nueva automatización:

1. Elige **Create automation** y selecciona el tipo **Prompt preset**.
2. Configura el **Name** como `GitHub Development Digest to Slack`.
3. Configura el **Prompt** con el siguiente texto, reemplazando los marcadores de posición del repositorio y del canal con tus valores:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Configura el **Trigger** como **Cron** con el horario `0 9 * * 1-5` (9 a. m. los días laborables) y configura la **Timezone** con tu zona horaria, por ejemplo `America/New_York`.
5. Configura el **Timeout** en `900` segundos.
6. Guarda la automatización.

La página de detalles de la automatización muestra la nueva automatización con su disparador cron y el punto de entrada generado del preset del prompt.

![Página de detalles de la automatización de Agent Canvas después de su creación](assets/05-automation-created.png)
## 7. Prueba la automatización

Desde la página de detalle de la automatización en la Agent Canvas UI:

1. Haz clic en **Run now** (o **Dispatch**) para ejecutar la automatización una vez de inmediato.
2. Observa la lista de ejecuciones en la misma página. La ejecución más reciente debería pasar a `COMPLETED`.
3. Abre tu canal de Slack de destino. Debería contener el resumen generado.

No necesitas esperar a que se active el cron schedule—**Run now** activa una ejecución bajo demanda para que puedas confirmar que el prompt, las conexiones MCP y la publicación en Slack funcionan antes de depender de la programación.

![Ejecución de automatización de Agent Canvas completada correctamente](assets/06-automation-run-completed.png)

![Canal de Slack mostrando el resumen de OpenHands generado](assets/07-slackbot-message.png)

## Solución de problemas

<!-- @os:windows -->
- **El puerto 8000 de Docker ya está en uso:** asigna un puerto de host diferente, por ejemplo `docker run ... -p 8080:8000 ...`, y abre `http://localhost:8080/canvas`.
- **`docker pull` falla con un error de credenciales** (por ejemplo, "A specified logon session does not exist"): ejecuta el pull desde una sesión interactiva de Windows, o descarga previamente la imagen. La imagen es pública, por lo que no se requiere `docker login`.
- **La UI carga pero el backend no está saludable:** el primer lanzamiento construye el entorno del Agent Server dentro del contenedor. Espera un minuto y actualiza, luego revisa `docker logs <container>` para ver el progreso.
- **Agent Canvas no puede comunicarse con Lemonade desde el contenedor:** configura la **Base URL** del LLM como `http://host.docker.internal:13305/api/v1` (no `127.0.0.1`), y confirma que Lemonade se esté ejecutando en el host de Windows.
<!-- @os:end -->

- **Lemonade está caído:** reinícialo con el comando `lemonade run "${LEMONADE_MODEL}"` del paso 1, luego vuelve a ejecutar la verificación de salud.
- **`npm install -g` falla con un error de permisos:** en Linux o WSL, configura un directorio global de npm propiedad del usuario, agrégalo al archivo de inicio de tu shell, luego instala Agent Canvas nuevamente:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Si usas `zsh`, agrega la misma línea `export PATH=...` a `~/.zshrc` en lugar de `~/.bashrc`.
- **Agent Canvas rechaza la configuración del LLM después de establecer `custom_tokenizer`:** instala `transformers` en el entorno Python del Agent Server, reinicia Agent Canvas si es necesario, y vuelve a intentar guardar la configuración del LLM. OpenHands requiere Transformers para cargar la plantilla de chat del tokenizador cuando se establece `custom_tokenizer`.
- **Agent Canvas no puede comunicarse con Lemonade:** verifica `curl -fsS "${LEMONADE_BASE_URL}/health"` y confirma que la base URL ingresada en el formulario de LLM del primer uso o en **Settings > LLM** coincida con el endpoint local en ejecución o el túnel HTTPS.
- **La configuración del LLM no se guardó:** asegúrate de haber hecho clic en **Next** después de ingresar los valores. Vuelve a abrir **Settings > LLM** para confirmar que los valores se guardaron.
- **GitHub MCP no puede ver repositorios privados:** confirma que el token de GitHub tenga acceso de lectura al repositorio de destino y que el botón **Test** de MCP en **Customize** muestre las herramientas de GitHub.
- **Slack puede leer canales pero no puede publicar:** invita a la aplicación de Slack al canal de destino y confirma que el bot tenga `chat:write`.
- **La automatización lista demasiados canales de Slack:** usa un ID de canal de Slack y establece `SLACK_CHANNEL_IDS` en el servidor MCP de Slack en **Customize**.
- **La ejecución de la automatización falla o excede el contexto:** confirma que Lemonade se haya iniciado con `ctx_size=65536`, confirma que el LLM de OpenHands tenga `custom_tokenizer` establecido, y usa un repositorio explícito con los conjuntos de resultados de GitHub limitados a entre 3 y 5 elementos. Si tu compilación de Agent Canvas expone configuraciones de condenser, establece el máximo de tokens del condenser por debajo de la ventana de contexto de Lemonade.

## Próximos pasos

- Agrega un resumen semanal solo de lanzamientos.
- Agrega una automatización activada por eventos de GitHub para alertas más rápidas de PR o push.
- Enruta el mismo resumen hacia Notion, Linear u otra herramienta compatible con MCP.

## Recursos

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentación de Lemonade Server](https://lemonade-server.ai/docs)
- [Repositorio de extensiones de OpenHands](https://github.com/OpenHands/extensions)
- [Servidores del Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paquete Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->