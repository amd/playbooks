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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requiere un mínimo de **32GB** de memoria del sistema.
<!-- @device:end -->

## Descripción general

Los agentes de código son herramientas poderosas que empoderan a los desarrolladores a través de la colaboración con agentes de IA respaldados por Modelos de Lenguaje de Gran Escala (LLMs). Pueden integrarse en el entorno de desarrollo, como la terminal o VS Code, permitiendo una integración fluida en el flujo de trabajo de un desarrollador.

Este tutorial demuestra cómo usar Cline, VS Code y LM Studio para ejecutar un agente de código completamente en tu máquina local.

## Lo que aprenderás

* Cómo ejecutar VS Code con el agente de código Cline para ayudar en tareas de ingeniería de software.
* Cómo configurar Cline para comunicarse con LM Studio para la inferencia local de agentes de código.
* Cómo usar agentes de código locales para resolver tareas reales de ingeniería de software.

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software
> **Nota**: Si VS Code no está instalado, puedes instalarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

<!-- @require:lmstudio,vscode -->

## Iniciar y configurar LM Studio

Usaremos LM Studio para servir el LLM que impulsa al agente de código.

- En la barra de búsqueda, busca `LM Studio` y abre la aplicación. Te encontrarás con la siguiente pantalla.

![Pantalla inicial de LM Studio](assets/initial-lm-studio.png)

A continuación, debemos cargar el LLM en el sistema. Vamos a usar el modelo `Qwen3-Coder-30B-A3B` con una longitud de contexto grande. (Usa la pestaña Model para instalarlo si aún no lo has hecho).
- Haz clic en la barra de búsqueda en la parte superior de la ventana de LM Studio o presiona `CTRL+L`. Activa el interruptor `Manually choose model load parameters` y luego haz clic en el modelo Qwen3-Coder-30B-A3B.
- Cambia la longitud de contexto de `4096` a `32768`, y asegúrate de que `GPU Offload` esté al máximo. Luego, haz clic en `Load Model`

![Selección del modelo](assets/model-list-zoomed.png)

Usamos una longitud de contexto grande para que el agente pueda procesar bases de código grandes y recordar los cambios que se han realizado.

![Configuración del modelo](assets/selecting-model-zoomed.png)

A continuación, debemos habilitar el servidor de LM Studio.
- Haz clic en la pestaña Developer o presiona `CTRL+2` en LM Studio a la izquierda.
- Verifica el interruptor de estado y asegúrate de que esté configurado en `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Estado del servidor](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Iniciar y configurar VS Code

Instalaremos la extensión Cline en VS Code y la conectaremos al servidor de LM Studio que acabamos de crear.
- En la barra de búsqueda, busca `VS Code` y abre la aplicación.
- Haz clic en el ícono `Extensions` en la columna izquierda de VS Code y busca `Cline`. Luego, haz clic en el botón `Install`.

![Instalación de la extensión Cline](assets/installing-cline-vscode-extension.png)

- Debería aparecer un ícono de Cline a la izquierda. Haz clic en él para abrir Cline. Aparecerá una ventana preguntando `How will you use Cline?` Como vamos a usar un LLM local ejecutándose a través de LM Studio, selecciona `Bring my own API Key` y presiona `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Creación de cuenta](assets/cline-how-will-you-use-cline-zoomed.png)

A continuación, necesitamos configurar Cline para que se comunique con el servidor de LM Studio que configuramos.
- Establece el API Provider como `LM Studio` y el modelo como `Qwen3-Coder-30B-A3B-GGUF`.

>**Consejo**: Es posible que haya modelos más nuevos disponibles. Considera descargar y cambiar a los modelos Qwen3.6 si lo deseas.


![Configuración del modelo](assets/cline-model-configuration-zoomed.png)

## Creando tu primer proyecto

¡Usemos nuestro agente local para crear un sitio web! Abre VSCode en un directorio de tu elección donde Cline creará los archivos.
- Para hacer esto, ve a `File -> Open Folder` en la parte superior izquierda de VS Code y elige una carpeta como `Documents`.

![Carpeta vacía de VS Code](assets/open-cline-test.png)

Ahora estamos listos para darle instrucciones al agente de código local.
- Haz clic en la extensión Cline en la columna izquierda e ingresa un mensaje para poner en marcha al agente. Como ejemplo, usemos el siguiente mensaje:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

El agente comenzará entonces a crear archivos según el mensaje. Como usuario, puedes observar cómo se genera el código en VS Code como se muestra a continuación. Es posible que debas hacer clic en `Save` cada vez que Cline quiera crear un archivo.

![Generación de código con Cline](assets/cline-code-generation.png)

Después de generar el software, el agente ha terminado y puedes ejecutar la aplicación. En este caso, el agente escribió en tres archivos: `index.html`, `script.js` y `styles.css`. Simplemente haciendo doble clic en el archivo HTML podemos cargar e interactuar con el sitio web generado.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->
## Próximos pasos

Después de generar el sitio web, puedes continuar trabajando con Cline para mejorarlo. Dos posibles mejoras son:

- **Documentación**: Con solo indicarle al agente `Add a README` es suficiente para que genere un archivo `README.md` que documente el sitio web.
- **Animación**: Indícale al modelo `Add an animation that visually represents a large language model running on a laptop.` para generar una animación en el sitio web.

Alentamos al lector a intentar generar otras aplicaciones usando esta configuración. A continuación, algunos ejemplos divertidos que hemos probado:

- **Juegos de arcade retro**: Prueba otros prompts. También puede ser divertido que el agente cree juegos de estilo retro en Python usando el paquete `PyGame` con el siguiente prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Análisis de datos**: Un área donde los agentes de codificación son particularmente útiles es la de scripting y análisis de datos. Este es un prompt para mostrar la capacidad del modelo local de generar software de análisis de datos para la visualización de precios de acciones:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Recursos

A continuación, encontrarás algunos recursos adicionales para aprender más sobre los agentes de codificación, Cline y la ejecución de cargas de trabajo en 

* Más información sobre la asociación e integración de AMD con LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog de AMD que explica cómo ejecutar Cline en tarjetas gráficas AMD Ryzen™ AI y Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog de Cline sobre cómo ejecutar agentes de codificación localmente en PC con IA: https://cline.bot/blog/local-models-amd