<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Ejecutando Hermes Agent localmente con Lemonade Server

## Descripción general

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) es un agente de IA autosuperable creado por Nous Research. Tiene un bucle de aprendizaje incorporado, crea habilidades a partir de la experiencia, construye una memoria persistente sobre quién eres tú a través de las sesiones y puede ejecutar automatizaciones programadas en tu nombre. A diferencia de un asistente de chat simple, Hermes realiza acciones reales: ejecuta comandos de shell, escribe archivos, navega por la web y delega flujos de trabajo paralelos a subagentes.

[**Lemonade Server**](https://lemonade-server.ai/) es el backend de inferencia local que lo impulsa. Es un servidor de código abierto que ejecuta modelos de IA generativa directamente en tu hardware de AMD y los expone a través de la API estándar de la industria de OpenAI.

Juntos forman un stack de agente de IA completamente local: Lemonade se encarga de la inferencia de modelos en tu GPU, y Hermes proporciona el bucle del agente, la memoria, las habilidades y la puerta de enlace de mensajería.

> **Antes de continuar:** Hermes Agent es un agente de IA altamente autónomo. Dar acceso a tu sistema a cualquier agente de IA puede generar resultados impredecibles o no deseados. Continúa solo si comprendes los riesgos y te sientes cómodo con software autónomo actuando en tu nombre.

---

## Qué aprenderás

Al finalizar este playbook podrás:

- **Instalar Hermes Agent** y configurarlo para que use **Lemonade Server** como su backend de IA.
- **(Recomendado) Habilitar el sandboxing con Docker/Podman** para aislar las acciones del agente de tu equipo anfitrión.
- **Iniciar la puerta de enlace de Hermes** y confirmar que tu agente está listo.
- **Conectar un canal de comunicación** (Discord o Telegram) para poder chatear con tu agente desde cualquier dispositivo.

---

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de requisitos previos de software

<!-- @os:linux -->
- Una PC con **Ubuntu 24.04+** o una distribución de Linux compatible basada en Debian con `apt-get`
- Al menos **12 GB de RAM** (se recomiendan 64 GB+ para modelos más grandes)
- **~10–30 GB de espacio libre en disco** para los pesos del modelo
- [Podman](https://podman.io/docs/installation) (opcional, para hacer sandboxing de Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Una PC con **Windows 10/11**
- Al menos **12 GB de RAM** (se recomiendan 64 GB+ para modelos más grandes)
- **~10–30 GB de espacio libre en disco** para los pesos del modelo
- Podman (opcional, para hacer sandboxing de Hermes Agent). Instálalo dentro de WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman viene preinstalado en Halo Box y no requiere configuración
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Descargar y cargar el modelo recomendado

El modelo recomendado para este playbook es **Qwen3.6-35B-A3B-GGUF** de Unsloth, un modelo MoE robusto con una ventana de contexto de 263k tokens que se adapta muy bien a las cargas de trabajo de agentes. Este modelo utiliza cuantización UD-Q4_K_XL. Descárgalo ahora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Luego cárgalo con una ventana de contexto amplia y guarda esa configuración para futuras ejecuciones:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

El modelo tiene una longitud de contexto predeterminada de 262,144 tokens. Si encuentras errores de falta de memoria (OOM), considera reducir la ventana de contexto.

> **Consejo: desactiva el modo de razonamiento para obtener respuestas de agente más rápidas:** Qwen3.6-35B-A3B se ejecuta en modo de razonamiento (thinking mode) de forma predeterminada, lo que agrega latencia antes de cada respuesta. En bucles de agentes esta sobrecarga se acumula rápidamente. El repositorio [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) proporciona una configuración lista para usar que desactiva el razonamiento. Para usarla, descarga el archivo e impórtalo:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Ejecutamos Hermes Agent dentro de WSL y lo conectamos a Lemonade, que se ejecuta de forma nativa en Windows. Esto te brinda un entorno de shell de Linux para Hermes mientras mantienes la aceleración por GPU de Lemonade en el lado de Windows.

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

Reinicia WSL:

```powershell
wsl --shutdown
wsl
```

### Conectar Lemonade desde Windows a WSL

WSL2 se ejecuta en una red virtual. Lemonade en Windows se vincula a `127.0.0.1`, al que WSL no puede acceder directamente. Un proxy de puertos de Windows reenvía el tráfico desde la IP de la puerta de enlace de WSL hacia el localhost de Windows.

**Encuentra la IP de la puerta de enlace de WSL** (ejecuta esto dentro de WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Agrega el proxy de puertos** (ejecútalo en PowerShell como Administrador, reemplazando `<WSL-Gateway-IP>` por la IP de la puerta de enlace de WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Agrega una regla de firewall** (en la misma PowerShell elevada):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifica desde WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Si ya cargaste el modelo Qwen3.6-35B-A3B-GGUF en el paso anterior, deberías ver una salida JSON que muestra tu modelo cargado.

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

> La regla `netsh portproxy` persiste tras los reinicios, pero la IP de la puerta de enlace de WSL puede cambiar después de ejecutar `wsl --shutdown`. Si Lemonade deja de estar accesible desde WSL después de un reinicio, obtén la IP de la puerta de enlace actualizada y actualiza el proxy con esta nueva IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Instalar Hermes Agent

<!-- @os:windows -->
> Ejecuta los comandos de esta sección dentro de tu **terminal de WSL**, salvo que se indique lo contrario.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

El flag `--skip-setup` omite el asistente de configuración interactivo para que puedas configurar manualmente el backend del modelo en el siguiente paso.

Recarga tu shell:

```bash
source ~/.bashrc
```

Confirma la instalación:

```bash
hermes --version
```

Ejecuta un autodiagnóstico para verificar todas las dependencias:

```bash
hermes doctor
```

> **Consejo:** Si ves `command not found` después de la instalación, agrega Hermes a tu PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Para que esto sea permanente, agrega la línea anterior a tu `~/.bashrc` o `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Configurar Hermes para usar Lemonade

Hermes almacena su configuración de modelo en `~/.hermes/config.yaml`. Puedes usar el selector interactivo `hermes model` o escribir la configuración directamente.

### Opción 1: Selector interactivo

<!-- @os:windows -->
> Ejecuta lo siguiente dentro de tu **terminal de WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Cuando se te solicite:

1. Selecciona **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** usa la IP del gateway de WSL: ejecuta `ip route show default | awk '{print $3}' | head -1` dentro de WSL para obtenerla, luego ingresa `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** elige `Qwen3.6-35B-A3B-GGUF` de la lista
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (o el nombre que prefieras)

`hermes model` guarda tanto la selección de modelo activo como una entrada nombrada en `custom_providers` que almacena la longitud de contexto junto con el endpoint. El resultado en `~/.hermes/config.yaml` se ve así:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Opción 2: Escribir la configuración directamente

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

Dentro de tu terminal de WSL, obtén la IP del host de Windows y escribe la configuración:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Recomendado) Habilitar el sandboxing de Podman

Hermes Agent puede enrutar todas las operaciones de shell y archivos del agente a través de un contenedor aislado en lugar de ejecutarlas directamente en tu host. Esto limita el radio de impacto de cualquier acción no intencionada al sandbox, dejando el sistema de archivos y la red de tu host intactos.

Construye una imagen de sandbox liviana:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Ingresa a tu terminal de WSL:

```powershell
wsl -d Ubuntu-24.04
```

Luego, construye una imagen de sandbox liviana:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Luego configura Hermes para usar Podman como el runtime de contenedores y establece el backend de terminal:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> El `terminal.backend` sigue siendo `docker`.
> `HERMES_DOCKER_BINARY` es lo que le indica a Hermes que use Podman como runtime en lugar de Docker.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes ahora levantará un contenedor de sandbox persistente y enrutará todas las llamadas de `terminal` y de herramientas de archivos a través de él. El contenedor comparte el ciclo de vida del proceso de Hermes, se reutiliza en todas las llamadas a herramientas, y se destruye cuando Hermes finaliza.

> **Verifica que el sandbox esté funcionando:** Inicia Hermes (`hermes`) y pídele que ejecute `run hostname`; deberías ver un ID de contenedor corto en lugar del nombre de host de tu máquina. También puedes pedirle que ejecute `rm -rf <path-to-a-dummy-file/folder>`: Hermes confirmará la eliminación, pero la carpeta seguirá estando en tu host. El comando se ejecutó dentro del `$HOME` aislado del contenedor, no en el tuyo.

> **¿Necesitas un aislamiento más fuerte?** Hermes también proporciona una imagen oficial de Docker (`nousresearch/hermes-agent`) que ejecuta todo el proceso del agente dentro de un contenedor: gateway, herramientas y todo lo demás. Consulta la [documentación de Docker de Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) para más detalles sobre la configuración.

---

<!-- @os:linux -->
## (Recomendado) Integración de Hermes con los servicios de Firecrawl

Hermes puede navegar y extraer contenido de sitios web usando sus herramientas web integradas. Sin embargo, muchos sitios web modernos utilizan sistemas de detección de bots, que bloquean las solicitudes HTTP simples y devuelven páginas de desafío en lugar del contenido real. Como resultado, Hermes puede no ser capaz de extraer información de manera confiable de estos sitios.

Para superar esta limitación, [Firecrawl](https://docs.firecrawl.dev/introduction) ofrece un servicio de rastreo web y extracción de contenido autoalojado que puede sortear estos desafíos y desbloquear todo el potencial de la automatización de Hermes.

En esta configuración, Firecrawl se ejecuta como un conjunto de contenedores Docker gestionados con Podman. Para simplificar la gestión del ciclo de vida y el inicio automático, registramos Firecrawl como un servicio de `systemd` a nivel de usuario que orquesta el stack subyacente de Podman Compose. Esto permite que Hermes inicie, detenga y verifique el servicio de Firecrawl usando comandos estándar de `systemctl --user` en lugar de interactuar directamente con los contenedores.

Para simplificar las cosas, dividimos todo el proceso en cuatro pasos:

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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
En este punto, el servicio ha sido definido pero aún no registrado con `systemd`.
Asegúrate de que el nombre del archivo coincida exactamente con el que creaste anteriormente, luego ejecuta:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Si tiene éxito, deberías ver la siguiente salida:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contiene enlaces simbólicos a servicios configurados para iniciarse automáticamente.

### 2. Configurar Firecrawl para tu servicio

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) es ideal para quienes necesitan control total sobre sus entornos de scraping y procesamiento de datos, pero conlleva la contrapartida de un mayor esfuerzo de mantenimiento y configuración.

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
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Establece `BULL_AUTH_KEY` con un secreto seguro, especialmente en cualquier implementación accesible desde redes no confiables.
### 3. Implementación de Hermes mediante Compose

Antes de continuar, asegúrate de haber descargado la imagen de Docker más reciente de Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Una vez hecho esto, descarga el archivo Compose de Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) y colócalo en el directorio raíz `/firecrawl`:

> Esta convención es necesaria para que `systemd` pueda localizar e iniciar el servicio correctamente, tal como se especifica en `WorkingDirectory=${HOME}/firecrawl`.

> Siempre puedes ampliar el stack agregando servicios adicionales de Firecrawl según sea necesario. La lista completa de servicios disponibles se encuentra en el archivo oficial [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Iniciar el servicio Hermes a través de Firecrawl 

Antes de entregar el control a `systemd`, valida que todo funcione correctamente ejecutando el stack manualmente:
```bash
podman compose -f hermes-compose.yaml up -d
```
Si todo está configurado correctamente, deberías ver que el contenedor de Hermes se inicia y la salida de tu línea de comandos debería verse similar a esto:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Una vez verificado, detén el stack antes de continuar:
```bash
podman compose -f hermes-compose.yaml down
```
Ahora que todo está validado, inicia el servicio a través de `systemd`:
```bash
systemctl --user start firecrawl.service
```
[La API de Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) es accesible desde dentro del contenedor interactivo, y el Panel Web está disponible en el mismo host y puerto en http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Para detener el servicio, ejecuta:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Inicia una sesión de CLI interactiva directamente: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Felicitaciones, has construido un stack de agente de IA completamente local.**

### Panel Web

Hermes incluye una interfaz de usuario basada en navegador para gestionar la configuración, claves de API, modelos, sesiones, memoria y tareas programadas (cron jobs). Abre una segunda terminal mientras el gateway o la CLI están en ejecución y lánzalo con:

```bash
hermes dashboard
```

Esto inicia un servidor local y abre `http://127.0.0.1:9119` en tu navegador. Consulta la [documentación del panel](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) para conocer todas las funciones disponibles.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opcional: Conectar un canal de comunicación

Una vez que el gateway esté en ejecución, podrás acceder a tu agente local desde cualquier dispositivo. Hermes es compatible con [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), y otros

---

### Discord

Discord requiere un servidor donde **tengas acceso de administrador** para agregar un bot. Si compartes servidores pero no eres propietario de ninguno, utiliza Telegram en su lugar.

#### Crear una aplicación y un bot de Discord

1. Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications) y haz clic en **New Application**. Asígnale un nombre (por ejemplo, "hermes-bot").
2. En la barra lateral, haz clic en **Bot**. Establece un nombre de usuario para el bot.
3. Aún en la página Bot, desplázate hasta **Privileged Gateway Intents** y habilita:
   - **Message Content Intent** (requerido)
   - **Server Members Intent** (recomendado)
4. Vuelve a desplazarte hacia arriba y haz clic en **Reset Token** para generar tu token de bot. Cópialo.

#### Agregar el bot a tu servidor

1. En la barra lateral, haz clic en **OAuth2 / URL Generator**.
2. En **Scopes**, habilita `bot` y `applications.commands`.
3. En **Bot Permissions**, habilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia la URL generada, pégala en tu navegador, selecciona tu servidor y confirma.

#### Recopilar tus IDs y permitir mensajes directos

Habilita el Modo Desarrollador en Discord (**User Settings / Advanced / Developer Mode**), luego:
- Haz clic derecho en el ícono de tu servidor: **Copy Server ID**
- Haz clic derecho en tu propio avatar: **Copy User ID**

Haz clic derecho en el ícono de tu servidor / **Privacy Settings** / activa **Direct Messages**. Esto es necesario para el paso de emparejamiento.

#### Configurar Hermes para Discord

Agrega lo siguiente a `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Luego inicia el gateway:

```bash
hermes gateway
```

El bot debería aparecer en línea en Discord en cuestión de segundos. Envíale un mensaje, ya sea un DM o en un canal donde pueda verlo.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Crear un bot de Telegram

1. Abre Telegram y envía un mensaje a **@BotFather**.
2. Envía `/newbot` y sigue las indicaciones. Guarda el token del bot que te proporcione.

#### Configurar Hermes para Telegram

Agrega lo siguiente a `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **¿No conoces tu ID de usuario de Telegram?** Envía un mensaje a [@userinfobot](https://t.me/userinfobot) en Telegram, y te responderá con tu ID numérico.

Luego inicia el gateway:

```bash
hermes gateway
```

Envía a tu bot cualquier mensaje en Telegram para probarlo. Ahora puedes chatear con tu agente a través de un DM de Telegram. Consulta la [guía completa de configuración de Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) para el modo webhook y opciones avanzadas.

---

## Próximos pasos

Ahora que tu agente puede recibir comandos desde tu teléfono y actuar en tu máquina local, aquí tienes tres direcciones que vale la pena explorar:

1. **Resumen automatizado de investigación**: Programa a Hermes para que busque en la web temas que te interesen cada mañana, resuma los hallazgos con tu modelo local y envíe un resumen a tu teléfono a través de Telegram o Discord, todo ejecutándose en tu propio hardware sin costos en la nube.

2. **Revisión de código a pedido**: Dirige a Hermes hacia un repositorio de GitHub, pídele que revise las solicitudes de extracción (pull requests) abiertas, y haz que publique comentarios o un resumen de vuelta en tu chat. Con el backend de terminal de Docker, todas las operaciones de git se ejecutan dentro del sandbox, manteniendo limpio tu host.

3. **Asistente local de archivos**: Dale a Hermes acceso a un directorio de trabajo y pídele que organice, renombre, resuma o transforme archivos a pedido desde tu teléfono. Debido a que el backend de terminal de Docker confina todas las escrituras al espacio de trabajo del sandbox, las operaciones destructivas accidentales quedan contenidas.