<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Ejecutar OpenClaw con Lemonade Server como backend

## Descripción general

[**OpenClaw**](https://openclaw.ai/) es un agente de IA autónomo que puede escribir y ejecutar código, administrar archivos y llevar a cabo tareas complejas de múltiples pasos en tu nombre. A diferencia de un asistente de chat que solo responde preguntas, OpenClaw realiza acciones reales en tu sistema, lo que significa que necesita un backend de IA rápido y capaz que pueda seguir el ritmo de un ciclo de agente exigente.

[**Lemonade Server**](https://lemonade-server.ai/) es ese backend. Es un servidor de inferencia local de código abierto que ejecuta modelos de GenAI directamente en tu hardware y los expone a través de la API estándar de la industria de OpenAI.

Juntos forman una pila de agente de IA completamente local: Lemonade se encarga de la inferencia del modelo y OpenClaw proporciona el ciclo de agente que convierte las salidas del modelo en acciones reales.

> **Antes de continuar:** OpenClaw es un agente de IA altamente autónomo. Dar a cualquier agente de IA acceso a tu sistema puede resultar en consecuencias impredecibles o no deseadas. Procede solo si comprendes los riesgos y te sientes cómodo con que un software autónomo actúe en tu nombre.

---

## Lo que aprenderás

Al finalizar este playbook podrás:

- Conocer **Lemonade Server**
- **Instalar OpenClaw** y **apuntarlo a Lemonade Server** como su backend de IA.
- **Iniciar el gateway de OpenClaw** y confirmar que tu agente está listo para trabajar.
- **Conectar un canal de comunicación** (Discord o Telegram) para que puedas chatear con tu agente desde cualquier dispositivo.

---

## Configurar la configuración de memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

<!-- @os:linux -->
- Una PC con **Ubuntu 24.04+** o una distribución Linux basada en Debian compatible con `apt-get`
- Al menos **12 GB de RAM** (se recomiendan 64 GB o más para modelos más grandes)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcional, para aislar OpenClaw en un sandbox)

- **~10–30 GB de espacio libre en disco** para los pesos del modelo
<!-- @os:end -->
<!-- @os:windows -->
- Una PC con **Windows 10/11**
- Al menos **12 GB de RAM** (se recomiendan 64 GB o más para modelos más grandes)
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

El modelo recomendado para este playbook es **Qwen3.6-35B-A3B-GGUF** de Unsloth, un sólido modelo MoE con una ventana de contexto de 263k tokens que es muy adecuado para cargas de trabajo de agentes. Este modelo utiliza cuantización UD-Q4_K_XL. Descárgalo ahora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Luego cárgalo con una ventana de contexto grande y guarda esa configuración para ejecuciones futuras:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

El modelo tiene una longitud de contexto predeterminada de 262,144 tokens. Si encuentras errores de falta de memoria (OOM), considera reducir la ventana de contexto. Sin embargo, dado que Qwen3.6 aprovecha el contexto extendido para tareas complejas, recomendamos mantener una longitud de contexto de al menos 128K tokens para preservar las capacidades de razonamiento.

> **Consejo: Deshabilitar el pensamiento para respuestas de agente más rápidas:** Qwen3.6-35B-A3B se ejecuta en modo de pensamiento de forma predeterminada, lo que agrega latencia antes de cada respuesta. En los ciclos de agente, esta sobrecarga se acumula rápidamente. El repositorio [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) proporciona una configuración lista para usar que deshabilita el pensamiento. Para usarla, descarga el archivo e impórtalo:
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

Ejecutamos OpenClaw dentro de WSL (recomendado) y lo conectamos a Lemonade que se ejecuta de forma nativa en Windows. Esto te proporciona un entorno de shell de Linux para OpenClaw mientras mantiene la aceleración GPU de Lemonade en el lado de Windows.

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

Ejecuta esto dentro del terminal de Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Reinicia WSL:

```powershell
wsl --shutdown
wsl
```

### Conectar Lemonade desde Windows hacia WSL

WSL2 se ejecuta en una red virtual. Lemonade en Windows se enlaza a `127.0.0.1`, al cual WSL no puede acceder directamente. Un proxy de puerto de Windows reenvía el tráfico desde la IP del gateway de WSL hacia localhost de Windows.

**Encuentra tu IP del gateway de WSL** (ejecuta dentro de WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Agrega el proxy de puerto** (ejecuta en PowerShell como Administrador, reemplazando `<WSL-Gateway-IP>` con tu IP del gateway de WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

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

> La regla `netsh portproxy` sobrevive a los reinicios, pero la IP del gateway de WSL puede cambiar después de `wsl --shutdown`. Si Lemonade deja de ser accesible desde WSL tras un reinicio, obtén la IP del gateway actualizada y actualiza el proxy con esta nueva IP.

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

El indicador `--no-onboard` omite el asistente de configuración interactivo; configurarás el backend del modelo manualmente en el siguiente paso, lo que te da control preciso sobre qué modelo y servidor se utilizan.

Abre un nuevo terminal y confirma la instalación:

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

> **Dimensionamiento de la ventana de contexto de OpenClaw:** La compactación de OpenClaw se activa cuando `contextTokens > contextWindow − reserveTokens`. El `reserveTokensFloor` predeterminado es de 20,000 tokens, un límite mínimo que anula `reserveTokens` cuando es menor, por lo que cualquier contexto de modelo por debajo de ~37k activará un bucle de compactación infinito. Establece una reserva baja y deshabilita el límite mínimo una vez en tu configuración y se aplicará a todos los modelos, sin necesidad de ajuste por modelo:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` es un *límite mínimo* (guardia mínima), no la reserva en sí; establecer solo el límite mínimo no tiene efecto. `reserveTokensFloor: 0` deshabilita la guardia para que se acepte el `reserveTokens` más bajo.
>
> **Cuándo aplicar esto:** Usa esta configuración si la ventana de contexto efectiva de tu modelo está por debajo de ~37k, ya sea porque el modelo es pequeño (por ejemplo, 8k, 16k, 32k) o porque lo has limitado intencionalmente a un valor menor (por ejemplo, cargando un modelo de 128k pero estableciendo el contexto en 16k en Lemonade). Sin esto, OpenClaw entra en un bucle de compactación infinito al inicio.
>
> **Modelos de contexto grande a contexto completo:** Puedes omitir esto por completo. Los valores predeterminados funcionan bien; la compactación se activará mucho antes de que la ventana se llene y el modelo tendrá amplio espacio para generar respuestas largas. Si lo aplicas, ten en cuenta que `reserveTokens: 4096` limita la longitud de la respuesta a ~4k tokens, lo que puede truncar la generación de archivos largos o planes detallados.
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
> El resto de tu configuración (gateway, canales, modelos, etc.) permanece sin cambios; solo es necesario agregar la clave `compaction`.

### (Recomendado) Habilitar el aislamiento en sandbox con Docker

OpenClaw puede enrutar todas las operaciones de archivos y código del agente a través de un contenedor Docker aislado en lugar de ejecutarlas directamente en tu host. Esto limita el alcance de cualquier acción no deseada al sandbox, dejando intactos el sistema de archivos y la red de tu host.

Construye la imagen del sandbox una vez (Docker debe estar instalado):

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

Ejecuta esto para agregar la clave `sandbox` dentro del bloque `agents.defaults` existente en `~/.openclaw/openclaw.json`:

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

Los contenedores sandbox **no tienen acceso a la red** de forma predeterminada. Consulta la [referencia de sandboxing](https://docs.openclaw.ai/gateway/sandboxing) para conocer los montajes de enlace y las anulaciones de red.

> #### Solución de problemas: Permiso denegado en Docker
> 
> Si obtienes "permission denied" al ejecutar comandos de Docker:
> 
> **Paso 1: Agrega tu usuario al grupo docker**
> 
> ```bash
> sudo groupadd docker                    # Crear el grupo si es necesario
> sudo usermod -aG docker $USER           # Agregarte al grupo
> newgrp docker                           # Activar el cambio
> docker run hello-world                  # Probarlo
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
> **Solución temporal rápida** (se restablece después del reinicio):
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

### Iniciar el gateway de OpenClaw

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

Para abrir el panel de control, ejecuta esto en un segundo terminal mientras el gateway sigue en ejecución:

```bash
openclaw dashboard
```

Dado que el gateway se enlaza al loopback, el panel de control se autentica automáticamente cuando se abre desde la misma máquina; no se necesita ingresar un token ni aprobar un dispositivo para el acceso local. Deberías ver el panel de control de OpenClaw con tu modelo de Lemonade listado como el backend activo.

> Si habilitaste el sandboxing, puedes verificarlo pidiéndole al agente que ejecute `run hostname` desde el panel de control. Si ves un ID de contenedor corto en lugar del nombre de host de tu máquina, el sandbox está funcionando.

**Felicitaciones, has construido una pila de agente de IA completamente local desde cero.**

> **¿Necesitas el token del gateway?** Ejecuta `openclaw dashboard --no-open` para imprimir la URL del panel de control con el token incorporado (también intenta copiarlo a tu portapapeles). Alternativamente, el token se encuentra en `gateway.auth.token` dentro de `~/.openclaw/openclaw.json`.
>
> **Aprobar un dispositivo remoto:** Cuando abres el panel de control desde una segunda máquina o teléfono, el navegador muestra un ID de solicitud. De vuelta en la máquina que ejecuta el gateway, ejecuta:
> ```bash
> openclaw devices approve <requestId>
> ```
> Esto solo es necesario para dispositivos remotos o secundarios; el acceso por loopback desde la misma máquina se autentica automáticamente.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcional: Conectar un canal de comunicación

Una vez que el gateway esté en ejecución, puedes acceder a tu agente local desde cualquier dispositivo. Elige la opción que se adapte a tu configuración. OpenClaw admite [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) y otros canales; consulta la lista completa en [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opción A: Discord

Discord requiere un servidor donde **tengas acceso de administrador** para agregar un bot. Si compartes servidores pero no eres propietario de ninguno, usa la Opción B (Telegram) en su lugar.

#### Crear una cuenta y un servidor de Discord

Si no tienes una cuenta de Discord, regístrate en [discord.com](https://discord.com). También necesitas un servidor donde seas administrador; crea uno haciendo clic en el ícono **+** en la barra lateral de Discord y seleccionando **Crear el mío**. Un servidor privado está bien.

#### Crear una aplicación y un bot de Discord

1. Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications) y haz clic en **Nueva Aplicación**. Dale un nombre (por ejemplo, "openclaw-bot").
2. En la barra lateral, haz clic en **Bot**. Establece un nombre de usuario para el bot.
3. Aún en la página del Bot, desplázate hasta **Privileged Gateway Intents** y habilita:
   - **Message Content Intent** (requerido)
   - **Server Members Intent** (recomendado)
4. Desplázate hacia arriba y haz clic en **Reset Token** para generar tu token de bot. Cópialo.

#### Agregar el bot a tu servidor

1. En la barra lateral, haz clic en **OAuth2/ URL Generator**.
2. En **Scopes**, habilita `bot` y `applications.commands`.
3. En **Bot Permissions**, habilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia la URL generada, pégala en tu navegador, selecciona tu servidor y confirma. El bot debería aparecer ahora en la lista de miembros de tu servidor.

#### Recopilar tus IDs

Habilita el Modo Desarrollador en Discord (**Configuración de usuario/ Avanzado/ Modo Desarrollador**), luego:
- Haz clic derecho en el ícono de tu servidor: **Copiar ID del servidor**
- Haz clic derecho en tu propio avatar: **Copiar ID de usuario**

#### Permitir mensajes directos de los miembros del servidor

Haz clic derecho en el ícono de tu servidor/ **Configuración de privacidad**/ activa **Mensajes directos**. Esto permite que el bot te envíe mensajes directos, lo cual es necesario para el paso de emparejamiento.

#### Configurar OpenClaw para Discord

Guarda tu token de bot como una variable de entorno, luego crea un único archivo de parche que habilite Discord, haga referencia al token y permita tu servidor. Reemplaza `<server_id>` y `<user_id>` con los IDs recopilados anteriormente.

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

> **No dependas de pedirle al agente que configure esto.** Cuando el sandboxing está habilitado, el agente no puede escribir en `~/.openclaw/openclaw.json` desde dentro del sandbox; usa los comandos CLI anteriores en el host en su lugar.

Reinicia el gateway para que tome la nueva configuración del canal:

```bash
openclaw gateway run --bind loopback --port 18789
```

Deberías ver `logged in to discord as <bot-name>` en la salida del gateway en pocos segundos.

#### Emparejar tu cuenta de Discord

Envía un mensaje directo al bot en Discord. Responderá con un código de emparejamiento corto.

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

Telegram es más sencillo que Discord para la mayoría de los usuarios; no requiere servidor ni acceso de administrador.

#### Crear un bot de Telegram

1. Abre Telegram y envía un mensaje a **@BotFather**.
2. Envía `/newbot` y sigue las instrucciones. Guarda el token de bot que te proporciona.

#### Configurar OpenClaw para Telegram

Guarda el token como una variable de entorno:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Agrega la configuración del canal a `~/.openclaw/openclaw.json` (o aplícala mediante el panel de control):

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

Reinicia el gateway, luego envía cualquier mensaje a tu bot en Telegram. Aprueba el emparejamiento:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Los códigos de emparejamiento expiran después de una hora. Ahora puedes chatear con tu agente a través de mensajes directos en Telegram.

---

## Próximos pasos

Ahora que tu agente puede recibir comandos desde tu teléfono y actuar en tu máquina local, aquí hay tres direcciones que vale la pena explorar:

1. **Resumen del mercado de valores**: Programa OpenClaw para obtener datos de APIs financieras en un intervalo fijo, resumir los movimientos del día con tu modelo local y enviar un resumen a tu teléfono cada mañana a través del canal que hayas elegido.

2. **Monitor de ajuste fino**: Inicia un trabajo de entrenamiento de forma remota a través de Telegram o Discord, luego haz que el agente monitoree el registro de entrenamiento e informe periódicamente los valores de pérdida, la utilización de la GPU y el uso del disco a tu teléfono. Si la ejecución se detiene o el VRAM aumenta repentinamente, te enteras de inmediato sin necesidad de estar frente a la máquina.

3. **IoT con un VLM local**: Apunta una cámara a tu puerta principal, ejecuta un modelo de visión en Lemonade y haz que OpenClaw analice fotogramas bajo demanda o ante un disparador. Pregunta "¿llegaron paquetes hoy?" desde tu teléfono y obtén una respuesta directa de tu propio hardware.