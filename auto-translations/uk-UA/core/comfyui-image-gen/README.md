<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

ComfyUI — це потужний, вузловий інтерфейс для Stable Diffusion та інших дифузійних моделей. На відміну від традиційних інтерфейсів "текст в зображення" з простими полями введення підказки, ComfyUI відображає весь конвеєр генерації зображень у вигляді візуального графа, надаючи вам детальний контроль над кожним кроком — від кодування тексту до маніпуляцій у латентному просторі та фінального декодування.

Цей посібник навчить вас використовувати ComfyUI з моделлю Z Image Turbo на вашому GPU для генерації високоякісних AI-зображень.

## Що ви дізнаєтеся

- Як запустити ComfyUI та завантажити шаблон Z-Image Turbo
- Розуміння компонентів дифузійного конвеєра
- Генерація зображень та налаштування параметрів генерації
- Збереження та обмін робочими процесами

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Надайте вашому користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набули чинності):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Створення віртуального середовища
На Linux відкрийте термінал у вибраному вами каталозі та виконайте наступну команду для створення venv:

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
Щоб запустити ComfyUI на Windows, натисніть на ярлик ComfyUI Desktop Launcher, який знаходиться на вашому робочому столі. Дотримуйтеся кроків для встановлення локальної версії з AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Потім натисніть кнопку ComfyUI у верхній середній частині додатка. Це відкриє вкладку налаштувань. Відкрийте вкладку Storage і переконайтеся, що шляхи налаштовані наступним чином для доступу до попередньо встановлених моделей.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
На AMD Ryzen™ AI Halo ComfyUI працює у попередньо зібраному контейнері, який не потребує додаткового налаштування Python.

Щоб запустити ComfyUI на Linux, натисніть на ярлик ComfyUI на панелі завдань. Він має відкритися самостійно у вікні браузера.
>**Порада**: ComfyUI та його моделі зберігаються за адресою `~/.local/share/ComfyUI/models`. Саме тут ви можете вручну додавати робочі процеси або нові моделі.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Щоб запустити ComfyUI на Windows, просто натисніть на ярлик ComfyUI на вашому робочому столі.
<!-- @os:end -->

<!-- @os:linux -->

Щоб запустити ComfyUI:

1. Переконайтеся, що ви перебуваєте в каталозі ComfyUI. 
2. Виконайте `python3 main.py --use-pytorch-cross-attention`

ComfyUI запускає локальний веб-сервер. Відкрийте браузер за адресою `http://127.0.0.1:8188`, щоб отримати доступ до інтерфейсу.

> **Порада**: Тримайте вікно термінала відкритим під час використання ComfyUI. Його закриття зупинить сервер.
<!-- @os:end -->
<!-- @device:end -->


## Пошук шаблону Z-Image Turbo

Перш ніж генерувати зображення, вам потрібно завантажити шаблон Z-Image Turbo. Ось як його знайти:

1. **Погляньте на крайній лівий край екрана** — там є вертикальна панель інструментів, що йде згори донизу з лівого боку додатка.

2. **Знайдіть значок папки** — на цій лівій панелі інструментів знайдіть значок, схожий на папку. При наведенні на нього з'явиться напис "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Натисніть на значок папки** — це відкриє панель Templates.

4. **Знайдіть "Z-Image Turbo"** — скористайтеся рядком пошуку або прогорніть доступні шаблони, щоб знайти робочий процес Z-Image Turbo Text To Image, а потім натисніть на нього, щоб завантажити.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Завантаження моделей

<!-- @require:comfyui-models -->

## Розуміння інтерфейсу

Коли шаблон Z-Image Turbo завантажиться, ви побачите полотно з 2 основними вузлами. Перший вузол називається "Text to Image (Z-Image-Turbo)", а другий призначений для перегляду зображення. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


На вузлі Z-Image натисніть кнопку у верхньому правому куті, щоб розгорнути вузол і побачити підграф.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Компоненти конвеєра

Робочий процес Z-Image Turbo використовує чотири ключові компоненти моделей, які працюють разом:

| Компонент | Роль |
|-----------|------|
| **Текстовий кодувальник** (Qwen 3 4B) | Перетворює вашу текстову підказку на ембеддинги, які розуміє дифузійна модель |
| **Дифузійна модель** (Z-Image Turbo) | Основна нейронна мережа, яка ітеративно очищає від шуму латентні представлення, перетворюючи їх на зображення |
| **VAE** (варіаційний автокодувальник) | Кодує зображення в латентний простір і назад (декодує кінцеві латентні представлення в пікселі) |
| **LoRA** (опційно) | Легкі адаптери, що змінюють стиль або об'єкт без перенавчання базової моделі |

Кожен вузол у робочому процесі відповідає одному з цих компонентів. Дані передаються зліва направо: текст → ембеддинги → скероване очищення від шуму → латентні представлення → фінальне зображення.
## Генерація вашого першого зображення

Модель Z-Image Turbo вже завантажена. Щоб згенерувати зображення:

1. **Введіть свій промпт** в основному вузлі Z-Image Node. Будьте якомога описовішими. Ось приклад:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Необов'язково)**: Перевірте або налаштуйте будь-які інші параметри в підграфі.
3. **Натисніть синю кнопку "Run Workflow"** у правому куті (або натисніть `Ctrl+Enter`)
4. Спостерігайте, як підсвічуються вузли під час виконання кожного кроку

Виконання всього робочого процесу має завершитися менш ніж за 30 секунд. Ваше згенероване зображення з'явиться у вузлі **Save Image** та буде збережене в папці `output/`.

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


## Налаштування параметрів генерації

### Налаштування KSampler

Вузол KSampler контролює основний процес дифузії:

| Параметр | Що контролює | Рекомендовано для Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Кількість ітерацій усунення шуму | 4–10 (turbo-моделі дистильовані для меншої кількості кроків) |
| **cfg** | Масштаб класифікатор-вільного керування (classifier-free guidance) — наскільки точно слідувати промпту | 1.0–2.0 (turbo-моделі використовують дуже низьке керування) |
| **sampler_name** | Алгоритм усунення шуму | `euler` та `res_multistep` добре працюють для turbo-моделей |
| **scheduler** | Крива розкладу шуму | `normal` або `simple` |
| **seed** | Випадкове зерно для відтворюваності | Встановіть фіксовані значення для ітерації над композицією |

### Розмір зображення

Щоб налаштувати вихідні розміри, знайдіть вузол **Empty Latent Image** та змініть **width** і **height**. Тримайте розміри на рівні або нижче 1024 пікселів по найдовшій стороні для оптимальної якості.

### ModelSamplingAuraFlow

Вузол **ModelSamplingAuraFlow** — це спеціалізований модифікатор семплінгу, який налаштовує, як процес дифузії обробляє розклад шуму. Ви побачите цей вузол підключеним до виходу моделі в робочому процесі Z-Image Turbo.

| Параметр | Що контролює | Рекомендовані значення |
|-----------|------------------|-------------------|
| **shift** | Налаштовує час розкладу шуму — вищі значення переносять більше уточнення деталей на пізніші кроки | 1.0–4.0 (типове значення — 3.0) |

Коли варто налаштувати **shift**:

- **Нижчі значення (1.0–2.0)**: швидша збіжність, добре для простих композицій
- **Вищі значення (3.0–4.0)**: більш поступове уточнення, може покращити дрібні деталі у складних сценах

Метод семплінгу AuraFlow спеціально розроблений для моделей на основі flow-matching, таких як Z-Image Turbo, забезпечуючи правильний розподіл шуму протягом усього процесу генерації.

## Робота з робочими процесами

### Збереження робочих процесів

Натисніть кнопку **Save** у меню, щоб експортувати ваш робочий процес у файл JSON. Це зберігає:

- Усі вузли та їхні параметри
- Усі з'єднання між вузлами
- Поточний текст промпту

### Завантаження робочих процесів

Перетягніть файл JSON робочого процесу на полотно або скористайтеся пунктом **Load** у меню. Робочий процес Z-Image Turbo, який ви бачите за замовчуванням, завантажується зі збереженого файлу робочого процесу.

### Обмін робочими процесами

Робочі процеси є самодостатніми — поділіться файлом JSON з колегами, і вони зможуть відтворити вашу точну конфігурацію. Це робить ComfyUI чудовим інструментом для спільних експериментів.

## Наступні кроки

- **Досліджуйте вузли LoRA**: застосовуйте адаптери стилю чи об'єкта без перенавчання
- **Додайте негативні промпти**: підключіть другий вузол CLIP Text Encode до входу умовності **negative** у KSampler, щоб спрямувати модель подалі від небажаних елементів, таких як розмиття, артефакти чи водяні знаки
- **Створюйте власні робочі процеси**: об'єднуйте кілька генерацій у ланцюжок, додавайте апскейлінг або створюйте варіації зображень
- **Переглядайте робочі процеси спільноти**: [Приклади ComfyUI](https://github.com/comfyanonymous/ComfyUI_examples) містять багато готових до використання робочих процесів

Сила ComfyUI — в експериментуванні: з'єднуйте вузли по-різному, налаштовуйте параметри та спостерігайте, як кожна зміна впливає на результат. Ця практична дослідницька робота формує інтуїтивне розуміння того, як працюють дифузійні моделі.

Для отримання додаткової інформації ознайомтеся з [документацією ComfyUI](https://docs.comfy.org/).