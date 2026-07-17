<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

ComfyUI is een krachtige, op nodes gebaseerde interface voor Stable Diffusion en andere diffusiemodellen. In tegenstelling tot traditionele tekst-naar-afbeelding-interfaces met eenvoudige promptvakken, stelt ComfyUI de volledige beeldgeneratiepijplijn bloot als een visuele grafiek, waardoor u nauwkeurige controle heeft over elke stap, van tekstcodering tot manipulatie van de latente ruimte tot de uiteindelijke decodering.

Deze tutorial leert u hoe u ComfyUI gebruikt met het Z Image Turbo-model op uw GPU om hoogwaardige AI-afbeeldingen te genereren.

## Wat U Leert

- Hoe u ComfyUI start en de Z-Image Turbo-sjabloon laadt
- Inzicht in de componenten van de diffusiepijplijn
- Afbeeldingen genereren en generatieparameters afstemmen
- Workflows opslaan en delen

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op Software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten Installeren

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Verleen uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Een Virtuele Omgeving Aanmaken
Open op Linux een terminal in de map van uw keuze en voer de volgende opdracht uit om een venv aan te maken:

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


## ComfyUI Starten

<!-- @device:halo_box -->
<!-- @os:windows -->
Om ComfyUI op Windows te starten, klikt u op de ComfyUI Desktop Launcher die u op uw bureaublad vindt. Volg de stappen om de lokale versie met AMD te installeren.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Klik vervolgens op de ComfyUI-knop bovenaan het midden van de app. Dit opent een instellingstabblad. Open het tabblad Opslag en zorg ervoor dat de paden als volgt zijn ingesteld om toegang te krijgen tot de vooraf geïnstalleerde modellen.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Om ComfyUI op Linux te starten, klikt u op de ComfyUI-snelkoppeling in de taakbalk. Het zou vanzelf in een browservenster moeten openen.
>**Tip**: ComfyUI en zijn modellen worden opgeslagen in `~/.local/share/ComfyUI/models`. Dit is waar u handmatig workflows of nieuwe modellen kunt toevoegen.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Om ComfyUI op Windows te starten, klikt u eenvoudig op de ComfyUI-snelkoppeling op uw bureaublad.
<!-- @os:end -->

<!-- @os:linux -->

Om ComfyUI te starten:

1. Zorg ervoor dat u zich in de ComfyUI-map bevindt. 
2. Voer `python3 main.py --use-pytorch-cross-attention` uit

ComfyUI start een lokale webserver. Open uw browser naar `http://127.0.0.1:8188` om toegang te krijgen tot de interface.

> **Tip**: Houd het terminalvenster open terwijl u ComfyUI gebruikt. Als u het sluit, wordt de server gestopt.
<!-- @os:end -->
<!-- @device:end -->


## De Z-Image Turbo-sjabloon Vinden

Voordat u afbeeldingen genereert, moet u de Z-Image Turbo-sjabloon laden. Zo vindt u deze:

1. **Kijk aan de uiterste linkerkant van het scherm**—er is een verticale werkbalk die van boven naar beneden loopt aan de meest linkse zijde van de app.

2. **Zoek het mappictogram**—zoek in die linker werkbalk naar een pictogram dat eruitziet als een map. Wanneer u erover beweegt, is het gelabeld als "Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klik op het mappictogram**—dit opent het paneel Templates.

4. **Zoek naar "Z-Image Turbo"**—gebruik de zoekbalk of scroll door de beschikbare sjablonen om de Z-Image Turbo Text To Image-workflow te vinden en klik om deze te laden.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Modellen Downloaden

<!-- @require:comfyui-models -->

## De Interface Begrijpen

Wanneer de Z-Image Turbo-sjabloon wordt geladen, ziet u een canvas met 2 hoofdknooppunten. Het eerste knooppunt heet 'Text to Image (Z-Image-Turbo)' en het tweede knooppunt is voor het bekijken van de afbeelding.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Klik op de Z-Image-node op de knop rechtsboven om de node uit te vouwen en de subgrafiek te bekijken.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Pijplijncomponenten

De Z-Image Turbo-workflow gebruikt vier belangrijke modelcomponenten die samenwerken:

| Component | Rol |
|-----------|------|
| **Tekstencoder** (Qwen 3 4B) | Converteert uw tekstprompt naar embeddings die het diffusiemodel begrijpt |
| **Diffusiemodel** (Z-Image Turbo) | Het centrale neurale netwerk dat latente representaties iteratief ontruist tot afbeeldingen |
| **VAE** (Variationele Autoencoder) | Codeert afbeeldingen naar/van de latente ruimte (decodeert de uiteindelijke latenten naar pixels) |
| **LoRA** (optioneel) | Lichtgewicht adapters die stijl of onderwerp aanpassen zonder het basismodel opnieuw te trainen |

Elk knooppunt in de workflow komt overeen met een van deze componenten. Gegevens stromen van links naar rechts: tekst → embeddings → begeleide ontruising → latenten → uiteindelijke afbeelding.

## Uw Eerste Afbeelding Genereren

Het Z-Image Turbo-model is al geladen. Om een afbeelding te genereren:

1. **Voer uw prompt in** in de hoofd Z-Image-node. Wees beschrijvend. Hier is een voorbeeld:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Optioneel)**: Bevestig of pas eventuele andere specifieke instellingen binnen de subgrafiek aan.
3. **Klik op de blauwe "Run Workflow"** in de rechterhoek (of druk op `Ctrl+Enter`)
4. Bekijk hoe de knooppunten oplichten terwijl elke stap wordt uitgevoerd

De volledige uitvoering van de workflow zou in minder dan 30 seconden moeten zijn voltooid. Uw gegenereerde afbeelding verschijnt in het knooppunt **Save Image** en wordt opgeslagen in de map `output/`.

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


## Generatieparameters Aanpassen

### KSampler-instellingen

Het KSampler-knooppunt beheert het kernproces van de diffusie:

| Parameter | Wat Het Beheert | Aanbevolen voor Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Aantal ontruisingsiteraties | 4–10 (turbomodellen zijn gedistilleerd voor minder stappen) |
| **cfg** | Classifier-vrije begeleidingsschaal—hoe nauwkeurig de prompt wordt gevolgd | 1.0–2.0 (turbomodellen gebruiken zeer lage begeleiding) |
| **sampler_name** | Ontruisingsalgoritme | `euler` en `res_multistep` werken goed voor turbomodellen |
| **scheduler** | Ruisschedulecurve | `normal` of `simple` |
| **seed** | Willekeurige seed voor reproduceerbaarheid | Stel vaste waarden in om op een compositie te itereren |

### Afbeeldingsgrootte

Om de uitvoerdimensies aan te passen, zoekt u het knooppunt **Empty Latent Image** en wijzigt u **width** en **height**. Houd de afmetingen op of onder 1024 pixels aan de langste zijde voor optimale kwaliteit.

### ModelSamplingAuraFlow

Het knooppunt **ModelSamplingAuraFlow** is een gespecialiseerde samplingmodifier die aanpast hoe het diffusieproces omgaat met ruisplanning. U ziet dit knooppunt verbonden met de modeluitvoer in de Z-Image Turbo-workflow.

| Parameter | Wat Het Beheert | Aanbevolen Waarden |
|-----------|------------------|-------------------|
| **shift** | Past de timing van het ruisschema aan—hogere waarden verschuiven meer detailverbetering naar latere stappen | 1.0–4.0 (standaard is 3.0) |

Wanneer u **shift** aanpast:

- **Lagere waarden (1.0–2.0)**: Snellere convergentie, goed voor eenvoudige composities
- **Hogere waarden (3.0–4.0)**: Meer geleidelijke verfijning, kan fijne details in complexe scènes verbeteren

De AuraFlow-samplingmethode is specifiek ontworpen voor flow-matching-modellen zoals Z-Image Turbo, waardoor een correcte ruisverdeling gedurende het gehele generatieproces wordt gewaarborgd.

## Werken met Workflows

### Workflows Opslaan

Klik op de knop **Save** in het menu om uw workflow als een JSON-bestand te exporteren. Dit legt het volgende vast:

- Alle knooppunten en hun parameters
- Alle verbindingen tussen knooppunten
- Huidige prompttekst

### Workflows Laden

Sleep een workflow-JSON-bestand naar het canvas of gebruik **Load** vanuit het menu. De Z-Image Turbo-workflow die u standaard ziet, wordt geladen vanuit een opgeslagen workflowbestand.

### Workflows Delen

Workflows zijn op zichzelf staand—deel het JSON-bestand met collega's en zij kunnen uw exacte configuratie reproduceren. Dit maakt ComfyUI uitstekend geschikt voor collaboratief experimenteren.

## Volgende Stappen

- **Verken LoRA-knooppunten**: Pas stijl- of onderwerpAdapters toe zonder opnieuw te trainen
- **Voeg negatieve prompts toe**: Verbind een tweede CLIP Text Encode-knooppunt met de **negative** conditioneringsinvoer van KSampler om het model weg te sturen van ongewenste kenmerken zoals vervaging, artefacten of watermerken
- **Bouw aangepaste workflows**: Koppel meerdere generaties, voeg upscaling toe of maak afbeeldingsvariaties
- **Blader door community-workflows**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) heeft veel kant-en-klare workflows

De kracht van ComfyUI ligt in experimenteren: verbind knooppunten anders, pas parameters aan en observeer hoe elke wijziging de uitvoer beïnvloedt. Deze praktische verkenning bouwt intuïtie op voor hoe diffusiemodellen werken.

Voor meer informatie, bekijk de [ComfyUI-documentatie](https://docs.comfy.org/).