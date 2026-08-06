<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală

ComfyUI este o interfață puternică, bazată pe noduri, pentru Stable Diffusion și alte modele de difuzie. Spre deosebire de interfețele tradiționale text-to-image cu casete simple de prompt, ComfyUI expune întregul pipeline de generare a imaginilor sub forma unui grafic vizual, oferindu-vă control detaliat asupra fiecărui pas, de la codificarea textului până la manipularea spațiului latent și decodificarea finală.

Acest tutorial vă învață cum să utilizați ComfyUI cu modelul Z Image Turbo pe GPU-ul dumneavoastră pentru a genera imagini AI de înaltă calitate.

## Ce veți învăța

- Cum să lansați ComfyUI și să încărcați șablonul Z-Image Turbo
- Înțelegerea componentelor pipeline-ului de difuzie
- Generarea de imagini și ajustarea parametrilor de generare
- Salvarea și partajarea fluxurilor de lucru

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor prealabile de software

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Acordați utilizatorului dumneavoastră acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca aceasta să aibă efect):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Crearea unui mediu virtual
Pe Linux, deschideți un terminal în directorul dorit și rulați următoarea comandă pentru a crea un venv:

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


## Lansarea ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Pentru a lansa ComfyUI pe Windows, faceți clic pe lansatorul desktop ComfyUI aflat pe desktopul dumneavoastră. Urmați pașii pentru a instala versiunea locală cu AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Apoi, faceți clic pe butonul ComfyUI din partea de sus, în mijloc, a aplicației. Aceasta va deschide o filă de setări. Deschideți fila Storage și asigurați-vă că traseele sunt setate după cum urmează pentru a accesa modelele preinstalate.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Pe AMD Ryzen™ AI Halo, ComfyUI rulează într-un container preconstruit care nu necesită configurare Python suplimentară.

Pentru a lansa ComfyUI pe Linux, faceți clic pe scurtătura ComfyUI din bara de activități. Ar trebui să se deschidă automat într-o fereastră de browser.
>**Sfat**: ComfyUI și modelele sale sunt stocate în `~/.local/share/ComfyUI/models`. Aici puteți adăuga manual fluxuri de lucru sau modele noi.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Pentru a lansa ComfyUI pe Windows, faceți pur și simplu clic pe scurtătura ComfyUI de pe desktop.
<!-- @os:end -->

<!-- @os:linux -->

Pentru a lansa ComfyUI:

1. Asigurați-vă că vă aflați în directorul ComfyUI. 
2. Rulați `python3 main.py --use-pytorch-cross-attention`

ComfyUI pornește un server web local. Deschideți browserul la adresa `http://127.0.0.1:8188` pentru a accesa interfața.

> **Sfat**: Păstrați fereastra terminalului deschisă în timp ce utilizați ComfyUI. Închiderea acesteia va opri serverul.
<!-- @os:end -->
<!-- @device:end -->


## Găsirea șablonului Z-Image Turbo

Înainte de a genera imagini, trebuie să încărcați șablonul Z-Image Turbo. Iată cum îl puteți găsi:

1. **Priviți marginea din stânga a ecranului**—există o bară de instrumente verticală care se întinde de sus până jos pe partea cea mai din stânga a aplicației.

2. **Găsiți pictograma de folder**—în acea bară de instrumente din stânga, căutați o pictogramă care arată ca un folder. Când treceți cu mouse-ul peste ea, este etichetată „Templates”.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Faceți clic pe pictograma de folder**—aceasta deschide panoul Templates.

4. **Căutați „Z-Image Turbo”**—utilizați bara de căutare sau derulați prin șabloanele disponibile pentru a găsi fluxul de lucru Z-Image Turbo Text To Image, apoi faceți clic pentru a-l încărca.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Descărcarea modelelor

<!-- @require:comfyui-models -->

## Înțelegerea interfeței

Când șablonul Z-Image Turbo se încarcă, veți vedea un canvas cu 2 noduri principale. Primul nod se numește „Text to Image (Z-Image-Turbo)”, iar al doilea nod este pentru vizualizarea imaginii. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Pe nodul Z-Image, faceți clic pe butonul din colțul din dreapta sus pentru a extinde nodul și a vedea subgraficul.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Componentele pipeline-ului

Fluxul de lucru Z-Image Turbo utilizează patru componente cheie de model care lucrează împreună:

| Componentă | Rol |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Convertește promptul dumneavoastră text în embeddings pe care modelul de difuzie le înțelege |
| **Diffusion Model** (Z-Image Turbo) | Rețeaua neuronală de bază care denoisifică iterativ reprezentările latente pentru a obține imagini |
| **VAE** (Variational Autoencoder) | Codifică imaginile către/din spațiul latent (decodifică latenții finali în pixeli) |
| **LoRA** (opțional) | Adaptoare ușoare care modifică stilul sau subiectul fără a reantrena modelul de bază |

Fiecare nod din flux de lucru corespunde uneia dintre aceste componente. Datele circulă de la stânga la dreapta: text → embeddings → denoising ghidat → latenți → imagine finală.
## Generarea primei imagini

Modelul Z-Image Turbo este deja încărcat. Pentru a genera o imagine:

1. **Introduceți promptul** în nodul principal Z-Image. Fiți descriptiv. Iată un exemplu:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opțional)**: Confirmați sau ajustați orice alte setări specifice din subgraf.
3. **Faceți clic pe butonul albastru „Run Workflow”** din colțul din dreapta (sau apăsați `Ctrl+Enter`)
4. Urmăriți cum se evidențiază nodurile pe măsură ce fiecare pas este executat

Întreaga execuție a fluxului de lucru ar trebui să se finalizeze în mai puțin de 30 de secunde. Imaginea generată apare în nodul **Save Image** și este salvată în folderul `output/`.

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


## Ajustarea parametrilor de generare

### Setările KSampler

Nodul KSampler controlează procesul central de difuzie:

| Parametru | Ce controlează | Recomandat pentru Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Numărul de iterații de eliminare a zgomotului | 4–10 (modelele turbo sunt distilate pentru mai puțini pași) |
| **cfg** | Scala de ghidare fără clasificator — cât de strict se urmează promptul | 1.0–2.0 (modelele turbo folosesc o ghidare foarte redusă) |
| **sampler_name** | Algoritmul de eliminare a zgomotului | `euler` și `res_multistep` funcționează bine pentru modelele turbo |
| **scheduler** | Curba programului de zgomot | `normal` sau `simple` |
| **seed** | Sămânța aleatorie pentru reproductibilitate | Setați valori fixe pentru a itera pe o compoziție |

### Dimensiunea imaginii

Pentru a ajusta dimensiunile de ieșire, găsiți nodul **Empty Latent Image** și modificați **width** și **height**. Păstrați dimensiunile la sau sub 1024 de pixeli pe latura cea mai lungă pentru o calitate optimă.

### ModelSamplingAuraFlow

Nodul **ModelSamplingAuraFlow** este un modificator de eșantionare specializat care ajustează modul în care procesul de difuzie gestionează programarea zgomotului. Veți vedea acest nod conectat la ieșirea modelului în fluxul de lucru Z-Image Turbo.

| Parametru | Ce controlează | Valori recomandate |
|-----------|------------------|-------------------|
| **shift** | Ajustează sincronizarea programului de zgomot — valori mai mari deplasează mai multă rafinare a detaliilor spre pașii ulteriori | 1.0–4.0 (valoarea implicită este 3.0) |

Când ajustați **shift**:

- **Valori mai mici (1.0–2.0)**: convergență mai rapidă, potrivită pentru compoziții simple
- **Valori mai mari (3.0–4.0)**: rafinare mai treptată, poate îmbunătăți detaliile fine în scene complexe

Metoda de eșantionare AuraFlow este concepută special pentru modele de tip flow-matching precum Z-Image Turbo, asigurând o distribuție corectă a zgomotului pe tot parcursul procesului de generare.

## Lucrul cu fluxuri de lucru

### Salvarea fluxurilor de lucru

Faceți clic pe butonul **Save** din meniu pentru a exporta fluxul de lucru ca fișier JSON. Acesta captează:

- Toate nodurile și parametrii lor
- Toate conexiunile dintre noduri
- Textul curent al promptului

### Încărcarea fluxurilor de lucru

Trageți un fișier JSON de flux de lucru pe canvas sau utilizați **Load** din meniu. Fluxul de lucru Z-Image Turbo pe care îl vedeți implicit este încărcat dintr-un fișier de flux de lucru salvat.

### Partajarea fluxurilor de lucru

Fluxurile de lucru sunt autonome — partajați fișierul JSON cu colegii, iar aceștia pot reproduce exact configurația dvs. Acest lucru face din ComfyUI un instrument excelent pentru experimentarea colaborativă.

## Pași următori

- **Explorați nodurile LoRA**: aplicați adaptoare de stil sau de subiect fără reantrenare
- **Adăugați prompturi negative**: conectați un al doilea nod CLIP Text Encode la intrarea de condiționare **negative** a KSampler pentru a ghida modelul departe de caracteristici nedorite, precum estomparea, artefactele sau filigranele
- **Construiți fluxuri de lucru personalizate**: înlănțuiți mai multe generări, adăugați upscaling sau creați variații de imagine
- **Explorați fluxuri de lucru din comunitate**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) conține numeroase fluxuri de lucru gata de utilizat

Punctul forte al ComfyUI este experimentarea: conectați nodurile în moduri diferite, ajustați parametrii și observați cum fiecare schimbare afectează rezultatul. Această explorare practică construiește intuiția privind funcționarea modelelor de difuzie.

Pentru mai multe informații, consultați [Documentația ComfyUI](https://docs.comfy.org/).