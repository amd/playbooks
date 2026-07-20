<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> В этом руководстве используются специальные теги, которые GitHub не может отобразить. Пожалуйста, перейдите на сайт [amd.com/playbooks](https://amd.com/playbooks), чтобы корректно просмотреть этот материал.
<!-- @github-only:end -->

## Обзор

ComfyUI — это мощный узловой (node-based) интерфейс для Stable Diffusion и других диффузионных моделей. В отличие от традиционных интерфейсов «текст-в-изображение» с простым полем для промпта, ComfyUI представляет весь конвейер генерации изображений в виде визуального графа, предоставляя точный контроль над каждым этапом — от кодирования текста до манипуляций в латентном пространстве и финального декодирования.

Это руководство научит вас использовать ComfyUI с моделью Z Image Turbo на вашем GPU для генерации высококачественных изображений с помощью ИИ.

## Чему вы научитесь

- Как запустить ComfyUI и загрузить шаблон Z-Image Turbo
- Понимание компонентов диффузионного конвейера
- Генерация изображений и настройка параметров генерации
- Сохранение и обмен рабочими процессами

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления изменений в силу необходимо выйти из системы и войти снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Создание виртуального окружения
В Linux откройте терминал в выбранном вами каталоге и выполните следующую команду для создания venv:

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


## Запуск ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Чтобы запустить ComfyUI в Windows, нажмите на значок ComfyUI Desktop Launcher на рабочем столе. Следуйте шагам для установки локальной версии с AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Затем нажмите кнопку ComfyUI в верхней средней части приложения. Откроется вкладка настроек. Откройте вкладку Storage и убедитесь, что пути указаны следующим образом для доступа к предустановленным моделям.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Чтобы запустить ComfyUI в Linux, нажмите на ярлык ComfyUI на панели задач. Он должен автоматически открыться в окне браузера.
>**Совет**: ComfyUI и его модели хранятся по пути `~/.local/share/ComfyUI/models`. Именно сюда вы можете вручную добавлять рабочие процессы или новые модели.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Чтобы запустить ComfyUI в Windows, просто нажмите на ярлык ComfyUI на рабочем столе.
<!-- @os:end -->

<!-- @os:linux -->

Чтобы запустить ComfyUI:

1. Убедитесь, что вы находитесь в каталоге ComfyUI. 
2. Выполните `python3 main.py --use-pytorch-cross-attention`

ComfyUI запускает локальный веб-сервер. Откройте браузер и перейдите по адресу `http://127.0.0.1:8188` для доступа к интерфейсу.

> **Совет**: Держите окно терминала открытым во время использования ComfyUI. Закрытие окна остановит сервер.
<!-- @os:end -->
<!-- @device:end -->


## Поиск шаблона Z-Image Turbo

Прежде чем генерировать изображения, необходимо загрузить шаблон Z-Image Turbo. Вот как его найти:

1. **Посмотрите на крайний левый край экрана** — там находится вертикальная панель инструментов, проходящая сверху вниз по левому краю приложения.

2. **Найдите значок папки** — на этой левой панели найдите значок, похожий на папку. При наведении на него отображается подпись «Templates».

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Нажмите на значок папки** — откроется панель Templates.

4. **Найдите «Z-Image Turbo»** — используйте строку поиска или прокрутите список доступных шаблонов, чтобы найти рабочий процесс Z-Image Turbo Text To Image, затем нажмите, чтобы загрузить его.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Загрузка моделей

<!-- @require:comfyui-models -->

## Знакомство с интерфейсом

После загрузки шаблона Z-Image Turbo вы увидите холст с 2 основными узлами. Первый узел называется «Text to Image (Z-Image-Turbo)», а второй предназначен для просмотра изображения. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


На узле Z-Image нажмите кнопку в правом верхнем углу, чтобы развернуть узел и увидеть подграф.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Компоненты конвейера

Рабочий процесс Z-Image Turbo использует четыре ключевых компонента модели, работающих совместно:

| Компонент | Роль |
|-----------|------|
| **Текстовый кодировщик** (Qwen 3 4B) | Преобразует ваш текстовый промпт в эмбеддинги, понятные диффузионной модели |
| **Диффузионная модель** (Z-Image Turbo) | Основная нейронная сеть, итеративно очищающая латентные представления от шума и превращающая их в изображения |
| **VAE** (вариационный автокодировщик) | Кодирует изображения в латентное пространство и обратно (декодирует финальные латенты в пиксели) |
| **LoRA** (опционально) | Легковесные адаптеры, изменяющие стиль или сюжет без переобучения базовой модели |

Каждый узел в рабочем процессе соответствует одному из этих компонентов. Данные проходят слева направо: текст → эмбеддинги → управляемое устранение шума → латенты → финальное изображение.

## Генерация первого изображения

Модель Z-Image Turbo уже загружена. Чтобы сгенерировать изображение:

1. **Введите ваш промпт** в основном узле Z-Image. Будьте описательны. Вот пример:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Опционально)**: Подтвердите или измените любые другие настройки внутри подграфа.
3. **Нажмите синюю кнопку «Run Workflow»** в правом углу (или нажмите `Ctrl+Enter`)
4. Наблюдайте, как узлы подсвечиваются по мере выполнения каждого шага

Выполнение всего рабочего процесса должно завершиться менее чем за 30 секунд. Сгенерированное изображение появится в узле **Save Image** и будет сохранено в папке `output/`.

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


## Настройка параметров генерации
### Настройки KSampler

Узел KSampler управляет основным процессом диффузии:

| Параметр | Что контролирует | Рекомендуется для Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Количество итераций удаления шума | 4–10 (turbo-модели дистиллированы для меньшего числа шагов) |
| **cfg** | Масштаб guidance без классификатора — насколько точно следовать промпту | 1.0–2.0 (turbo-модели используют очень низкое значение guidance) |
| **sampler_name** | Алгоритм удаления шума | `euler` и `res_multistep` хорошо подходят для turbo-моделей |
| **scheduler** | Кривая расписания шума | `normal` или `simple` |
| **seed** | Случайное зерно для воспроизводимости | Устанавливайте фиксированные значения для итеративной работы над композицией |

### Размер изображения

Чтобы изменить размеры вывода, найдите узел **Empty Latent Image** и измените **width** и **height**. Для оптимального качества сохраняйте размеры не более 1024 пикселей по большей стороне.

### ModelSamplingAuraFlow

Узел **ModelSamplingAuraFlow** — это специализированный модификатор сэмплирования, который регулирует то, как процесс диффузии обрабатывает расписание шума. Вы увидите этот узел подключённым к выходу модели в рабочем процессе Z-Image Turbo.

| Параметр | Что контролирует | Рекомендуемые значения |
|-----------|------------------|-------------------|
| **shift** | Регулирует время расписания шума — более высокие значения смещают больше уточнения деталей на поздние шаги | 1.0–4.0 (значение по умолчанию — 3.0) |

Когда стоит настраивать **shift**:

- **Низкие значения (1.0–2.0)**: более быстрая сходимость, хорошо подходит для простых композиций
- **Высокие значения (3.0–4.0)**: более постепенное уточнение, может улучшить мелкие детали в сложных сценах

Метод сэмплирования AuraFlow специально разработан для моделей с flow-matching, таких как Z-Image Turbo, обеспечивая правильное распределение шума на протяжении всего процесса генерации.

## Работа с рабочими процессами

### Сохранение рабочих процессов

Нажмите кнопку **Save** в меню, чтобы экспортировать рабочий процесс в файл JSON. Это сохраняет:

- Все узлы и их параметры
- Все соединения между узлами
- Текущий текст промпта

### Загрузка рабочих процессов

Перетащите файл JSON рабочего процесса на холст или используйте пункт **Load** в меню. Рабочий процесс Z-Image Turbo, который вы видите по умолчанию, загружается из сохранённого файла рабочего процесса.

### Совместное использование рабочих процессов

Рабочие процессы самодостаточны — поделитесь файлом JSON с коллегами, и они смогут воспроизвести вашу точную настройку. Это делает ComfyUI отличным инструментом для совместных экспериментов.

## Дальнейшие шаги

- **Изучите узлы LoRA**: применяйте адаптеры стиля или объекта без переобучения
- **Добавьте негативные промпты**: подключите второй узел CLIP Text Encode к входу условия **negative** узла KSampler, чтобы отвести модель от нежелательных особенностей, таких как размытие, артефакты или водяные знаки
- **Создавайте собственные рабочие процессы**: объединяйте несколько генераций в цепочку, добавляйте апскейлинг или создавайте вариации изображений
- **Изучайте рабочие процессы сообщества**: [Примеры ComfyUI](https://github.com/comfyanonymous/ComfyUI_examples) содержат много готовых к использованию рабочих процессов

Сильная сторона ComfyUI — это эксперименты: подключайте узлы по-разному, настраивайте параметры и наблюдайте, как каждое изменение влияет на результат. Такое практическое исследование формирует интуитивное понимание работы диффузионных моделей.

Дополнительную информацию можно найти в [документации ComfyUI](https://docs.comfy.org/).