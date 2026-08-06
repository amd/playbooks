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

🍋 **Lemonade** es un servidor de IA local de código abierto que te permite ejecutar modelos de lenguaje grandes (LLMs), generadores de imágenes y modelos de audio directamente en tu propio hardware. Expone los modelos a través de la API estándar de la industria de **OpenAI**, por lo que cualquier aplicación que funcione con OpenAI puede funcionar instantáneamente con Lemonade. Al final de este playbook, estarás usando Lemonade para ejecutar modelos localmente en tu máquina.

## Qué aprenderás

Al final de este playbook podrás:

* **Instalar Lemonade Server** y verificar que se esté ejecutando.
* **Descargar y chatear con un LLM** usando un solo comando.
* **Explorar la interfaz web** y probar diferentes modalidades como visión, voz a texto y generación de imágenes.
* **Cambiar entre backends de GPU** entre Vulkan y el software AMD ROCm™.
* **Construir una aplicación en Python** impulsada por un LLM local usando la API compatible con OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Ejecutar modelos en la unidad de procesamiento neuronal (NPU) de AMD** usando los modos de ejecución Hybrid y FLM en hardware AMD Ryzen™ AI.
<!-- @device:end -->

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

Antes de comenzar, asegúrate de tener:

- Una PC con **Windows 11** o una distribución de **Linux** compatible (Ubuntu 24.04+, Fedora, Debian)
- Se recomiendan **16 GB de RAM** para el modelo en tiempo de ejecución usado en los pasos 1 a 7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Se recomiendan **32 GB o más** si quieres usar el modelo de generación de código más grande del paso 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB de espacio libre en disco**, dependiendo de los modelos que descargues. El modelo más grande de esta guía pesa alrededor de 20 GB.
- **Python 3.10–3.13** (usado en la sección de la aplicación en Python)
- Una conexión a internet (con cable o inalámbrica)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcional] Un NPU AMD XDNA 2 (serie Ryzen AI 300/400/Max 300 o Z2 Extreme) con el controlador más reciente instalado desde [Instrucciones de instalación del software Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) si deseas ejecutar un modelo en el NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## Conceptos clave: cómo funcionan los servidores de IA local

Antes de ejecutar un modelo, vale la pena entender *por qué* las cosas están configuradas de esta manera. Lemonade es un **servidor de modelos local**, un proceso que carga modelos de IA en memoria y los expone a las aplicaciones a través de HTTP, tal como lo haría un servicio de IA en la nube.

### ¿Por qué un servidor?

| Beneficio | Qué significa para ti |
|---------|----------------------|
| **Integración simplificada** | Las aplicaciones se comunican con una sola API HTTP en lugar de lidiar con bibliotecas específicas de hardware en C++ o Python. |
| **Modelos compartidos** | Un solo modelo cargado puede servir a varias aplicaciones a la vez, sin copias duplicadas que consuman tu RAM. |
| **Portabilidad de la nube a lo local** | El código escrito para la API en la nube de OpenAI funciona con Lemonade con solo cambiar una URL. |
| **Separación de responsabilidades** | La gestión de modelos, la transmisión de datos y la tolerancia a fallos son manejadas por el servidor para que los desarrolladores puedan enfocarse en su aplicación. |

### El estándar de la API de OpenAI

Lemonade implementa la **API de OpenAI**, la misma interfaz utilizada por ChatGPT, Azure OpenAI y decenas de otros servicios. El modelo de conversación es simple:

| Rol | Quién está hablando |
|------|---------------|
| **system** | Instrucciones para el modelo (persona, restricciones, herramientas disponibles) |
| **user** | Mensajes del humano (o de la aplicación) hacia el modelo |
| **assistant** | Respuestas generadas por el modelo |

Esto significa que cualquier biblioteca o aplicación que sea compatible con OpenAI puede comunicarse con Lemonade apuntando a `http://localhost:13305/api/v1` mientras Lemonade Server esté en ejecución.

## Actividad principal: tu primer chat de IA local

Descarguemos un LLM y tengamos una conversación con él, ejecutando la IA completamente en tu propia máquina.

### Paso 1: Descargar y ejecutar un modelo

Lemonade viene con una biblioteca de modelos seleccionados. Empecemos con **Gemma-4-E2B-it**, un modelo compacto y capaz que incluye soporte de visión. Abre una terminal y ejecuta:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Este único comando hace tres cosas:

1. **Descarga** el modelo (~3 GB) desde Hugging Face, si aún no ha sido descargado. (Puede tardar un poco)
2. **Inicia** el proceso de Lemonade Server en el puerto 13305.
3. **Abre Lemonade App** para que puedas comenzar a chatear con el modelo.


<!-- @os:windows -->
En Windows, Lemonade App se inicia automáticamente y puedes comenzar a chatear de inmediato. Si instalaste el paquete `minimal.msi`, la aplicación no está incluida. Para comenzar a chatear, abre tu navegador web y ve a `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
En Linux, abre tu navegador y navega a `http://localhost:13305` para acceder a la aplicación web.
<!-- @os:end -->

Intenta escribir una pregunta:

```
What are three fun facts about lemons?
```

El modelo responderá directamente en la ventana de chat. **¡Felicitaciones! Estás ejecutando un modelo de lenguaje grande localmente.**

![Lemonade App con registros mostrados](../../dependencies/assets/ChatwithLogs.png)

En el panel de registros del servidor (Server Logs) dentro de Lemonade App, puedes encontrar datos de telemetría sobre el rendimiento del modelo después de cada respuesta. Por ejemplo:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Paso 2: Explora la interfaz web y las diferentes modalidades

Lemonade incluye una interfaz web integrada donde puedes:

- **Interactuar** con el modelo cargado en una ventana de chat familiar
- **Explorar modelos** en la pestaña Model Manager
- **Descargar nuevos modelos** con un solo clic

Prueba a cambiar entre diferentes modalidades usando la pestaña **Model Manager** en la interfaz web, donde puedes explorar modelos por Recipe o por Category:

1. **Visión:** El modelo `Gemma-4-E2B-it-GGUF` que ya tienes cargado admite visión. Pega una imagen en el cuadro de chat y pídele al modelo que la describa.
2. **Generación de imágenes:** En la categoría Image, descarga un modelo de imagen como `SDXL-Turbo` desde el Model Manager, y luego usa el Lemonade Image Generator para escribir un prompt y generar una imagen localmente.
3. **Audio:** En la categoría Audio, descarga un modelo de audio como `Whisper-Tiny`, que puede hacer conversión de voz a texto. Proporciona una grabación de audio para transcribirla localmente. Para conversión de texto a voz, prueba alguno de los modelos de la categoría Speech, como `kokoro-v1`.

![Multimodalidad con Lemonade](../../dependencies/assets/multi_modality.png)

### Paso 3: Prueba un modelo con un backend diferente

Si pasas el cursor sobre un modelo en la app de Lemonade, verás un ícono de engranaje. Al hacer clic en él, podrás seleccionar opciones para el modelo, incluyendo la elección del backend deseado.

Por defecto, Lemonade usa Vulkan para la aceleración por GPU. Si tienes una GPU discreta de AMD compatible, puedes cambiar a ROCm.

![Seleccionar backend en Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Para administrar tus backends instalados, haz clic en el botón de backend en la columna más a la izquierda.

Alternativamente, puedes especificar el backend usando el siguiente comando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

También puedes establecer tu backend predeterminado usando la variable de entorno `LEMONADE_LLAMACPP` con los valores: `vulkan`, `rocm` o `cpu`.

---

## Profundizando: crea una aplicación con IA usando Python

El verdadero poder de un servidor de IA local es que cualquier aplicación puede conectarse a él usando solo unas pocas líneas de código. Para demostrarlo, construyamos un pequeño pero funcional **generador de tarjetas de estudio (flashcards)** en el que le das un tema, genera tarjetas de estudio y puedes autoevaluarte de forma interactiva.

### Paso 4: Inicia el servidor

Verifica que el servidor de Lemonade esté ejecutándose. Normalmente se inicia automáticamente en segundo plano después de la instalación. Para verificarlo, ejecuta:

```
lemonade status
```

Deberías ver un mensaje como: `Server is running on port 13305`.

Si el servidor no está en ejecución, inícialo abriendo la app de Lemonade. Usa el puerto predeterminado **13305** (puedes confirmarlo o seleccionarlo desde el ícono de la bandeja del sistema).

### Paso 5: Instala el cliente Python de OpenAI

En una terminal, crea un entorno virtual (venv) e instala el cliente Python de OpenAI usando los siguientes comandos:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Paso 6: Construye la aplicación de tarjetas de estudio

Descarguemos un modelo diferente para generar código: `Qwen3.5-35B-A3B-GGUF`. Este es un modelo grande (~20 GB) y de alto rendimiento, más adecuado para sistemas con 32 GB o más de RAM. Si tienes menos RAM disponible, prueba con `Qwen3.5-9B-GGUF` (~6 GB) en su lugar.

Puedes descargarlo desde la interfaz de usuario o ejecutar lo siguiente:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Ingresa el siguiente prompt en la interfaz de chat de Lemonade para generar código para una aplicación sencilla de tarjetas de estudio. 

Usaremos Qwen3.5-35B-A3B-GGUF (un modelo más grande, mejor en la escritura de código) para generar nuestra aplicación en Python, y la aplicación en sí llamará a Gemma-4-E2B-it-GGUF (el modelo más pequeño que ya descargaste) en tiempo de ejecución. Luego, el código puede copiarse a un archivo de tu elección para ejecutarse en Python.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Consejo**: Hemos seguido prácticas de ingeniería estándar mediante una creación cuidadosa del prompt y el uso de un sistema de dos modelos para optimizar recursos y velocidad.

Para tu comodidad, hemos proporcionado un ejemplo de salida en [`flashcards.py`](assets/flashcards.py). Siéntete libre de descargarlo a tu directorio. De cualquier manera, ahora deberías tener un archivo Python que se puede ejecutar.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Paso 7: Ejecuta el código generado

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Esto es lo que deberías ver:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

En aproximadamente 150 líneas de código, has construido una herramienta de estudio completamente funcional impulsada por un LLM local. No hay clave de API que administrar, ni costos de uso, y ningún dato sale nunca de tu máquina.

> **Idea clave:** Nota que la línea `client = OpenAI(base_url=...) ` es la *única* cosa que conecta esta aplicación con Lemonade en lugar de la nube de OpenAI. El resto del código es idéntico a lo que escribirías contra cualquier servicio compatible con OpenAI. Si alguna vez has usado la biblioteca Python de OpenAI, ya sabes cómo crear aplicaciones con Lemonade.

### Qué demuestra esto

Esta pequeña aplicación pone en práctica varios patrones de integración del mundo real:

| Patrón | Dónde aparece |
|---------|-----------------|
| **Prompts de sistema** | El mensaje `"system"` le indica al LLM que genere JSON estructurado |
| **Salida estructurada** | La aplicación analiza la respuesta del LLM como JSON para construir las tarjetas de estudio |
| **Solicitudes sin estado** | Cada llamada a `generate_flashcards()` es independiente |
| **Manejo de errores** | El bloque `try/except` maneja de forma controlada los casos en los que la salida del LLM no es JSON válido |

Estos mismos patrones se aplican a cualquier aplicación, como chatbots, asistentes de código, generadores de contenido o herramientas de automatización.

#### Desafío adicional

* Para un desafío extra, intenta actualizar la aplicación para que las tarjetas de estudio se lean en voz alta al usuario, tomando como referencia el ejemplo proporcionado [aquí](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Ejecución de modelos en la NPU (opcional)

Si tienes un Ryzen AI 300/400/Max 300 series o Z2 Extreme, tu dispositivo cuenta con una **Unidad de Procesamiento Neuronal (NPU)** integrada, un chip dedicado diseñado específicamente para cargas de trabajo de IA. Ejecutar modelos en la NPU es más eficiente energéticamente que usar la GPU, lo que la hace ideal para tareas de IA en segundo plano, sesiones más largas y uso con batería.

Lemonade admite tres modos de ejecución en la NPU, todos transparentes detrás de la misma API de OpenAI:

| Modo | Cómo funciona | Receta | Modelos de ejemplo |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | La NPU procesa el prompt, la iGPU genera los tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Solo NPU** | La inferencia completa se ejecuta en la NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Usa el motor FastFlowLM en la NPU, optimizado para AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Requisitos

- Procesador **AMD Ryzen AI 300/400 series o Z2 series**
- Para modelos **FLM**: el runtime de FLM se puede instalar desde la app de Lemonade, o Lemonade instalará automáticamente el runtime de FLM al ejecutar un modelo FLM. Para obtener más información sobre FastFlowLM, consulta [aquí](https://fastflowlm.com/docs/).


### Paso 8: Ejecutar un modelo híbrido

Los modelos híbridos dividen el trabajo entre la NPU y la iGPU para lograr un buen equilibrio entre velocidad y eficiencia. En la Lemonade App, selecciona un modelo de la lista `Ryzen AI LLM`, por ejemplo, `Qwen3-4B-Hybrid`, o ejecútalo usando el siguiente comando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade detecta tu NPU automáticamente e instala el backend de **Ryzen AI LLM**.

> **¿Qué sucede internamente?** Cuando envías un mensaje, la NPU procesa todo tu prompt en paralelo (esto se denomina "prefill"). Luego, la iGPU toma el control para generar la respuesta un token a la vez (esto se denomina "decode"). Este enfoque híbrido aprovecha las fortalezas de cada chip.

### Paso 9: Ejecutar un modelo FLM

Los modelos FastFlowLM (FLM) están optimizados específicamente para la arquitectura NPU XDNA2 de AMD y pueden ser muy rápidos para su tamaño. Por ejemplo, selecciona `qwen3.5-4b-FLM` de la lista `FastFlowLM NPU` o usa el siguiente comando:

<!-- @os:windows -->
Para habilitar `FastFlowLM` en Windows:

* Abre el menú `Backends Manager`.
* Ubica la categoría de backend `FastFlowLM NPU`.
* Haz clic en Install NPU.
* Una vez completada la instalación, ~36 modelos predeterminados estarán disponibles en el menú desplegable de FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Cuando la app `Lemonade` se inicia por primera vez, el backend `FastFlowNPU` no está habilitado de forma predeterminada. 
La aplicación local abrirá la página de instalación para guiarte a través de la configuración.

Para habilitar `FastFlowLM` en Linux:

* Abre la app `Lemonade`.
* Visita la documentación [oficial de FLM](https://lemonade-server.ai/flm_npu_linux.html) y sigue los pasos de instalación de FLM seleccionando tu distribución de Linux.
* Habilita backports según se indica en la página de instalación.
* Descarga la última versión `v0.9.x` desde la [página de tags](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Para AMD Halo Developer Platform, asegúrate de elegir Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Instala el paquete `.deb` descargado.
* Recomendado: cierra la `Lemonade App` y vuelve a abrirla para que se detecten los cambios.
* Recomendado: abre `Backends Manager` y haz clic en Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Después de una instalación exitosa, deberías ver que `flm:npu` se completó en el **Download Manager** dentro de la **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Luego puedes seleccionar cualquiera de los modelos FFLM disponibles y comenzar a usar el backend de la NPU.

Para un modelo específico, descarga el modelo deseado desde la [página de modelos](https://fastflowlm.com/docs/models/qwen/) y valídalo usando el comando de Shell proporcionado en la documentación.
```
flm run qwen3.5-4b-FLM
```
o mediante 
```
lemonade run qwen3.5-4b-FLM
```

Los modelos FLM incluyen algunas de las arquitecturas más populares (Gemma 3, Qwen 3, Llama 3 y DeepSeek R1) y varían desde menos de 1 GB hasta más de 13 GB.
Lemonade detecta tu NPU automáticamente e instala el backend de **FastFlowLM NPU**.

<!-- @os:windows -->
> **Consejo:** Para obtener el mejor rendimiento de la NPU, habilita el modo turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Cambio de modelos

La aplicación de tarjetas de estudio del Paso 6 también funciona con modelos de NPU, solo cambia el nombre del modelo:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Próximos pasos

Ya tienes un servidor de IA local funcionando en tu propio hardware; aquí te mostramos hacia dónde ir a continuación:

1. **Conecta tus aplicaciones favoritas**: Lemonade funciona de forma inmediata con [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), y [muchas más](https://lemonade-server.ai/marketplace).

2. **Explora más modelos**: Recorre la [biblioteca completa de modelos](https://lemonade-server.ai/docs/server/server_models/) para encontrar modelos optimizados para programación, razonamiento, visión y más. Usa la Lemonade App o `lemonade list` para ver qué hay disponible.

3. **Desbloquea la aceleración de GPU con ROCm**: Si tienes una GPU de AMD compatible, cambia al backend de ROCm: `lemonade config set llamacpp.backend=rocm`. Consulta las [GPU de AMD compatibles](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lee la especificación completa de la API**: Lemonade admite finalización de chats, embeddings, transcripción de audio, generación de imágenes, texto a voz y más. Consulta la [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) para conocer todos los endpoints.

5. **Contribuye**: Lemonade es de código abierto. Consulta la [guía de contribución](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) y busca [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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