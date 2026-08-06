<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Ejecutar OpenClaw con Lemonade Server como backend

## Descripción general

[**OpenClaw**](https://openclaw.ai/) es un agente de IA autónomo que puede escribir y ejecutar código, administrar archivos y llevar a cabo tareas complejas de varios pasos en tu nombre. A diferencia de un asistente de chat que solo responde preguntas, OpenClaw realiza acciones reales en tu sistema, lo que significa que necesita un backend de IA rápido y capaz que pueda seguir el ritmo de un bucle de agente exigente.

[**Lemonade Server**](https://lemonade-server.ai/) es ese backend. Es un servidor de inferencia local de código abierto que ejecuta modelos de GenAI directamente en tu hardware y los expone a través de la API estándar de la industria de OpenAI.

Juntos, forman un stack de agente de IA completamente local: Lemonade se encarga de la inferencia del modelo y OpenClaw proporciona el bucle de agente que convierte las salidas del modelo en acciones reales.

> **Antes de continuar:** OpenClaw es un agente de IA altamente autónomo. Dar acceso a tu sistema a cualquier agente de IA puede generar resultados impredecibles o no deseados. Continúa solo si comprendes los riesgos y te sientes cómodo con software autónomo actuando en tu nombre.

---

## Lo que aprenderás

Al final de este playbook podrás:

- Aprender sobre **Lemonade Server**
- **Instalar OpenClaw** y **configurarlo para que apunte a Lemonade Server** como su backend de IA.
- **Iniciar el gateway de OpenClaw** y confirmar que tu agente está listo para trabajar.
- **Conectar un canal de comunicación** (Discord o Telegram) para poder chatear con tu agente desde cualquier dispositivo.

---

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar si hay actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

<!-- @os:linux -->
- Una PC con **Ubuntu 24.04+** o una distribución de Linux compatible basada en Debian con `apt-get`
- Al menos **12 GB de RAM** (se recomiendan 64 GB+ para modelos más grandes)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcional, para aislar OpenClaw en un sandbox)
- **~10–30 GB de espacio libre en disco** para los pesos del modelo
<!-- @os:end -->

<!-- @os:windows -->
- Una PC con **Windows 10/11**
- Al menos **12 GB de RAM** (se recomiendan 64 GB+ para modelos más grandes)
- **~10–30 GB de espacio libre en disco** para los pesos del modelo
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opcional, para aislar OpenClaw en un sandbox)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Descargar y cargar el modelo recomendado

El modelo recomendado para este playbook es **Qwen3.6-35B-A3B-GGUF** de Unsloth, un potente modelo MoE con una ventana de contexto de 263k tokens que es ideal para cargas de trabajo de agentes. Este modelo usa la cuantización UD-Q4_K_XL. Descárgalo ahora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Luego cárgalo con una ventana de contexto grande y guarda esa configuración para futuras ejecuciones:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

El modelo tiene una longitud de contexto predeterminada de 262,144 tokens. Si encuentras errores de falta de memoria (OOM), considera reducir la ventana de contexto. Sin embargo, dado que Qwen3.6 aprovecha el contexto extendido para tareas complejas, recomendamos mantener una longitud de contexto de al menos 128K tokens para preservar las capacidades de razonamiento.

> **Consejo: Desactiva el pensamiento para respuestas de agente más rápidas:** Qwen3.6-35B-A3B se ejecuta en modo de pensamiento de forma predeterminada, lo que añade latencia antes de cada respuesta. Para los bucles de agente, esta sobrecarga se acumula rápidamente. El repositorio [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) proporciona una configuración lista para usar que desactiva el pensamiento. Para usarla, descarga el archivo e impórtalo:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
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

## Configurar WSL

Ejecutamos OpenClaw dentro de WSL (Recomendado) y lo conectamos a Lemonade, que se ejecuta de forma nativa en Windows. Esto te brinda un entorno de shell de Linux para OpenClaw mientras mantienes la aceleración de GPU de Lemonade en el lado de Windows.

### Instalar WSL y Ubuntu

Abre PowerShell como Administrador e instala el kernel de WSL:

```powershell
wsl --install --no-distribution
```

Luego instala Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Habilitar systemd en WSL

Ejecuta esto dentro de la terminal de Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Sal de WSL y reinícialo:

```powershell
exit
wsl --shutdown
wsl
```

### Conectar Lemonade desde Windows a WSL

WSL2 se ejecuta en una red virtual. Lemonade en Windows se vincula a `127.0.0.1`, al cual WSL no puede acceder directamente. Un proxy de puerto de Windows reenvía el tráfico desde la IP de gateway de WSL hacia el localhost de Windows.

**Encuentra la IP de gateway de WSL** (ejecuta dentro de WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Agrega el proxy de puerto** (ejecuta en PowerShell como Administrador, reemplazando `<WSL-Gateway-IP>` con tu IP de gateway de WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Nota: Si encuentras un error `netsh: command not found`, intenta usar el nombre explícito del ejecutable en su lugar - `netsh.exe`

**Agrega una regla de firewall** (en el mismo PowerShell elevado):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifica desde WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Si ya cargaste el modelo Qwen3.6-35B-A3B-GGUF en el paso anterior, deberías ver una salida JSON como esta:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### Cómo mantener el puente funcionando después de reiniciar

La regla `netsh portproxy` sobrevive a los reinicios, pero la IP del gateway de WSL puede cambiar después de ejecutar `wsl --shutdown` o reiniciar el equipo. Cuando esto sucede, el proxy sigue apuntando a la IP anterior y Lemonade deja de estar accesible desde WSL. Si eso ocurre, usa una de las opciones a continuación.

**Opción 1 (recomendada) — Reparar el puente automáticamente.** Para evitar hacer esto manualmente cada vez, usa una tarea programada que verifique el puente en cada inicio de sesión e inicio del sistema, y lo reconstruya solo cuando la IP del gateway haya cambiado. Consulta la [guía de reparación automática del puente de Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Opción 2 — Reparar el puente manualmente.** Primero, obtén la IP actual del gateway de WSL ejecutando esto dentro de WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Copia este valor; lo usarás en lugar de `<new-WSL-Gateway-IP>` a continuación.

Luego, en una **PowerShell elevada** (Ejecutar como administrador), lista las reglas existentes, elimina solo la regla obsoleta de Lemonade y agrega una nueva con la IP actual:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

En la salida de `show all`, la regla obsoleta de Lemonade es la entrada cuya dirección de conexión es `127.0.0.1` en el puerto `13305`; su dirección de escucha es tu `<old-WSL-Gateway-IP>`. Al eliminar por esa dirección, se elimina únicamente esta regla y se mantienen intactas las demás reglas de port-proxy en tu equipo.

La regla del firewall que agregaste durante la configuración está vinculada al puerto `13305` (no a la IP), por lo que sigue funcionando y no es necesario volver a crearla.

> **Recomendación:** Para evitar problemas con el gateway, sugerimos firmemente la siguiente configuración de shell:
> - Los **comandos de Windows** deben ejecutarse en **PowerShell**
> - Los **comandos de la distro de WSL** deben ejecutarse en un **Símbolo del sistema** (ejecutado como **Administrador**)

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Instalar y configurar OpenClaw

### Instalar OpenClaw
<!-- @os:windows -->
> Ejecuta los comandos de esta sección dentro de tu **terminal de WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

La bandera `--no-onboard` omite el asistente de configuración interactivo; configurarás el backend del modelo manualmente en el siguiente paso, lo cual te da un control preciso sobre qué modelo y servidor se utilizan.

Abre una nueva terminal y confirma la instalación:

```bash
openclaw --version
```

> **Consejo:** Si ves `command not found` después de la instalación, agrega el directorio bin global de npm a tu PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Para que esto sea permanente, agrega la línea anterior a tu archivo `~/.bashrc` o `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Configurar OpenClaw para usar Lemonade

Ejecuta el proceso de incorporación no interactivo de OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Este comando escribe la configuración de OpenClaw en `~/.openclaw/openclaw.json`.

> **Dimensionamiento de la ventana de contexto de OpenClaw:** La compactación de OpenClaw se activa cuando `contextTokens > contextWindow − reserveTokens`. El valor predeterminado de `reserveTokensFloor` es 20,000 tokens, un piso que anula `reserveTokens` cuando este es menor, por lo que cualquier contexto de modelo por debajo de ~37k activará un bucle infinito de compactación. Establece una reserva baja y desactiva el piso una vez en tu configuración, y se aplicará a todos los modelos, sin necesidad de ajustes por modelo:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` es un *piso* (protección mínima), no la reserva en sí; establecer solo el piso no tiene efecto. `reserveTokensFloor: 0` desactiva la protección para que se acepte el valor menor de `reserveTokens`.
>
> **Cuándo aplicar esto:** Usa esta configuración si la ventana de contexto efectiva de tu modelo está por debajo de ~37k, ya sea porque el modelo es pequeño (p. ej., 8k, 16k, 32k) o porque la has limitado intencionalmente a un valor menor (p. ej., cargar un modelo de 128k pero establecer el contexto en 16k en Lemonade). Sin esto, OpenClaw entra en un bucle infinito de compactación al iniciar.
>
> **Modelos con contexto grande a contexto completo:** Puedes omitir esto por completo. Los valores predeterminados funcionan bien; la compactación se activará mucho antes de que se llene la ventana y el modelo tendrá amplio espacio para generar respuestas largas. Si igualmente lo aplicas, ten en cuenta que `reserveTokens: 4096` limita la longitud de la respuesta a ~4k tokens, lo que puede cortar la generación de archivos largos o planes detallados.
>
> **Dónde agregar esto:** Coloca el bloque `compaction` dentro de `agents.defaults` en tu `openclaw.json` (generalmente en `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> El resto de tu configuración (gateway, channels, models, etc.) permanece sin cambios; solo es necesario agregar la clave `compaction`.
### (Recomendado) Habilitar el Sandboxing de Docker

OpenClaw puede enrutar todas las operaciones de archivos y código del agente a través de un contenedor Docker aislado en lugar de ejecutarlas directamente en tu host. Esto limita el radio de impacto de cualquier acción no intencionada al sandbox, dejando intactos el sistema de archivos y la red de tu host.

Compila la imagen del sandbox una vez (Docker debe estar instalado):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Ejecuta esto para agregar la clave `sandbox` dentro del bloque existente `agents.defaults` en `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Los contenedores del sandbox **no tienen acceso a la red** de forma predeterminada. Consulta la [referencia de sandboxing](https://docs.openclaw.ai/gateway/sandboxing) para montajes de enlace y anulaciones de red.

> #### Solución de problemas: Permiso denegado en Docker
> 
> Si obtienes "permission denied" al ejecutar comandos de Docker:
> 
> **Paso 1: Agrega tu usuario al grupo docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Paso 2: Si el error persiste, aplica la solución permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Luego **reinicia** tu sistema.
> 
> **Solución temporal rápida** (se restablece después de reiniciar):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (Recomendado) Integración de OpenClaw con los Servicios de Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) ofrece un servicio autoalojado de rastreo web y extracción de contenido que puede superar estos desafíos y desbloquear todo el potencial de la automatización de OpenClaw. 

En esta configuración, OpenClaw se ejecuta como un conjunto de contenedores Docker administrados con Podman. Para simplificar la gestión del ciclo de vida y el inicio automático, registramos Firecrawl como un servicio `systemd` a nivel de usuario que orquesta la pila subyacente de Podman Compose. Esto permite que OpenClaw inicie el gateway, lo detenga y verifique el servicio de Firecrawl usando comandos estándar `systemctl --user` en lugar de interactuar directamente con los contenedores. 

Para mantener las cosas simples, hemos dividido todo el proceso en cuatro pasos:

---

### 1. Registrar el servicio del sistema
Navega al directorio de configuración de usuario de systemd:
```bash
cd ~/.config/systemd/user
```
Crea y abre un nuevo archivo llamado `firecrawl.service`.
```bash
nano firecrawl.service
```
Copia y pega la siguiente configuración:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
En este punto, el servicio ha sido definido pero aún no registrado con `systemd`. 
Asegúrate de que el nombre de archivo coincida exactamente con el que creaste arriba, luego ejecuta:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Si tiene éxito, deberías ver la siguiente salida:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contiene enlaces simbólicos a servicios configurados para iniciarse automáticamente.

### 2. Configurar Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) es ideal para quienes necesitan control total sobre sus entornos de scraping y procesamiento de datos, pero conlleva la contrapartida de esfuerzos adicionales de mantenimiento y configuración.

Comienza clonando el repositorio:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crea `.env` en el directorio raíz `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Desplegar OpenClaw con Podman Compose

Antes de continuar, asegúrate de haber descargado la imagen Docker más reciente de OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Una vez hecho esto, descarga el archivo Compose de OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) y colócalo en el directorio raíz `/firecrawl`:

> Esta convención es necesaria para que `systemd` pueda localizar e iniciar el servicio correctamente, tal como se especifica en `WorkingDirectory=${HOME}/firecrawl`.

> Siempre puedes ampliar la pila agregando servicios adicionales de Firecrawl según sea necesario. La lista completa de servicios disponibles se encuentra en el [docker-compose.yaml oficial de Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Iniciar el servicio de OpenClaw a través de Firecrawl 

Antes de entregar el control a `systemd`, valida que todo funcione correctamente ejecutando la pila manualmente:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Si todo está configurado correctamente, deberías ver que el contenedor de OpenClaw se levanta y la salida de tu línea de comandos debería verse similar a esto:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Una vez verificado, baja la pila antes de continuar:
```bash
podman compose -f openclaw-compose.yaml down
```
Antes de iniciar el servicio, debes asegurarte de que se establezcan la propiedad y los permisos correctos en el directorio `firecrawl` y su archivo `.env`. 
Esto es esencial para que el servicio pueda escribir tus credenciales al inicio.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Ahora que todo está validado, inicia el servicio a través de `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Las Acciones de OpenClaw](https://docs.openclaw.ai/) son accesibles desde dentro del contenedor interactivo, y el Panel Web está disponible en el mismo host y puerto en http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Obtener tu `OPENCLAW_GATEWAY_TOKEN`

Una vez que el servicio esté en funcionamiento, notarás un nuevo directorio `.openclaw` creado en tu carpeta de inicio (~/.openclaw). Este directorio está bloqueado de forma predeterminada, por lo que deberás desbloquearlo para recuperar tu token de gateway.

1. Otorga acceso al directorio:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lee tu token de gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Ubica el valor `OPENCLAW_GATEWAY_TOKEN` en la salida.

3. Abre el panel del gateway en tu navegador http://127.0.0.1:18789. Pega tu token cuando se te solicite autenticarte.

Para detener el servicio, ejecuta:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Iniciar el gateway de OpenClaw

El gateway es el proceso de OpenClaw que gestiona el ciclo del agente y sirve el panel de control:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Para abrir el panel de control, ejecuta esto en una segunda terminal mientras el gateway sigue en ejecución:

```bash
openclaw dashboard
```

Dado que el gateway se vincula a loopback, el panel de control se autentica automáticamente cuando se abre desde la misma máquina, no se necesita ingresar un token ni aprobar el dispositivo para el acceso local. Deberías ver el panel de control de OpenClaw con tu modelo de Lemonade listado como el backend activo.

> Si has habilitado el sandboxing, puedes verificarlo pidiéndole al agente que ejecute `run hostname` desde el panel de control. Si ves un ID de contenedor corto en lugar del nombre de host de tu máquina, el sandbox está funcionando.

**Felicidades, has construido una pila de agente de IA completamente local desde cero.**

> **¿Necesitas el token del gateway?** Ejecuta `openclaw dashboard --no-open` para imprimir la URL del panel de control con el token incrustado (también intenta copiarlo a tu portapapeles). Alternativamente, el token está en `gateway.auth.token` dentro de `~/.openclaw/openclaw.json`.

**Acceder al panel de control desde otro dispositivo (a través de un túnel SSH)**

Si OpenClaw se ejecuta en una máquina remota, puedes acceder a su panel de control desde tu máquina local a través de un túnel SSH. El túnel reenvía el puerto del gateway (`18789`) para que tu navegador local pueda comunicarse con el gateway remoto a través de `127.0.0.1`.

1. Desde tu **máquina local**, conéctate a la máquina remota una vez y acepta el mensaje de huella digital para que el host se agregue a tus hosts conocidos:

   ```bash
   ssh user@<host-ip>
   ```

2. Aún en tu **máquina local**, abre el túnel SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Nota:** Después de ingresar tu contraseña, la terminal no muestra ninguna salida y parece quedarse colgada. Esto es esperado: la bandera `-N` le indica a SSH que no ejecute ningún comando remoto, por lo que simplemente mantiene el túnel abierto. Deja esta terminal en ejecución.

3. En tu **máquina local**, abre un navegador y ve a `http://127.0.0.1:18789`.

4. En la **máquina remota**, imprime el token del gateway y pégalo en el navegador para iniciar sesión:

   ```bash
   openclaw dashboard --no-open
   ```

   Esto imprime la URL del panel de control con el token incrustado; copia el token para iniciar sesión. (El token también se almacena en `gateway.auth.token` dentro de `~/.openclaw/openclaw.json`).

> **Aprobar un dispositivo remoto:** Cuando abres el panel de control desde otra máquina o teléfono, el navegador puede mostrar un ID de solicitud. En la **máquina remota**, lista las solicitudes pendientes:
> ```bash
> openclaw devices list
> ```
> Luego aprueba la solicitud correspondiente:
> ```bash
> openclaw devices approve <requestId>
> ```
> Esto solo es necesario para dispositivos remotos o secundarios; el acceso por loopback desde la misma máquina se autentica automáticamente. Consulta la documentación de [Acceso remoto](https://docs.openclaw.ai/gateway/remote) para más detalles.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcional: Conectar un canal de comunicación

Una vez que el gateway está en ejecución, puedes acceder a tu agente local desde cualquier dispositivo. Elige la opción que se adapte a tu configuración. OpenClaw es compatible con [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), y otros canales; consulta la lista completa en [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opción A: Discord

Discord requiere un servidor donde **tengas acceso de administrador** para agregar un bot. Si compartes servidores pero no eres dueño de ninguno, usa la Opción B (Telegram) en su lugar.

#### Crear una cuenta y un servidor de Discord

Si no tienes una cuenta de Discord, regístrate en [discord.com](https://discord.com). También necesitas un servidor donde seas administrador; crea uno haciendo clic en el ícono **+** en la barra lateral de Discord y seleccionando **Create My Own**. Un servidor privado está bien.

#### Crear una aplicación y un bot de Discord

1. Ve al [Discord Developer Portal](https://discord.com/developers/applications) y haz clic en **New Application**. Dale un nombre (por ejemplo, "openclaw-bot").
2. En la barra lateral, haz clic en **Bot**. Configura un nombre de usuario para el bot.
3. Aún en la página de Bot, desplázate hasta **Privileged Gateway Intents** y habilita:
   - **Message Content Intent** (obligatorio)
   - **Server Members Intent** (recomendado)
4. Vuelve a desplazarte hacia arriba y haz clic en **Reset Token** para generar el token de tu bot. Cópialo.

#### Agregar el bot a tu servidor

1. En la barra lateral, haz clic en **OAuth2/ URL Generator**.
2. En **Scopes**, habilita `bot` y `applications.commands`.
3. En **Bot Permissions**, habilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia la URL generada, pégala en tu navegador, selecciona tu servidor y confirma. El bot debería aparecer ahora en la lista de miembros de tu servidor.

#### Recopilar tus IDs

Habilita el modo desarrollador en Discord (**User Settings/ Advanced/ Developer Mode**) y luego:
- Haz clic derecho en el ícono de tu servidor: **Copy Server ID**
- Haz clic derecho en tu propio avatar: **Copy User ID**

#### Permitir mensajes directos de los miembros del servidor

Haz clic derecho en el ícono de tu servidor/ **Privacy Settings**/ activa **Direct Messages**. Esto permite que el bot te envíe mensajes directos, lo cual es necesario para el paso de emparejamiento.

#### Configurar OpenClaw para Discord

Guarda el token de tu bot como una variable de entorno, luego crea un único archivo de parche que habilite Discord, haga referencia al token y agregue tu servidor a la lista de permitidos. Reemplaza `<server_id>` y `<user_id>` con los IDs recopilados anteriormente.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **No te bases en pedirle al agente que configure esto.** Cuando el sandboxing está habilitado, el agente no puede escribir en `~/.openclaw/openclaw.json` desde dentro del sandbox; usa en su lugar los comandos de la CLI mencionados anteriormente en el host.

Reinicia el gateway para que tome la nueva configuración del canal:

```bash
openclaw gateway run --bind loopback --port 18789
```

Deberías ver `logged in to discord as <bot-name>` en la salida del gateway en cuestión de segundos.
#### Vincula tu cuenta de Discord

Envía un DM al bot en Discord. Este responderá con un código de emparejamiento corto.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Apruébalo en la máquina que ejecuta OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Los códigos de emparejamiento expiran después de una hora.

Ahora puedes chatear con tu agente directamente desde Discord y delegar tareas a tu hardware local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opción B: Telegram

Telegram es más simple que Discord para la mayoría de los usuarios, no requiere servidor ni acceso de administrador.

#### Crea un bot de Telegram

1. Abre Telegram y envía un mensaje a **@BotFather**.
2. Envía `/newbot` y sigue las instrucciones. Guarda el token del bot que te proporciona.

#### Configura OpenClaw para Telegram

Guarda el token como una variable de entorno:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Agrega la configuración del canal a `~/.openclaw/openclaw.json` (o actualízala mediante el panel de control):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Reinicia el gateway y luego envía cualquier mensaje a tu bot en Telegram. Aprueba el emparejamiento:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Los códigos de emparejamiento expiran después de una hora. Ahora puedes chatear con tu agente mediante DM en Telegram.

---

## Próximos pasos

Ahora que tu agente puede recibir comandos desde tu teléfono y actuar en tu máquina local, aquí tienes tres direcciones que vale la pena explorar:

1. **Resumidor del mercado bursátil**: Programa OpenClaw para obtener datos de APIs financieras en un intervalo fijo, resumir los movimientos del día con tu modelo local y enviar un resumen a tu teléfono cada mañana mediante el canal que elijas.

2. **Monitor de ajuste fino**: Inicia un trabajo de entrenamiento de forma remota mediante Telegram o Discord, y haz que el agente siga el registro de entrenamiento y reporte valores periódicos de pérdida, uso de GPU y uso de disco de vuelta a tu teléfono. Si la ejecución se detiene o la VRAM se dispara, te enteras de inmediato sin necesidad de estar frente a la máquina.

3. **IOT con un VLM local**: Apunta una cámara hacia la puerta de tu casa, ejecuta un modelo de visión en Lemonade y haz que OpenClaw analice los fotogramas a demanda o mediante un disparador. Pregunta "¿llegó algún paquete hoy?" desde tu teléfono y obtén una respuesta directa desde tu propio hardware.

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