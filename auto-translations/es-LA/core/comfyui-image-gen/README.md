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

ComfyUI es una interfaz potente basada en nodos para Stable Diffusion y otros modelos de difusión. A diferencia de las interfaces tradicionales de texto a imagen con simples cuadros de prompt, ComfyUI expone todo el pipeline de generación de imágenes como un grafo visual, dándote control detallado sobre cada paso, desde la codificación de texto hasta la manipulación del espacio latente y la decodificación final.

Este tutorial te enseña cómo usar ComfyUI con el modelo Z Image Turbo en tu GPU para generar imágenes de alta calidad con IA.

## Qué aprenderás

- Cómo iniciar ComfyUI y cargar la plantilla de Z-Image Turbo
- Comprender los componentes del pipeline de difusión
- Generar imágenes y ajustar los parámetros de generación
- Guardar y compartir workflows

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto tenga efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Crear un entorno virtual
En Linux, abre una terminal en el directorio de tu elección y ejecuta el siguiente comando para crear un venv:

<!-- @test:id=create-venv-linux timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv comfyui-env
source comfyui-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source comfyui-env/bin/activate" -->
<!-- @device:end -->

<!-- @require:driver,pytorch,comfyui -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=comfyui-desktop-workspace-present-windows timeout=60 hidden=True -->
```powershell
# The new Comfy Desktop (since June 2026) installs into %LOCALAPPDATA%\Comfy-Desktop\
# Layout: ComfyUI-Installs\<name>\ComfyUI\ holds main.py + .venv
#         ComfyUI-Shared\ holds the shared model library
$instBase  = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI"
$comfyRoot = Join-Path $instBase "ComfyUI"
$py        = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy    = Join-Path $comfyRoot "main.py"
$sharedModels = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Shared\models"

if (-not (Test-Path $instBase))     { throw "Comfy Desktop instance not found at: $instBase" }
if (-not (Test-Path $comfyRoot))    { throw "ComfyUI source not found at: $comfyRoot" }
if (-not (Test-Path $py))           { throw "ComfyUI venv python not found: $py" }
if (-not (Test-Path $mainPy))       { throw "ComfyUI main.py not found: $mainPy" }
if (-not (Test-Path $sharedModels)) { throw "Comfy Desktop shared models dir not found: $sharedModels" }

Write-Host "OK: instance root: $instBase"
Write-Host "OK: ComfyUI source: $comfyRoot"
Write-Host "OK: Python: $py"
Write-Host "OK: main.py: $mainPy"
Write-Host "OK: shared models: $sharedModels"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-clone-linux timeout=300 hidden=True -->
```bash
set -euo pipefail
if [ -d "ComfyUI/.git" ]; then
 (cd ComfyUI && git fetch --all && git reset --hard origin/master)
else
 git clone https://github.com/Comfy-Org/ComfyUI.git
fi
cd ComfyUI
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-requirements-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r ./ComfyUI/requirements.txt
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=comfyui-sync-requirements-windows timeout=600 hidden=True -->
```powershell
$comfyRoot = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py  = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$req = Join-Path $comfyRoot "requirements.txt"

if (-not (Test-Path $py))  { throw "ComfyUI venv python not found: $py" }
if (-not (Test-Path $req)) { throw "ComfyUI requirements.txt not found: $req" }

& $py -m pip install --upgrade --force-reinstall --no-cache-dir comfyui-frontend-package
if ($LASTEXITCODE -ne 0) { throw "Failed to install comfyui-frontend-package into workspace venv." }

& $py -c "import importlib.metadata as m; print(m.version('comfyui-frontend-package'))"
if ($LASTEXITCODE -ne 0) { throw "comfyui-frontend-package metadata still missing after install." }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows --> 
<!-- @test:id=comfyui-backend-usable-windows timeout=120 hidden=True -->
```powershell
$py = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Missing ComfyUI venv python: $py" }

& $py -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('hip', getattr(torch.version,'hip',None));"
if ($LASTEXITCODE -ne 0) { throw "Torch import/check failed in ComfyUI venv." }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-install-rocm-torch-linux timeout=900 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

python - <<'PY'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"ROCm/HIP version: {getattr(torch.version, 'hip', None)}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-verify-torch-linux timeout=120 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
python -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('hip', getattr(torch.version,'hip',None));"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows --> 
<!-- @test:id=comfyui-populate-models-from-cache-windows timeout=600 hidden=True -->
```powershell
# The new Comfy Desktop (since June 2026) uses a shared model library separate from the ComfyUI source.
# Models are served from %LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Shared\models\
# as configured in shared_model_paths.yaml.
$modelsRoot = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Shared\models"
if (-not (Test-Path $modelsRoot)) { throw "Comfy Desktop shared models dir not found: $modelsRoot" }

$cacheDiff = "C:\ModelCache\ComfyUI\models\diffusion_models\z_image_turbo_bf16.safetensors"
$cacheTE   = "C:\ModelCache\ComfyUI\models\text_encoders\qwen_3_4b.safetensors"
$cacheVAE  = "C:\ModelCache\ComfyUI\models\vae\ae.safetensors"

if (-not (Test-Path $cacheDiff)) { throw "models missing on runner: $cacheDiff" }
if (-not (Test-Path $cacheTE))   { throw "models missing on runner: $cacheTE" }
if (-not (Test-Path $cacheVAE))  { throw "models missing on runner: $cacheVAE" }

New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "diffusion_models")
New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "text_encoders")
New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "vae")

Copy-Item -Force $cacheDiff (Join-Path $modelsRoot "diffusion_models\z_image_turbo_bf16.safetensors")
Copy-Item -Force $cacheTE   (Join-Path $modelsRoot "text_encoders\qwen_3_4b.safetensors")
Copy-Item -Force $cacheVAE  (Join-Path $modelsRoot "vae\ae.safetensors")

Write-Host "OK: models copied into $modelsRoot"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-populate-models-from-cache-linux timeout=600 hidden=True -->
```bash
cd ComfyUI
cache_diff="/opt/model_cache/ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors"
cache_te="/opt/model_cache/ComfyUI/models/text_encoders/qwen_3_4b.safetensors"
cache_vae="/opt/model_cache/ComfyUI/models/vae/ae.safetensors"
test -f "$cache_diff" || (echo "models missing on runner: $cache_diff" && exit 1)
test -f "$cache_te" || (echo "models missing on runner: $cache_te" && exit 1)
test -f "$cache_vae" || (echo "models missing on runner: $cache_vae" && exit 1)
mkdir -p models/diffusion_models models/text_encoders models/vae
cp -f "$cache_diff" models/diffusion_models/z_image_turbo_bf16.safetensors
cp -f "$cache_te" models/text_encoders/qwen_3_4b.safetensors
cp -f "$cache_vae" models/vae/ae.safetensors
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=comfyui-server-up-windows timeout=300 hidden=True -->
```powershell
$comfyRoot   = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py          = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy      = Join-Path $comfyRoot "main.py"
$sharedPaths = Join-Path $env:APPDATA "Comfy Desktop\shared_model_paths.yaml"

$proc = Start-Process -FilePath $py `
 -ArgumentList "`"$mainPy`" --listen 127.0.0.1 --port 8188 --extra-model-paths-config `"$sharedPaths`"" `
 -WorkingDirectory $comfyRoot `
 -NoNewWindow -PassThru

try {
 $ok = $false
 for ($i=0; $i -lt 60; $i++) {
   $resp = curl.exe -s --max-time 2 http://127.0.0.1:8188/
   if ($LASTEXITCODE -eq 0 -and $resp) { $ok = $true; break }
   Start-Sleep -Seconds 1
 }
 if (-not $ok) { throw "ComfyUI server not reachable at http://127.0.0.1:8188/" }
 Write-Host "OK: ComfyUI server is reachable!"
} finally {
 Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-server-up-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
python ./ComfyUI/main.py --listen 127.0.0.1 --port 8188 >/tmp/comfyui.log 2>&1 &
PID=$!

cleanup() {
 kill -9 "$PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

ok=0
for i in $(seq 1 60); do
 resp="$(curl -s --max-time 2 http://127.0.0.1:8188/ || true)"
 if [ -n "$resp" ]; then ok=1; break; fi
 sleep 1
done

if [ "$ok" -ne 1 ]; then
 echo "ComfyUI server not reachable at http://127.0.0.1:8188/"
 tail -n 200 /tmp/comfyui.log || true
 exit 1
fi

echo "OK: ComfyUI server is reachable!"
```
<!-- @test:end --> 
<!-- @os:end -->


## Iniciar ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Para iniciar ComfyUI en Windows, haz clic en el Lanzador de Escritorio de ComfyUI que se encuentra en tu Escritorio. Sigue los pasos para instalar la versión local con AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Luego, haz clic en el botón ComfyUI en la parte superior central de la aplicación. Esto abrirá una pestaña de configuración. Abre la pestaña Storage y asegúrate de que las rutas estén configuradas de la siguiente manera para acceder a los modelos preinstalados.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
En AMD Ryzen™ AI Halo, ComfyUI se ejecuta en un contenedor prediseñado que no requiere configuración adicional de Python.

Para iniciar ComfyUI en Linux, haz clic en el acceso directo de ComfyUI en la barra de tareas. Debería abrirse automáticamente en una ventana del navegador.
>**Consejo**: ComfyUI y sus modelos se almacenan en `~/.local/share/ComfyUI/models`. Aquí es donde puedes agregar manualmente workflows o nuevos modelos.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Para iniciar ComfyUI en Windows, simplemente haz clic en el acceso directo de ComfyUI en tu Escritorio.
<!-- @os:end -->

<!-- @os:linux -->

Para iniciar ComfyUI:

1. Asegúrate de estar dentro del directorio de ComfyUI. 
2. Ejecuta `python3 main.py --use-pytorch-cross-attention`

ComfyUI inicia un servidor web local. Abre tu navegador en `http://127.0.0.1:8188` para acceder a la interfaz.

> **Consejo**: Mantén abierta la ventana de la terminal mientras usas ComfyUI. Cerrarla detendrá el servidor.
<!-- @os:end -->
<!-- @device:end -->


## Encontrar la plantilla de Z-Image Turbo

Antes de generar imágenes, necesitas cargar la plantilla de Z-Image Turbo. Así es como la encuentras:

1. **Mira en el borde izquierdo de la pantalla**: hay una barra de herramientas vertical que recorre de arriba a abajo el lado más a la izquierda de la aplicación.

2. **Encuentra el ícono de carpeta**: en esa barra de herramientas izquierda, busca un ícono que parezca una carpeta. Al pasar el cursor sobre él, se etiqueta como "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Haz clic en el ícono de carpeta**: esto abre el panel de Templates.

4. **Busca "Z-Image Turbo"**: usa la barra de búsqueda o desplázate por las plantillas disponibles para encontrar el workflow Z-Image Turbo Text To Image, luego haz clic para cargarlo.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Descarga de modelos

<!-- @require:comfyui-models -->

## Entendiendo la interfaz

Cuando se carga la plantilla de Z-Image Turbo, verás un lienzo con 2 nodos principales. El primer nodo se llama 'Text to Image (Z-Image-Turbo)', y el segundo nodo es para visualizar la imagen. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


En el nodo Z-Image, haz clic en el botón superior derecho para expandir el Nodo y ver el subgrafo.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Componentes del pipeline

El workflow de Z-Image Turbo usa cuatro componentes clave de modelo que trabajan juntos:

| Componente | Función |
|-----------|------|
| **Codificador de texto** (Qwen 3 4B) | Convierte tu prompt de texto en embeddings que el modelo de difusión entiende |
| **Modelo de difusión** (Z-Image Turbo) | La red neuronal central que elimina ruido de forma iterativa de las representaciones latentes hasta convertirlas en imágenes |
| **VAE** (Autocodificador Variacional) | Codifica imágenes hacia/desde el espacio latente (decodifica los latentes finales en píxeles) |
| **LoRA** (opcional) | Adaptadores ligeros que modifican el estilo o el tema sin volver a entrenar el modelo base |

Cada nodo en el workflow corresponde a uno de estos componentes. Los datos fluyen de izquierda a derecha: texto → embeddings → eliminación de ruido guiada → latentes → imagen final.
## Generando tu primera imagen

El modelo Z-Image Turbo ya está cargado. Para generar una imagen:

1. **Ingresa tu prompt** en el nodo principal de Z-Image. Sé descriptivo. Aquí tienes un ejemplo:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opcional)**: Confirma o ajusta cualquier otra configuración específica dentro del subgrafo.
3. **Haz clic en el botón azul "Run Workflow"** en la esquina derecha (o presiona `Ctrl+Enter`)
4. Observa cómo se resaltan los nodos a medida que se ejecuta cada paso

La ejecución completa del flujo de trabajo debería tardar menos de 30 segundos. Tu imagen generada aparece en el nodo **Save Image** y se guarda en la carpeta `output/`.

<!-- @os:windows -->
<!-- @test:id=comfyui-generate-zimage-windows timeout=1200 hidden=True -->
```powershell
$comfyRoot      = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py             = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy         = Join-Path $comfyRoot "main.py"
$sharedPaths    = Join-Path $env:APPDATA "Comfy Desktop\shared_model_paths.yaml"

$proc = Start-Process -FilePath $py `
 -ArgumentList "`"$mainPy`" --listen 127.0.0.1 --port 8188 --extra-model-paths-config `"$sharedPaths`"" `
 -WorkingDirectory $comfyRoot `
 -NoNewWindow -PassThru

try {
 $ok = $false
 for ($i=0; $i -lt 60; $i++) {
   $resp = curl.exe -s --max-time 2 http://127.0.0.1:8188/
   if ($LASTEXITCODE -eq 0 -and $resp) { $ok = $true; break }
   Start-Sleep -Seconds 1
 }
 if (-not $ok) { throw "ComfyUI server not ready on http://127.0.0.1:8188/" }

 # run submit script from assets working dir (where image_z_image_turbo.json should exist)
 @'
import json, time, urllib.request, urllib.error, sys, os
wf_path = "image_z_image_turbo.json"
if not os.path.exists(wf_path):
 raise SystemExit(f"Missing workflow json in working dir: {os.getcwd()} -> {wf_path}")
with open(wf_path, "r", encoding="utf-8") as f:
 workflow = json.load(f)
data = json.dumps({"prompt": workflow}).encode("utf-8")
req = urllib.request.Request(
 "http://127.0.0.1:8188/prompt",
 data=data,
 headers={"Content-Type":"application/json"},
 method="POST",
)
try:
 with urllib.request.urlopen(req, timeout=60) as r:
   prompt_id = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
 body = e.read().decode("utf-8", "replace")
 print("HTTPError", e.code, e.reason)
 print(body)
 sys.exit(1)
except Exception as e:
  print("Request failed:", repr(e))
  sys.exit(1)

for _ in range(600):
 with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=60) as r:
   hist = json.load(r)
 entry = hist.get(prompt_id, {})
 if entry.get("outputs"):
   print("OK, output image generated!")
   sys.exit(0)
 time.sleep(1)

print("No outputs after waiting.")
sys.exit(1)
'@ | & $py -
 if ($LASTEXITCODE -ne 0) { throw "Workflow submit/generation failed" }

} finally {
 Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:linux --> 
<!-- @test:id=comfyui-generate-zimage-linux timeout=1200 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
# start server
python ./ComfyUI/main.py --listen 127.0.0.1 --port 8188 >/tmp/comfyui.log 2>&1 &
PID=$!

cleanup() {
 kill -9 "$PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# wait ready
ok=0
for i in $(seq 1 60); do
 resp="$(curl -s --max-time 2 http://127.0.0.1:8188/ || true)"
 if [ -n "$resp" ]; then ok=1; break; fi
 sleep 1
done

if [ "$ok" -ne 1 ]; then
 echo "ComfyUI server not ready"
 tail -n 200 /tmp/comfyui.log || true
 exit 1
fi

# submit workflow json from assets folder (one level up from ComfyUI)
python - <<'PY'
import json, time, urllib.request, urllib.error, sys, os

wf_path = "image_z_image_turbo.json"
if not os.path.exists(wf_path):
 raise SystemExit(f"Missing workflow json in working dir: {os.getcwd()} -> {wf_path}")

with open(wf_path, "r", encoding="utf-8") as f:
 workflow = json.load(f)

data = json.dumps({"prompt": workflow}).encode("utf-8")
req = urllib.request.Request(
 "http://127.0.0.1:8188/prompt",
 data=data,
 headers={"Content-Type":"application/json"},
 method="POST",
)

try:
 with urllib.request.urlopen(req, timeout=60) as r:
   prompt_id = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
 body = e.read().decode("utf-8", "replace")
 print("HTTPError", e.code, e.reason)
 print(body)
 sys.exit(1)

for _ in range(600):
 with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=60) as r:
   hist = json.load(r)
 entry = hist.get(prompt_id, {})
 if entry.get("outputs"):
   print("OK, output image generated!")
   sys.exit(0)
 time.sleep(1)

print("No outputs after waiting.")
sys.exit(1)
PY
```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows -->
<!-- @test:id=comfyui-output-exists-windows timeout=60 hidden=True -->
```powershell
$outDir = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\output"

# ComfyUI saves into date-stamped subdirectories, so recurse to find PNGs
$files = Get-ChildItem -Path $outDir -Filter *.png -File -Recurse -ErrorAction SilentlyContinue
if (-not $files) {
 throw "No PNG files found under: $outDir"
}
$files | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { $_.FullName }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-output-exists-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
ls -1 ComfyUI/output/*.png >/dev/null 2>&1 || (echo "No PNG files found in ComfyUI/output" && exit 1)
ls -1t ComfyUI/output/*.png | head -n 5
```
<!-- @test:end --> 
<!-- @os:end -->


## Ajustando los parámetros de generación

### Configuración de KSampler

El nodo KSampler controla el proceso central de difusión:

| Parámetro | Qué controla | Recomendado para Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Número de iteraciones de eliminación de ruido | 4–10 (los modelos turbo están destilados para requerir menos pasos) |
| **cfg** | Escala de guía sin clasificador—qué tan estrictamente se sigue el prompt | 1.0–2.0 (los modelos turbo usan una guía muy baja) |
| **sampler_name** | Algoritmo de eliminación de ruido | `euler` y `res_multistep` funcionan bien para modelos turbo |
| **scheduler** | Curva del programa de ruido | `normal` o `simple` |
| **seed** | Semilla aleatoria para reproducibilidad | Establece valores fijos para iterar sobre una composición |

### Tamaño de imagen

Para ajustar las dimensiones de salida, busca el nodo **Empty Latent Image** y modifica **width** y **height**. Mantén las dimensiones en 1024 píxeles o menos en el lado más largo para una calidad óptima.

### ModelSamplingAuraFlow

El nodo **ModelSamplingAuraFlow** es un modificador de muestreo especializado que ajusta cómo el proceso de difusión maneja la programación del ruido. Verás este nodo conectado a la salida del modelo en el flujo de trabajo de Z-Image Turbo.

| Parámetro | Qué controla | Valores recomendados |
|-----------|------------------|-------------------|
| **shift** | Ajusta el tiempo del programa de ruido—valores más altos desplazan más refinamiento de detalle hacia pasos posteriores | 1.0–4.0 (el valor predeterminado es 3.0) |

Cuándo ajustar **shift**:

- **Valores más bajos (1.0–2.0)**: Convergencia más rápida, ideal para composiciones simples
- **Valores más altos (3.0–4.0)**: Refinamiento más gradual, puede mejorar los detalles finos en escenas complejas

El método de muestreo AuraFlow está diseñado específicamente para modelos de coincidencia de flujo (flow-matching) como Z-Image Turbo, garantizando una distribución de ruido adecuada durante todo el proceso de generación.

## Trabajando con flujos de trabajo

### Guardando flujos de trabajo

Haz clic en el botón **Save** en el menú para exportar tu flujo de trabajo como un archivo JSON. Esto captura:

- Todos los nodos y sus parámetros
- Todas las conexiones entre nodos
- El texto del prompt actual

### Cargando flujos de trabajo

Arrastra un archivo JSON de flujo de trabajo al lienzo, o usa **Load** desde el menú. El flujo de trabajo de Z-Image Turbo que ves de forma predeterminada se carga desde un archivo de flujo de trabajo guardado.

### Compartiendo flujos de trabajo

Los flujos de trabajo son autocontenidos—comparte el archivo JSON con colegas, y ellos podrán reproducir exactamente tu configuración. Esto hace que ComfyUI sea excelente para la experimentación colaborativa.

## Próximos pasos

- **Explora los nodos LoRA**: Aplica adaptadores de estilo o de sujeto sin necesidad de reentrenamiento
- **Agrega prompts negativos**: Conecta un segundo nodo CLIP Text Encode a la entrada de condicionamiento **negative** de KSampler para guiar al modelo a evitar características no deseadas como desenfoque, artefactos o marcas de agua
- **Crea flujos de trabajo personalizados**: Encadena múltiples generaciones, agrega escalado o crea variaciones de imágenes
- **Explora flujos de trabajo de la comunidad**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) tiene muchos flujos de trabajo listos para usar

La fortaleza de ComfyUI es la experimentación: conecta los nodos de diferentes maneras, ajusta parámetros y observa cómo cada cambio afecta el resultado. Esta exploración práctica desarrolla la intuición sobre cómo funcionan los modelos de difusión.

Para más información, consulta la [Documentación de ComfyUI](https://docs.comfy.org/).