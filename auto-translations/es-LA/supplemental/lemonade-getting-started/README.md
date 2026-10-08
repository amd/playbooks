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

## Resumen

🍋 **Lemonade** es un servidor de IA local de código abierto que te permite ejecutar modelos de lenguaje grande (LLM), generadores de imágenes y modelos de audio directamente en tu propio hardware. Expone los modelos a través de la **API de OpenAI**, el estándar de la industria, por lo que cualquier aplicación que funcione con OpenAI puede funcionar instantáneamente con Lemonade. Al finalizar este playbook, estarás usando Lemonade para ejecutar modelos de forma local en tu máquina.

## Qué Aprenderás

Al finalizar este playbook podrás:

* **Instalar Lemonade Server** y verificar que esté en ejecución.
* **Descargar y chatear con un LLM** usando un solo comando.
* **Explorar la interfaz web** y probar distintas modalidades como visión, voz a texto y generación de imágenes.
* **Cambiar entre backends de GPU**, entre Vulkan y el software AMD ROCm™.
* **Crear una aplicación en Python** impulsada por un LLM local usando la API compatible con OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Ejecutar modelos en la unidad de procesamiento neuronal (NPU) de AMD** usando los modos de ejecución Hybrid y FLM en hardware AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Configuración de la Memoria

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar Actualizaciones de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de Requisitos Previos de Software

Antes de comenzar, asegúrate de tener:

- Una PC con **Windows 11** o una distribución de **Linux** compatible (Ubuntu 24.04+, Fedora, Debian)
- Se recomiendan **16 GB de RAM** para el modelo de ejecución usado en los Pasos 1 a 7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Se recomiendan **32 GB o más** si quieres usar el modelo de generación de código más grande del Paso 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **Entre ~4 y 30 GB de espacio libre en disco**, según los modelos que descargues. El modelo más grande de esta guía pesa unos 20 GB.
- **Python 3.10–3.13** (usado en la sección de la aplicación en Python)
- Una conexión a internet (por cable o inalámbrica)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcional] Una NPU AMD XDNA 2 (serie Ryzen AI 300/400/Max 300 o Z2 Extreme) con el controlador más reciente instalado desde [Instrucciones de Instalación del Software Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), si quieres ejecutar un modelo en la NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
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

## Conceptos Básicos — Cómo Funcionan los Servidores de IA Locales

Antes de ejecutar un modelo, vale la pena entender *por qué* las cosas están configuradas así. Lemonade es un **servidor de modelos local**, un proceso que carga modelos de IA en memoria y los expone a las aplicaciones a través de HTTP, tal como lo haría un servicio de IA en la nube.

### ¿Por Qué un Servidor?

| Beneficio | Qué Significa para Ti |
|---------|----------------------|
| **Integración simplificada** | Las aplicaciones se comunican con una sola API HTTP en lugar de lidiar con bibliotecas de C++ o Python específicas del hardware. |
| **Modelos compartidos** | Un solo modelo cargado puede servir a múltiples aplicaciones a la vez, sin copias duplicadas que consuman tu RAM. |
| **Portabilidad de la nube a lo local** | El código escrito para la API en la nube de OpenAI funciona con Lemonade cambiando una sola URL. |
| **Separación de responsabilidades** | El servidor se encarga de la gestión de modelos, el streaming y la tolerancia a fallos, de modo que los desarrolladores puedan enfocarse en su aplicación. |

### El Estándar de la API de OpenAI

Lemonade implementa la **API de OpenAI**, la misma interfaz que usan ChatGPT, Azure OpenAI y docenas de otros servicios. El modelo de conversación es simple:

| Rol | Quién Habla |
|------|---------------|
| **system** | Instrucciones para el modelo (persona, restricciones, herramientas disponibles) |
| **user** | Mensajes del humano (o la aplicación) hacia el modelo |
| **assistant** | Respuestas generadas por el modelo |

Esto significa que cualquier biblioteca o aplicación compatible con OpenAI puede comunicarse con Lemonade apuntándola a `http://localhost:13305/api/v1` mientras Lemonade Server esté en ejecución.

## Actividad Principal — Tu Primer Chat de IA Local

Descarguemos un LLM y conversemos con él, ejecutando la IA por completo en tu propia máquina.

### Paso 1: Descargar y Ejecutar un Modelo

Lemonade incluye una biblioteca de modelos curada. Comencemos con **Gemma-4-E2B-it**, un modelo compacto y capaz que incluye soporte de visión. Abre una terminal y ejecuta:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Este único comando hace tres cosas:

1. **Descarga** el modelo (~3 GB) desde Hugging Face, si aún no ha sido descargado. (Puede tardar un tiempo)
2. **Inicia** el proceso de Lemonade Server en el puerto 13305.
3. **Abre Lemonade App** para que puedas comenzar a chatear con el modelo.


<!-- @os:windows -->
En Windows, Lemonade App se inicia automáticamente y puedes comenzar a chatear de inmediato. Si instalaste el paquete `minimal.msi`, la aplicación no está incluida. Para comenzar a chatear, abre tu navegador web y ve a `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
En Linux, abre tu navegador y dirígete a `http://localhost:13305` para acceder a la aplicación web.
<!-- @os:end -->

Intenta escribir una pregunta:

```
What are three fun facts about lemons?
```

El modelo responderá directamente en la ventana de chat. **¡Felicidades! Ahora estás ejecutando un modelo de lenguaje grande de forma local.**

![Lemonade App con Logs mostrados](../../dependencies/assets/ChatwithLogs.png)

En el panel de Registros del Servidor (Server Logs) de Lemonade App, puedes encontrar datos de telemetría sobre el rendimiento del modelo después de cada respuesta. Por ejemplo:

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

Prueba a cambiar entre diferentes modalidades usando la pestaña **Model Manager** de la interfaz web, donde puedes explorar modelos por Recipe o por Category:

1. **Vision:** El modelo `Gemma-4-E2B-it-GGUF` que ya tienes cargado admite vision. Pega una imagen en el cuadro de chat y pídele al modelo que la describa.
2. **Generación de imágenes:** En la categoría Image, descarga un modelo de imagen como `SDXL-Turbo` desde el Model Manager, y luego usa el Lemonade Image Generator para escribir un prompt y generar una imagen de forma local.
3. **Audio:** En la categoría Audio, descarga un modelo de audio como `Whisper-Tiny`, que puede hacer speech-to-text. Proporciona una grabación de audio para transcribirla localmente. Para text-to-speech, prueba alguno de los modelos de la categoría Speech, como `kokoro-v1`.

![Multimodalidad con Lemonade](../../dependencies/assets/multi_modality.png)

### Paso 3: Prueba un modelo con un backend diferente

Si pasas el cursor sobre un modelo en la Lemonade App, verás un ícono de engranaje. Al hacer clic en él, podrás seleccionar opciones para el modelo, incluyendo la elección del backend deseado.

Por defecto, Lemonade usa Vulkan para la aceleración por GPU. Si tienes una GPU discreta de AMD compatible, puedes cambiar a ROCm.

![Seleccionar backend en Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Para administrar tus backends instalados, haz clic en el botón de backend en la columna de más a la izquierda.

Como alternativa, puedes especificar el backend usando el siguiente comando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

También puedes configurar tu backend predeterminado mediante la variable de entorno `LEMONADE_LLAMACPP` con los valores: `vulkan`, `rocm` o `cpu`.

---

## Profundizando más — Construye una aplicación impulsada por IA con Python

El verdadero poder de un servidor de IA local es que cualquier aplicación puede conectarse a él usando solo unas pocas líneas de código. Para demostrarlo, construyamos un **generador de tarjetas de estudio (flashcards)** pequeño pero funcional, al que le das un tema, genera las tarjetas y puedes ponerte a prueba de forma interactiva.

### Paso 4: Inicia el servidor

Verifica que el servidor de Lemonade esté en ejecución. Normalmente se inicia automáticamente en segundo plano tras la instalación. Para verificarlo, ejecuta:

```
lemonade status
```

Deberías ver un mensaje como: `Server is running on port 13305`.

Si el servidor no está en ejecución, inícialo abriendo la aplicación Lemonade. Usa el puerto predeterminado **13305** (puedes confirmarlo o seleccionarlo desde el ícono de la bandeja del sistema).

### Paso 5: Instala el cliente de Python de OpenAI

En una terminal, crea un venv e instala el cliente de Python de OpenAI usando los siguientes comandos:
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

### Paso 6: Construye la aplicación de flashcards

Descarguemos un modelo diferente para generar código: `Qwen3.5-35B-A3B-GGUF`. Es un modelo grande (~20 GB) y de alto rendimiento, más adecuado para sistemas con 32 GB o más de RAM. Si tienes menos RAM disponible, prueba con `Qwen3.5-9B-GGUF` (~6 GB) en su lugar.

Puedes descargarlo desde la interfaz o ejecutar lo siguiente:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Introduce el siguiente prompt en la interfaz de chat de Lemonade para generar código para una aplicación simple de flashcards.

Usaremos Qwen3.5-35B-A3B-GGUF (un modelo más grande, mejor para escribir código) para generar nuestra aplicación de Python, y la aplicación en sí llamará en tiempo de ejecución a Gemma-4-E2B-it-GGUF (el modelo más pequeño que ya descargaste). Luego puedes copiar el código a un archivo de tu elección para ejecutarlo en Python.

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

> **Consejo**: Seguimos prácticas de ingeniería estándar mediante una creación minuciosa del prompt y el uso de un sistema de dos modelos para optimizar recursos y velocidad.

Para tu comodidad, proporcionamos un ejemplo de salida en [`flashcards.py`](assets/flashcards.py). Puedes descargarlo a tu directorio si lo deseas. De cualquier forma, ahora deberías tener un archivo de Python listo para ejecutarse.

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

En aproximadamente 150 líneas de código, has construido una herramienta de estudio completamente funcional impulsada por un LLM local. No hay ninguna clave de API que administrar, ningún costo de uso y ningún dato sale nunca de tu máquina.

> **Idea clave:** Observa que la línea `client = OpenAI(base_url=...) ` es lo *único* que conecta esta aplicación con Lemonade en lugar de con la nube de OpenAI. El resto del código es idéntico al que escribirías contra cualquier servicio compatible con OpenAI. Si alguna vez has usado la librería de Python de OpenAI, ya sabes cómo construir aplicaciones con Lemonade.

### Qué demuestra esto

Esta pequeña aplicación pone en práctica varios patrones de integración del mundo real:

| Patrón | Dónde aparece |
|---------|-----------------|
| **Prompts de sistema** | El mensaje `"system"` le indica al LLM que genere un JSON estructurado |
| **Salida estructurada** | La aplicación analiza la respuesta del LLM como JSON para construir las flashcards |
| **Solicitudes sin estado** | Cada llamada a `generate_flashcards()` es independiente |
| **Manejo de errores** | El bloque `try/except` maneja de forma controlada los casos en que la salida del LLM no es un JSON válido |

Estos mismos patrones se adaptan a cualquier aplicación, como chatbots, asistentes de código, generadores de contenido o herramientas de automatización.

#### Desafío adicional

* Como desafío adicional, intenta actualizar la aplicación para que las flashcards se lean en voz alta al usuario, tomando como referencia el ejemplo que se proporciona [aquí](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Ejecución de modelos en la NPU (opcional)

Si tienes un Ryzen AI de la serie 300/400/Max 300 o Z2 Extreme, tu dispositivo cuenta con una **unidad de procesamiento neuronal (NPU)** integrada, un chip dedicado diseñado específicamente para cargas de trabajo de IA. Ejecutar modelos en la NPU es más eficiente en cuanto a energía que usar la GPU, lo que la hace ideal para tareas de IA en segundo plano, sesiones más largas y uso con batería.

Lemonade admite tres modos de ejecución en la NPU, todos transparentes detrás de la misma API de OpenAI:

| Modo | Cómo funciona | Receta | Modelos de ejemplo |
|------|-------------|--------|----------------|
| **Híbrido (NPU + iGPU)** | La NPU procesa el prompt, la iGPU genera los tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Solo NPU** | Toda la inferencia se ejecuta en la NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Usa el motor FastFlowLM en la NPU, optimizado para AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Requisitos

- Procesador **AMD Ryzen AI de la serie 300/400 o serie Z2**
- Para modelos **FLM**: El runtime de FLM se puede instalar desde la app de Lemonade, o Lemonade lo instalará automáticamente al ejecutar un modelo FLM. Para obtener más información sobre FastFlowLM, consulta [aquí](https://fastflowlm.com/docs/).


### Paso 8: Ejecutar un modelo híbrido

Los modelos híbridos dividen el trabajo entre la NPU y la iGPU para lograr un buen equilibrio entre velocidad y eficiencia. En la Lemonade App, selecciona un modelo de la lista `Ryzen AI LLM`, por ejemplo, `Qwen3-4B-Hybrid`, o ejecútalo con el siguiente comando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade detecta tu NPU automáticamente e instala el backend **Ryzen AI LLM**.

> **¿Qué sucede detrás de escena?** Cuando envías un mensaje, la NPU procesa todo tu prompt en paralelo (esto se llama "prefill"). Luego, la iGPU toma el control para generar la respuesta un token a la vez (esto se llama "decode"). Este enfoque híbrido aprovecha las fortalezas de cada chip.

### Paso 9: Ejecutar un modelo FLM

Los modelos FastFlowLM (FLM) están específicamente optimizados para la arquitectura NPU XDNA2 de AMD y pueden ser muy rápidos para su tamaño. Por ejemplo, selecciona `qwen3.5-4b-FLM` de la lista `FastFlowLM NPU` o usa el siguiente comando:

<!-- @os:windows -->
Para habilitar `FastFlowLM` en Windows:

* Abre el menú `Backends Manager`.
* Localiza la categoría de backend `FastFlowLM NPU`.
* Haz clic en Install NPU.
* Una vez completada la instalación, estarán disponibles ~36 modelos predeterminados en el menú desplegable de FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Cuando se abre la app `Lemonade` por primera vez, el backend `FastFlowNPU` no está habilitado de manera predeterminada.
La app local abrirá la página de instalación para guiarte durante la configuración.

Para habilitar `FastFlowLM` en Linux:

* Abre la app `Lemonade`.
* Visita la documentación [oficial de FLM](https://lemonade-server.ai/flm_npu_linux.html) y sigue los pasos de instalación de FLM seleccionando tu distribución de Linux.
* Habilita los backports según lo indicado en la página de instalación.
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
* Recomendado: cierra la `Lemonade App` y ábrela nuevamente para que se detecten los cambios.
* Recomendado: abre `Backends Manager` y haz clic en Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Tras una instalación exitosa, deberías ver que `flm:npu` se completó en el **Download Manager** dentro de la **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Luego puedes seleccionar cualquiera de los modelos FFLM disponibles y comenzar a usar el backend de NPU.

Para un modelo específico, descarga el modelo deseado desde la [página de modelos](https://fastflowlm.com/docs/models/qwen/) y valídalo usando el comando de Shell proporcionado en la documentación.
```
flm run qwen3.5-4b-FLM
```
o mediante 
```
lemonade run qwen3.5-4b-FLM
```

Los modelos FLM incluyen algunas de las arquitecturas más populares (Gemma 3, Qwen 3, Llama 3 y DeepSeek R1) y van desde menos de 1 GB hasta más de 13 GB.
Lemonade detecta tu NPU automáticamente e instala el backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Consejo:** Para obtener el mejor rendimiento de la NPU, habilita el modo turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Cambio de modelos

La app de tarjetas didácticas del Paso 6 también funciona con modelos de NPU; solo cambia el nombre del modelo:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Próximos pasos

Ya tienes un servidor de IA local ejecutándose en tu propio hardware. Aquí te mostramos hacia dónde ir a continuación:

1. **Conecta tus aplicaciones favoritas**: Lemonade funciona de inmediato con [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) y [muchas más](https://lemonade-server.ai/marketplace).

2. **Explora más modelos**: Recorre la [biblioteca de modelos](https://lemonade-server.ai/docs/server/server_models/) completa para encontrar modelos optimizados para programación, razonamiento, visión y más. Usa la Lemonade App o `lemonade list` para ver qué hay disponible.

3. **Desbloquea la aceleración de GPU con ROCm**: Si tienes una GPU de AMD compatible, cambia al backend de ROCm: `lemonade config set llamacpp.backend=rocm`. Consulta las [GPU de AMD compatibles](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Lee la especificación completa de la API**: Lemonade admite finalización de chats, embeddings, transcripción de audio, generación de imágenes, texto a voz y más. Consulta la [Especificación del servidor](https://lemonade-server.ai/docs/server/server_spec/) para ver todos los endpoints.

5. **Contribuye**: Lemonade es de código abierto. Revisa la [guía de contribución](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) y busca [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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