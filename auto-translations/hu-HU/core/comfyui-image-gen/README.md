<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

A ComfyUI egy hatékony, csomópontalapú felület a Stable Diffusion és más diffúziós modellek számára. Az egyszerű promptmezőkkel rendelkező hagyományos szöveg-kép felületekkel ellentétben a ComfyUI a teljes képgenerálási folyamatot vizuális gráfként jeleníti meg, így részletes kontrollt biztosít minden lépés felett – a szövegkódolástól a látenstér-manipuláción át a végső dekódolásig.

Ez az oktatóanyag megtanítja, hogyan használd a ComfyUI-t a Z Image Turbo modellel a GPU-don, hogy kiváló minőségű AI-képeket generálj.

## Mit fogsz megtanulni

- Hogyan indítsd el a ComfyUI-t és töltsd be a Z-Image Turbo sablont
- A diffúziós folyamat összetevőinek megértése
- Képek generálása és a generálási paraméterek finomhangolása
- Munkafolyamatok mentése és megosztása

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Adj hozzáférést a felhasználódnak a GPU-eszközökhöz** (a módosítás érvénybe lépéséhez jelentkezz ki, majd be):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Virtuális környezet létrehozása
Linuxon nyiss egy terminált a kívánt könyvtárban, és futtasd a következő parancsot egy venv létrehozásához:

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


## A ComfyUI elindítása

<!-- @device:halo_box -->
<!-- @os:windows -->
A ComfyUI Windowson való elindításához kattints az asztalon található ComfyUI Desktop Launcher ikonra. Kövesd a lépéseket a helyi verzió AMD-vel való telepítéséhez.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Ezután kattints az alkalmazás tetején középen található ComfyUI gombra. Ez megnyit egy beállítások lapot. Nyisd meg a Storage lapot, és győződj meg arról, hogy az elérési utak az alábbiak szerint vannak beállítva az előre telepített modellek eléréséhez.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
A ComfyUI Linuxon való elindításához kattints a tálcán található ComfyUI parancsikonra. Automatikusan megnyílik egy böngészőablakban.
>**Tipp**: A ComfyUI és modelljei a `~/.local/share/ComfyUI/models` könyvtárban találhatók. Ide tudsz manuálisan munkafolyamatokat vagy új modelleket hozzáadni.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
A ComfyUI Windowson való elindításához egyszerűen kattints az asztalon található ComfyUI parancsikonra.
<!-- @os:end -->

<!-- @os:linux -->

A ComfyUI elindításához:

1. Győződj meg arról, hogy a ComfyUI könyvtárában vagy. 
2. Futtasd a `python3 main.py --use-pytorch-cross-attention` parancsot

A ComfyUI elindít egy helyi webszervert. Nyisd meg a böngészőben a `http://127.0.0.1:8188` címet a felület eléréséhez.

> **Tipp**: Tartsd nyitva a terminálablakot a ComfyUI használata közben. Bezárása leállítja a szervert.
<!-- @os:end -->
<!-- @device:end -->


## A Z-Image Turbo sablon megkeresése

A képek generálása előtt be kell töltened a Z-Image Turbo sablont. Így találod meg:

1. **Nézz a képernyő bal szélére** – az alkalmazás bal oldalán egy függőleges eszköztár fut fentről lefelé.

2. **Keresd a mappa ikont** – a bal oldali eszköztárban keress egy mappára hasonlító ikont. Ha fölé viszed az egeret, a „Templates" felirat jelenik meg.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Kattints a mappa ikonra** – ez megnyitja a Templates panelt.

4. **Keress rá a „Z-Image Turbo" kifejezésre** – használd a keresősávot, vagy görgess az elérhető sablonok között a Z-Image Turbo Text To Image munkafolyamat megkereséséhez, majd kattints rá a betöltéshez.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Modellek letöltése

<!-- @require:comfyui-models -->

## A felület megismerése

Amikor a Z-Image Turbo sablon betöltődik, egy vásznat látsz 2 fő csomóponttal. Az első csomópont neve „Text to Image (Z-Image-Turbo)", a második pedig a kép megtekintésére szolgál.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


A Z-Image csomóponton kattints a jobb felső gombra a csomópont kibontásához és az algrafikont megtekintéséhez.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### A folyamat összetevői

A Z-Image Turbo munkafolyamat négy kulcsfontosságú modellkomponensből áll, amelyek együtt működnek:

| Összetevő | Szerepe |
|-----------|------|
| **Szövegkódoló** (Qwen 3 4B) | A szöveges promptot olyan beágyazásokká alakítja, amelyeket a diffúziós modell megért |
| **Diffúziós modell** (Z-Image Turbo) | Az alapvető neurális hálózat, amely iteratívan zajtalanítja a látens reprezentációkat képekké |
| **VAE** (Variational Autoencoder) | Képeket kódol/dekódol a látenstérbe/ből (a végső látenseket pixelekké dekódolja) |
| **LoRA** (opcionális) | Könnyűsúlyú adapterek, amelyek stílust vagy témát módosítanak az alapmodell újratanítása nélkül |

A munkafolyamat minden csomópontja ezen összetevők egyikének felel meg. Az adatok balról jobbra áramlanak: szöveg → beágyazások → irányított zajtalanítás → látensek → végső kép.

## Az első kép generálása

A Z-Image Turbo modell már be van töltve. Kép generálásához:

1. **Add meg a promptot** a fő Z-Image csomópontban. Légy részletes. Íme egy példa:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opcionális)**: Erősítsd meg vagy módosítsd az algrafikonon belüli egyéb beállításokat.
3. **Kattints a kék „Run Workflow" gombra** a jobb sarokban (vagy nyomj `Ctrl+Enter` billentyűkombinációt)
4. Figyeld, ahogy a csomópontok kiemelkednek az egyes lépések végrehajtásakor

A teljes munkafolyamat végrehajtása kevesebb mint 30 másodpercet vesz igénybe. A generált kép megjelenik a **Save Image** csomópontban, és az `output/` mappába kerül mentésre.

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


## Generálási paraméterek módosítása

### KSampler beállítások

A KSampler csomópont vezérli az alapvető diffúziós folyamatot:

| Paraméter | Mit vezérel | Ajánlott a Z-Image Turbo-hoz |
|-----------|------------------|-------------------------------|
| **steps** | A zajtalanítási iterációk száma | 4–10 (a turbo modellek kevesebb lépésre vannak desztillálva) |
| **cfg** | Osztályozómentes irányítási skála – mennyire kövesse szorosan a promptot | 1,0–2,0 (a turbo modellek nagyon alacsony irányítást használnak) |
| **sampler_name** | Zajtalanítási algoritmus | Az `euler` és a `res_multistep` jól működik turbo modellekhez |
| **scheduler** | Zajütemezési görbe | `normal` vagy `simple` |
| **seed** | Véletlenszerű mag a reprodukálhatósághoz | Állíts be rögzített értékeket egy kompozíció iterálásához |

### Képméret

A kimeneti méretek módosításához keresd meg az **Empty Latent Image** csomópontot, és módosítsd a **width** és **height** értékeket. Az optimális minőség érdekében tartsd a méreteket legfeljebb 1024 pixelen a leghosszabb oldalon.

### ModelSamplingAuraFlow

A **ModelSamplingAuraFlow** csomópont egy speciális mintavételezési módosító, amely azt állítja be, hogyan kezeli a diffúziós folyamat a zajütemezést. Ezt a csomópontot a Z-Image Turbo munkafolyamatban a modell kimenetéhez csatlakoztatva látod.

| Paraméter | Mit vezérel | Ajánlott értékek |
|-----------|------------------|-------------------|
| **shift** | A zajütemezés időzítését állítja be – a magasabb értékek a részletfinomítást a későbbi lépésekre tolják | 1,0–4,0 (az alapértelmezett 3,0) |

Mikor érdemes módosítani a **shift** értékét:

- **Alacsonyabb értékek (1,0–2,0)**: Gyorsabb konvergencia, egyszerű kompozíciókhoz megfelelő
- **Magasabb értékek (3,0–4,0)**: Fokozatosabb finomítás, összetett jelenetek apró részleteit javíthatja

Az AuraFlow mintavételezési módszer kifejezetten az olyan flow-matching modellekhez lett tervezve, mint a Z-Image Turbo, biztosítva a megfelelő zajeloszlást a generálási folyamat során.

## Munkafolyamatokkal való munka

### Munkafolyamatok mentése

Kattints a **Save** gombra a menüben a munkafolyamat JSON-fájlként való exportálásához. Ez rögzíti a következőket:

- Az összes csomópontot és paramétereiket
- A csomópontok közötti összes kapcsolatot
- Az aktuális prompt szövegét

### Munkafolyamatok betöltése

Húzz egy munkafolyamat JSON-fájlt a vászonra, vagy használd a **Load** lehetőséget a menüből. Az alapértelmezés szerint látható Z-Image Turbo munkafolyamat egy mentett munkafolyamat-fájlból töltődik be.

### Munkafolyamatok megosztása

A munkafolyamatok önállóak – oszd meg a JSON-fájlt kollégáiddal, és ők pontosan reprodukálhatják a beállításaidat. Ez teszi a ComfyUI-t kiválóvá az együttműködésen alapuló kísérletezéshez.

## Következő lépések

- **Fedezd fel a LoRA csomópontokat**: Alkalmazz stílus- vagy témadaptereket újratanítás nélkül
- **Adj hozzá negatív promptokat**: Csatlakoztass egy második CLIP Text Encode csomópontot a KSampler **negative** kondicionálási bemenetéhez, hogy a modellt a nem kívánt jellemzőktől – például elmosódástól, artefaktusoktól vagy vízjelektől – eltávolítsd
- **Készíts egyéni munkafolyamatokat**: Láncolj össze több generálást, adj hozzá felskálázást, vagy hozz létre képvariációkat
- **Böngéssz a közösségi munkafolyamatok között**: A [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) oldalon számos azonnal használható munkafolyamat található

A ComfyUI erőssége a kísérletezés: csatlakoztasd a csomópontokat másképp, módosítsd a paramétereket, és figyeld meg, hogyan befolyásolja az egyes változtatás a kimenetet. Ez a gyakorlati felfedezés intuíciót épít a diffúziós modellek működéséről.

További információkért tekintsd meg a [ComfyUI dokumentációját](https://docs.comfy.org/).