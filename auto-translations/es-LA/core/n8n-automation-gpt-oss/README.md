<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Resumen

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requiere un mínimo de **32GB** de memoria del sistema.
<!-- @device:end -->

n8n es una plataforma de automatización de flujos de trabajo que te permite conectar aplicaciones y servicios mediante un editor visual basado en nodos.

Este playbook te enseña cómo configurar un resumidor de noticias financieras impulsado por IA que extrae los últimos titulares de negocios de un feed RSS de noticias y usa un LLM local que se ejecuta en tu sistema para generar un resumen orientado a inversionistas.

## Qué aprenderás

- Cómo instalar e iniciar n8n
- Importar y configurar un flujo de trabajo prediseñado
- Conectarse a Lemonade usando la integración nativa de n8n
- Entender los nodos del flujo de trabajo y el flujo de datos

## ¿Qué es Lemonade?

[Lemonade](https://lemonade-server.ai) es una plataforma de servicio de LLM local construida para hardware AMD. Proporciona una API compatible con OpenAI que se ejecuta completamente en tu máquina; tus datos nunca salen de tu dispositivo.

En este playbook, usamos Lemonade para servir un LLM local al cual se conecta n8n para tareas impulsadas por IA.

n8n incluye un **nodo nativo de Lemonade** (`Lemonade Chat Model`) que proporciona una integración de primera clase, sin necesidad de configuración manual. Esto hace que conectar tu LLM local a flujos de trabajo de automatización sea sencillo.

<!-- @device:halo_box,halo,stx,krk -->
## Configuración de la memoria

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Buscar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


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
  "max_tokens": 32
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
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## Instalación de n8n
<!-- @os:windows -->
Instala n8n globalmente usando npm.

> **Nota**: Es posible que veas algunas advertencias de npm. Esto es esperado.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Consejo**: Es posible que los usuarios de Windows necesiten modificar su Política de Ejecución de PowerShell (por ejemplo,
> configurándola como RemoteSigned o Unrestricted) antes de ejecutar algunos comandos de Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problema con PATH**: Si `n8n --version` indica que el comando no se encuentra, asegúrate de que el directorio bin global de npm esté en el `PATH` del usuario. La ruta de instalación habitual es `C:\Users\<username>\AppData\Roaming\npm`.
> Agrega esto a la ruta del usuario (Editar las variables de entorno del sistema > Variables de entorno > Editar la ruta de usuario) y recarga la terminal.

<!-- @os:end -->

<!-- @os:linux -->
Ahora vamos a usar el servicio Podman para contenerizar nuestra instalación de n8n.

Por favor, descarga lo siguiente en un directorio de tu elección: [compose.yml](assets/compose.yml)

En ese directorio, ejecuta el siguiente comando:
```bash
podman compose up -d
```

Esto debería instalar n8n y escribir en un almacenamiento persistente.

Inicia n8n escribiendo `localhost:5678` en la barra de direcciones de tu navegador.
<!-- @os:end -->

<!-- @os:windows -->
## Iniciar n8n

Inicia n8n desde la terminal:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n inicia un servidor web local. Presiona `'o'` o abre tu navegador en `http://localhost:5678` para acceder al editor.
<!-- @os:end -->


> **Consejo**: Mantén abierta la ventana de la terminal mientras usas n8n. Cerrarla podría detener el servidor.

## Iniciar Lemonade

Lemonade es el servidor local que ejecutará un modelo y se conectará a n8n.

<!-- @os:linux -->
Abre la GUI de Lemonade haciendo clic en el ícono de Lemonade en la barra de tareas. Desde aquí puedes explorar modelos, backends y cargar los modelos preinstalados.
<!-- @os:end -->

<!-- @os:windows -->
Abre la GUI de Lemonade haciendo clic en el ícono de Lemonade. Haz clic derecho en el ícono de la bandeja para abrir la aplicación. Luego, puedes agregar modelos, backends y cargar los modelos preinstalados.
<!-- @os:end -->

>**Consejo**: Una vez en ejecución, la GUI de Lemonade también está disponible en http://localhost:13305

Alternativamente, puedes abrir una terminal y ejecutar `lemonade list` para ver qué modelos están instalados. Luego, ejecuta:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Configuración del flujo de trabajo

### Paso 1: Regístrate o inicia sesión en n8n

Cuando abras n8n por primera vez, se te pedirá que crees una cuenta o inicies sesión:

1. Abre `http://localhost:5678` en tu navegador
2. Crea una nueva cuenta local con tu correo electrónico, o inicia sesión si ya tienes una
3. Una vez que hayas iniciado sesión, verás el panel de n8n

> **Consejo**: Si quedas bloqueado fuera de tu cuenta, intenta `n8n user-management:reset`

### Paso 2: Importar el flujo de trabajo

Hemos proporcionado un flujo de trabajo prediseñado que puedes importar directamente:

1. Descarga el siguiente archivo de flujo de trabajo: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Haz clic en **Start from Scratch** para abrir el editor de flujos de trabajo. Alternativamente, haz clic en el botón + en la parte superior izquierda y luego en **Add workflow**.
3. Haz clic en el menú **...** (tres puntos) en la barra superior derecha y selecciona **Import from file**
4. Selecciona el archivo descargado `financial-news-workflow.json`
5. El flujo de trabajo aparecerá en el lienzo
### Paso 3: Entendiendo el Flujo de Trabajo

El flujo de trabajo importado contiene 8 nodos conectados:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nodo | Propósito |
|------|-----------|
| **When clicking 'Execute workflow'** | Disparador manual para iniciar el flujo de trabajo |
| **Fetch Financial News Feed** | Nodo RSS Read que obtiene los titulares de negocios más recientes de un feed RSS (por defecto usa el feed de NYT Business, no requiere clave de API) |
| **Aggregate Headlines** | Nodo Aggregate que recopila los títulos y resúmenes de los titulares de cada elemento del feed en una sola lista |
| **Clean Extracted News Data** | Nodo Set que combina todos los titulares en un solo campo de texto |
| **AI Financial News Summarizer** | AI Agent que procesa las noticias con un system prompt de analista financiero |
| **Lemonade Chat Model** | Se conecta a tu servidor local de Lemonade que ejecuta el LLM |
| **Structured Output Parser** | Da formato a la salida de la IA como JSON estructurado |
| **Convert to File** | Convierte el resumen en un archivo descargable |

> **Consejo**: Para usar una fuente de noticias diferente, haz doble clic en el nodo **Fetch Financial News Feed** y reemplaza la URL con cualquier feed RSS de negocios o mercados que prefieras.

### Paso 4: Configurar las Credenciales de Lemonade

Antes de ejecutar el flujo de trabajo, necesitas conectarlo a tu servidor local de Lemonade:

1. Haz doble clic en el nodo **Lemonade Chat Model** en n8n
2. En el menú desplegable **Credential to connect with** selecciona **Create New Credential**
3. Ingresa los valores de la siguiente tabla y haz clic en guardar.
4. Elige el modelo correspondiente que tengas cargado en Lemonade Server.

  | Campo | Valor |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Nota**: Antes de probar, ejecuta `lemonade status` en una terminal para confirmar que el servidor de Lemonade esté en funcionamiento.
<!-- @device:halo_box -->
> Este flujo de trabajo usa GPT-OSS-120B y viene preinstalado en Lemonade. Puedes cambiarlo a otros modelos cargados en la configuración del nodo Lemonade Chat Model.
<!-- @device:end -->

### Paso 5: Probar el Flujo de Trabajo

1. Asegúrate de que Lemonade esté en funcionamiento con un modelo cargado
2. Haz clic en **Execute workflow** en la parte inferior central del lienzo
3. Observa cómo cada nodo se ejecuta de izquierda a derecha—se ponen en verde al completarse
4. Haz doble clic en el nodo **AI Financial News Summarizer** para ver el resumen generado en el panel inferior.
5. Haz doble clic en el nodo **Convert to File** para descargar el archivo de texto correspondiente en el panel inferior.

## Entendiendo el AI Agent

El AI Financial News Summarizer usa un system prompt diseñado para el análisis financiero:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

El agente recibe los datos de noticias depurados y genera un resumen estructurado con el sentimiento del mercado.

### Guardando tu Flujo de Trabajo

Haz clic en el nombre del flujo de trabajo en la parte superior y renómbralo si lo deseas. Los flujos de trabajo se guardan automáticamente mientras trabajas.

## Próximos Pasos

- **Programar automatización**: Reemplaza el Manual Trigger con un **Schedule Trigger** para ejecutarlo diariamente
- **Enviar notificaciones**: Agrega un nodo de **Discord**, **Slack** o **Email** para recibir los resúmenes
- **Probar diferentes modelos**: Cambia el modelo en el nodo Lemonade Chat Model para experimentar con diferentes LLM
- **Cambiar la fuente de noticias**: Apunta el nodo **Fetch Financial News Feed** a un feed RSS diferente para seguir otras secciones o publicaciones
- **Probar diferentes backends**: n8n también es compatible con [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio y otros backends de LLM locales

### Explorar las Plantillas de n8n

n8n tiene cientos de plantillas de flujos de trabajo prediseñadas. Explora la biblioteca oficial de plantillas en:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Busca "AI", "LLM" o "automation" para encontrar flujos de trabajo que puedas importar y personalizar.

Para más información, consulta la [Documentación de n8n](https://docs.n8n.io/).

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