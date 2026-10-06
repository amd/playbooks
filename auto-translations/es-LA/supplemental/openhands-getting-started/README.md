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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Descripción general

[OpenHands](https://github.com/All-Hands-AI/OpenHands) es un agente de software con IA
que puede escribir código, ejecutar comandos, navegar por la web y editar archivos en un
espacio de trabajo real. En lugar de copiar sugerencias de una ventana de chat, apuntas al
agente hacia una carpeta de proyecto y dejas que haga el trabajo: implementar una
característica, corregir un error, escribir pruebas o explicar una base de código.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) es la interfaz de navegador
recomendada para ejecutar OpenHands. Un solo comando `agent-canvas` inicia el servidor
del agente, el backend de automatización y el frontend web juntos, de modo que puedes
mantener una conversación con el agente desde tu navegador.

Para mantener todo en tu sistema AMD, el agente se comunica con un modelo local servido
por Lemonade Server. Lemonade expone ese modelo a través de una API compatible con
OpenAI, de modo que Agent Canvas puede configurarlo como cualquier otro endpoint estilo
OpenAI, mientras que el modelo, tu código y el contexto de la conversación permanecen
en tu máquina.

En este playbook, iniciarás un modelo local, abrirás Agent Canvas, lo apuntarás hacia ese
modelo y ejecutarás tu primera tarea de codificación contra una carpeta de proyecto real.

## Lo Que Aprenderás

- Cómo iniciar Lemonade Server y confirmar que un modelo local responde solicitudes de chat
- Cómo instalar y abrir Agent Canvas desde el paquete npm
- Cómo configurar Agent Canvas para usar un modelo local de Lemonade como LLM
- Cómo iniciar una conversación de OpenHands y observar al agente editar archivos y
  ejecutar comandos en un espacio de trabajo
- Cómo revisar lo que el agente cambió y guiarlo con mensajes de seguimiento

## Conceptos Básicos

| Concepto | Qué es | Dónde encaja en este playbook |
| --- | --- | --- |
| Lemonade Server | Una plataforma local de servicio de LLM creada para hardware AMD que expone una API compatible con OpenAI. Tus datos nunca salen de tu máquina. | Ejecuta el modelo que impulsa al agente. |
| OpenHands | Un agente de software con IA que lee y edita archivos, ejecuta comandos de shell y navega por la web dentro de un espacio de trabajo. | El agente que controlas desde el chat. |
| Agent Canvas | La interfaz de navegador y el backend que ejecuta las conversaciones de OpenHands y muestra las llamadas a herramientas y los cambios de archivos. | Inicia la pila y aloja tu conversación. |
| Espacio de trabajo | La carpeta de proyecto que el agente tiene permitido leer y modificar. | El objetivo de las ediciones y comandos del agente. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Los flujos de trabajo de agentes de codificación se benefician de un modelo más grande y
> una ventana de contexto mayor. Usa al menos 32 GB de memoria del sistema, y preferentemente
> 64 GB o más para modelos GGUF más grandes.
<!-- @device:end -->

## Configuración de la Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Buscar Actualizaciones de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Requisitos Previos


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Necesitas:

- Lemonade Server instalado y con capacidad de servir el modelo a continuación.

<!-- @os:linux -->
- Node.js 22.12 o posterior y `npm` (usado por el CLI de `agent-canvas`).
- `uv`, el administrador de paquetes de Python que usa Agent Canvas para gestionar el
  entorno del servidor del agente. Si tu sistema aún no lo tiene, instálalo desde la
  [guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/)
  antes de abrir Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  instalado y en ejecución. En Windows, la pila de Agent Canvas se ejecuta a partir de la
  imagen de Docker publicada, que incluye Node.js, `uv` y el paquete
  `@openhands/agent-canvas`, por lo que no necesitas instalarlos en el host.
<!-- @os:end -->

- Una carpeta de proyecto en la que trabajar. Puede ser cualquier repositorio git local o
  directorio de código en el que quieras que trabaje el agente.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Iniciar Lemonade Server

Inicia el modelo desde el CLI de Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Elige un modelo que se ajuste a tu hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) es un
> modelo de codificación potente, pero necesita un grupo de memoria grande. Si tu dispositivo
> tiene memoria o VRAM de GPU limitada, elige en su lugar un modelo GGUF más pequeño de la
> biblioteca de modelos de Lemonade, y usa ese ID de modelo en todo este playbook.

> **Nota:** El primer `lemonade run` descarga el modelo si aún no está presente, lo cual
> puede tardar un tiempo según el tamaño del modelo y tu conexión.

Lemonade expone una API compatible con OpenAI en:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Verificar el Modelo Local

Confirma que Lemonade puede servir el modelo seleccionado:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Luego envía una pequeña solicitud de chat:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. Instalar e iniciar Agent Canvas

<!-- @os:linux -->
Instala el paquete publicado de Agent Canvas de forma global:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Luego inicia la pila completa desde una terminal:

```bash
agent-canvas
```

Por defecto, Agent Canvas se inicia en `http://localhost:8000`. Abre esa URL en
tu navegador. El puerto no es especial: si el 8000 ya está en uso, indica
cualquier puerto libre con `--port` (o `-p`) al iniciar Agent Canvas:

```bash
agent-canvas --port 3000
```

Luego abre `http://localhost:3000` en su lugar. El backend local predeterminado debería
mostrarse como saludable en la pantalla de inicio.

El comando `agent-canvas` inicia el servidor del agente, el backend de
automatización y el frontend web juntos. Solo necesitas este comando para
ejecutar OpenHands localmente.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
En Windows, ejecuta la imagen de contenedor publicada de Agent Canvas con Docker Desktop.
La imagen incluye el Agent Server, el backend de automatización y el frontend web, por lo que
no necesitas instalar Node.js, `uv` ni la CLI en el equipo anfitrión.

Primero, crea las carpetas de configuración y espacio de trabajo que el contenedor monta:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Descarga la imagen publicada (es pública, por lo que no se requiere inicio de sesión):

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

Abre `http://localhost:8000/canvas` en tu navegador. Si el puerto 8000 ya está en
uso, asigna un puerto de host diferente, por ejemplo `-p 8080:8000`, y abre
`http://localhost:8080/canvas` en su lugar.

> **Nota:** El primer inicio inicializa el Agent Server dentro del contenedor,
> por lo que puede tardar uno o dos minutos antes de que el backend se reporte como saludable.

El montaje `.openhands` conserva tu perfil de LLM y configuración entre
reinicios del contenedor. El resto de esta guía configura todo a través de la
interfaz de Agent Canvas en tu navegador.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. Configurar el LLM local

En el primer inicio, Agent Canvas abre un flujo de incorporación. En ese flujo:

1. Mantén **OpenHands** seleccionado como agente y haz clic en **Next**.
2. En **Set up your LLM**, selecciona **Advanced**.
3. Mantén **Authentication** configurado como **API key**.
4. Establece **Custom Model** en `openai/Qwen3.6-35B-A3B-GGUF`.
5. Establece **Base URL** en `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > En Windows la pila se ejecuta en un contenedor, que no puede acceder al host en
   > `127.0.0.1`. Usa `http://host.docker.internal:13305/api/v1` en su lugar para que
   > el agente en contenedor pueda acceder a Lemonade ejecutándose en el host de Windows.
   <!-- @os:end -->
6. En **API Key**, ingresa cualquier marcador de posición no vacío, como `lemonade-local`.
   Lemonade no requiere una clave real, pero el cliente de OpenHands necesita un valor
   para enviar.
7. Haz clic en **Next**.

La configuración avanzada completa debería verse así. El campo de la clave de API
está oculto por la interfaz.

![Configuración avanzada de LLM en el primer uso de Agent Canvas con el modelo Lemonade y la URL base local](assets/01-llm-advanced-settings.png)

Agent Canvas guarda estos valores como un perfil de LLM. Si tu versión te pide que
nombres ese perfil, usa un nombre sin espacios como `lemonade-local`. Si cambias
de modelo más adelante, abre **Settings > LLM** y actualiza los mismos campos avanzados. Puedes
cambiar entre perfiles guardados desde el campo de chat con el comando `/model`.

## 5. Abrir un espacio de trabajo

El agente solo puede leer y modificar archivos dentro de un espacio de trabajo que elijas. Antes de
comenzar una tarea, indica a Agent Canvas la carpeta de tu proyecto:

1. Desde la pantalla de inicio, elige **Open Workspace**.
2. Selecciona la carpeta que contiene tu proyecto (por ejemplo, un repositorio git
   en el que quieras que trabaje el agente).
3. Inicia una nueva conversación en ese espacio de trabajo.

Todo lo que hace el agente—leer archivos, ejecutar comandos, editar código—se
limita a ese espacio de trabajo.

![Pantalla de inicio de Agent Canvas después de la incorporación](assets/02-agent-canvas-home.png)

## 6. Ejecuta tu primera tarea de codificación

Con el espacio de trabajo abierto y el LLM local seleccionado, escribe una tarea concreta en
el chat. Una buena primera tarea es pequeña y verificable, por ejemplo:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observa la línea de tiempo de la conversación. OpenHands hará lo siguiente:

- Leerá el espacio de trabajo para comprender su estructura.
- Creará `hello.py` con la función solicitada y el bloque de prueba.
- Opcionalmente ejecutará `python3 hello.py` para verificar el resultado.
- Informará lo que hizo y cualquier salida de comando en el chat.

Deberías ver el nuevo archivo aparecer en el espacio de trabajo, y el mensaje final del agente
debería describir el cambio que realizó. Este es el momento decisivo: el
agente escribió y ejecutó código real en la carpeta de tu proyecto.

## 7. Revisa y guía al agente

Después de que el agente termine un paso, revisa su trabajo antes de aceptar el siguiente:

- **Cambios en archivos**: usa el explorador de archivos del espacio de trabajo o la vista de diferencias
  del agente para ver exactamente qué se agregó, cambió o eliminó.
- **Salida de comandos**: expande cualquier comando que ejecutó el agente para ver stdout, stderr
  y el código de salida.
- **Seguimiento**: si el resultado no es lo que esperabas, responde en la misma
  conversación con una corrección. El agente mantiene el contexto previo y
  itera sobre los mismos archivos.

Por ejemplo, si la prueba no imprimió el saludo esperado, responde:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

El agente volverá a leer el archivo, ejecutará el comando, diagnosticará el problema y editará
el archivo nuevamente, todo en la misma conversación.
## Solución de problemas

<!-- @os:linux -->
- **`agent-canvas` no está en PATH:** reinstala con
  `npm install -g @openhands/agent-canvas` y confirma que el directorio binario global de npm
  esté en tu PATH antes de que `agent-canvas` pueda iniciarse desde una nueva
  terminal.
- **`npm install -g` falla con un error de permisos:** configura un directorio
  global de npm propiedad del usuario, luego vuelve a abrir la terminal e instala Agent Canvas de nuevo.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Falta `uv`:** instálalo desde
  [la guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas usa `uv` para gestionar el entorno Python del servidor del agente.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` o `docker run` no logra conectarse:** asegúrate de que Docker Desktop
  esté en ejecución (su ícono de ballena está en la bandeja del sistema) y que el motor haya
  terminado de iniciarse. `docker version` debería mostrar tanto una sección Client como una Server.
- **El contenedor se inicia pero el backend nunca se vuelve saludable:** el primer
  inicio inicializa el Agent Server dentro del contenedor; dale uno o
  dos minutos, luego revisa `docker logs <container>` en busca de errores.
- **El contenedor no puede alcanzar Lemonade:** el contenedor llega al host a través de
  `host.docker.internal`. Confirma que Lemonade esté sirviendo en el host de Windows con
  `lemonade status`, y usa `http://host.docker.internal:13305/api/v1` como la
  URL base al configurar el LLM.
<!-- @os:end -->

- **La UI carga pero el backend muestra estado no saludable:** espera uno o dos
  minutos a que el servidor del agente termine de iniciarse, luego actualiza. Si sigue sin
  estar saludable, reinicia la pila y revisa los registros en busca de errores.
- **Las solicitudes de chat de Lemonade fallan con un error de conexión:** confirma que
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` tenga éxito y que
  Lemonade siga sirviendo el modelo con `lemonade status`.
- **El agente produce un error de longitud de contexto o límite de tokens:** inicia una
  conversación nueva para que el agente no cargue un historial demasiado grande. Si
  sigue ocurriendo, reinicia Lemonade con un `ctx_size` mayor que el predeterminado de
  65536 (por ejemplo, `ctx_size=131072`), si la memoria lo permite.
- **El agente produce ediciones de baja calidad o incompletas:** cambia a un modelo
  más grande en Lemonade, o asígnale al agente una tarea más pequeña y concreta y deja que la
  termine antes de pedir el siguiente cambio.

## Próximos pasos

- Prueba una tarea más grande en el mismo espacio de trabajo, como agregar un archivo de prueba unitaria o
  corregir un error conocido, y revisa el diff del agente antes de conservar el cambio.
- Conecta un servidor MCP como GitHub o Slack en **Customize** para que
  el agente pueda leer incidencias o publicar actualizaciones mientras trabaja.
- Guarda varios perfiles de LLM (un modelo pequeño y rápido y un modelo grande y más potente) y
  alterna entre ellos con `/model` a mitad de la conversación.
- Continúa con [las automatizaciones de OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) para
  convertir bucles de desarrollo recurrentes en ejecuciones de agentes programadas o activadas por eventos.

## Recursos

- [Documentación de OpenHands](https://docs.openhands.dev/)
- [Resumen de Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuración de Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Perfiles de LLM y configuración de modelos](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentación de Lemonade Server](https://lemonade-server.ai/docs)

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