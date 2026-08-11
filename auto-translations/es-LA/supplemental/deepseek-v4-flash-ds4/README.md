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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Descripción general

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) es la variante enfocada en eficiencia de la familia DeepSeek V4, un modelo de Mixture of Experts con 284 mil millones de parámetros y 13 mil millones de parámetros activos. Según el [informe técnico de DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), obtiene un puntaje de 79% en SWE-bench Verified y 91.6% en LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) es un motor de inferencia dedicado, creado específicamente para esta arquitectura de modelo. En lugar de ser un runtime de propósito general, ds4 se enfoca directamente en la familia DeepSeek V4 con optimizaciones de kernel específicas de la arquitectura para AMD ROCm™ software. Actualmente es una de las implementaciones de DeepSeek V4 Flash con mejor rendimiento en Strix Halo.

Este tutorial muestra cómo usar `ds4-cockpit`, una interfaz de usuario de terminal, para configurar ds4, descargar los pesos del modelo e iniciar el servicio de DeepSeek V4 Flash de forma local en la AMD Ryzen™ AI Halo Developer Platform.

## Qué aprenderás

- Cómo instalar e iniciar la interfaz de usuario de terminal `ds4-cockpit`
- Cómo crear el contenedor toolbox de ROCm para ds4
- Descargar la cuantización recomendada para un solo nodo Halo
- Iniciar el servidor de inferencia ds4 y exponer un endpoint compatible con OpenAI
- Conectar una Web UI o un agente de codificación al servidor local

## Configuración de la memoria

<!-- @require:memory-config -->

## Instalación de los requisitos previos de software

> **Requisitos del sistema para esta configuración (IQ2_XXS de un solo nodo con contexto de 126k):**
> - Un sistema Strix Halo con **al menos 128 GB de memoria unificada**.
> - **La VRAM dedicada del BIOS (UMA frame buffer) configurada al mínimo**, para que el grupo de memoria compartida pueda ser lo más grande posible.
> - El grupo de memoria compartida de la GPU **configurado en al menos 110 GB**: ejecuta `amd-ttm --set 110` (consulta el paso de configuración de memoria anterior) y reinicia. Valores más bajos pueden generar errores de memoria insuficiente al cargar el modelo con un contexto de 126k. Si tu sistema tiene menos memoria disponible, reduce el valor de **Context** en Server Mode en su lugar.
>
> **Nota:** Intenta establecer el **grupo de memoria compartida de la GPU** en **110 GB** como punto de partida. Si te encuentras con errores de memoria insuficiente, aumenta el grupo de memoria compartida o reduce el tamaño del contexto.

ds4-cockpit usa contenedores toolbox para ejecutar el motor ds4. Instala `podman`, `distrobox` y `pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## Cuantizaciones disponibles

El autor de ds4 proporciona varias versiones cuantizadas de DeepSeek V4 Flash en formato GGUF. Todos los modelos a continuación usan calibración por matriz de importancia (imatrix), que conserva mayor precisión para las partes del modelo que más importan en tareas de codificación y razonamiento.

| Cuantización | Tamaño | Descripción |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | Recomendado para un solo nodo de 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Mantiene las capas 37–42 en precisión Q4 para mejor exactitud. Cabe en 128 GB pero deja menos espacio para el contexto |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Mayor calidad. Requiere dos nodos Halo mediante clustering multinodo |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | Complemento opcional para decodificación especulativa que mejora la velocidad de generación |

El modelo **IQ2_XXS imatrix** es un buen punto de partida. Cabe cómodamente en un solo nodo y deja suficiente memoria para una ventana de contexto razonable.

## Instalación de ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) es una interfaz de usuario de terminal ligera para facilitar la puesta en marcha de ds4 en Strix Halo. Se encarga de crear los contenedores toolbox, descargar los pesos del modelo e iniciar los servidores. Instálala con `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Inicia el cockpit:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Creación del toolbox

En la pestaña **Interactive Toolboxes**, selecciona el toolbox estable/disponible más reciente (por ejemplo, `ds4-rocm-7.2.4`) y haz clic en **Create/Update**. Esto descarga la imagen del contenedor y crea el entorno del toolbox.


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Descarga del modelo

Ve a la pestaña **Model Manager**. Selecciona **IQ2_XXS imatrix (~80.8 GB)** en el menú desplegable y haz clic en **Download**. Los archivos del modelo se guardarán en `~/ds4` de forma predeterminada (puedes cambiar la ruta de almacenamiento).

> **Nota:** El modelo IQ2_XXS pesa aproximadamente 80 GB, por lo que la descarga puede tardar un tiempo según tu conexión. Puedes continuar una vez que finalice.

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## Inicio del servidor

Ve a la pestaña **Server Mode**. Selecciona el modelo descargado y el toolbox, y configura el tamaño del contexto, el host y el puerto. Cuando estés listo, haz clic en **Start ds4-server**.

> **Consejo:** Un tamaño de contexto de `126000` es un valor inicial razonable que debería caber en un solo nodo; puedes aumentarlo si tienes memoria de sobra, o reducirlo si te encuentras con errores de memoria insuficiente. El puerto (`8000` en esta guía) es arbitrario; elige cualquier puerto libre.

> **KV Disk Cache (opcional).** Activar **KV Disk Cache** descarga la caché de KV al disco (en **Host Cache Dir**, `~/.cache/ds4-kv` de forma predeterminada) para que los prompts de sistema repetidos se restauren desde el SSD en lugar de recalcularse. Es una optimización de rendimiento para flujos de trabajo de agentes de codificación con prompts largos y repetidos, y **no es necesario** para ejecutar el servidor.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

El servidor se iniciará y escuchará en el puerto 8000, exponiendo un endpoint de API compatible con OpenAI en `http://localhost:8000/v1`.

**Prueba rápida:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->

## Conexión de una Web UI

Puedes conectar cualquier interfaz de chat compatible con el formato de la API de OpenAI. Por ejemplo, para usar HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Abre `http://localhost:3000` en tu navegador para comenzar a chatear.
## Conectar un agente de codificación

El servidor ds4 expone endpoints compatibles tanto con OpenAI como con Anthropic, por lo que la mayoría de los agentes de codificación pueden conectarse a él directamente. Por ejemplo, para agregarlo al agente de codificación `pi`, agrega el siguiente bloque a `~/.pi/agent/models.json`:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **Consejo**: Si tu agente de codificación o interfaz web se ejecuta en una máquina diferente a la plataforma Halo, deberás reenviar el puerto 8000 mediante SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Próximos pasos

- **Clustering multinodo**: Si tienes dos dispositivos Halo, ds4 permite distribuir el modelo Q4 (~153 GB) entre ambas máquinas mediante paralelismo de canalización (pipeline parallelism). Consulta la [documentación de ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) para conocer las instrucciones de configuración.
- **Decodificación especulativa (MTP)**: Descarga los pesos MTP (~3.6 GB) y pasa `--mtp` al servidor para obtener una velocidad de generación más rápida.
- **Descarga de caché KV a disco**: Para flujos de trabajo de agentes de codificación, habilita `--kv-disk-dir` para que los prompts de sistema repetidos se restauren desde el SSD en lugar de recalcularse cada vez.

Para obtener más información, consulta el [repositorio de ds4](https://github.com/antirez/ds4) y el [toolbox de ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).