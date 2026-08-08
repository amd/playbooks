<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

ComfyUI is een krachtige, op nodes gebaseerde interface voor Stable Diffusion en andere diffusiemodellen. In tegenstelling tot traditionele tekst-naar-afbeelding-interfaces met eenvoudige promptvakken, toont ComfyUI de volledige beeldgeneratiepijplijn als een visuele graaf, waardoor je fijnmazige controle hebt over elke stap, van tekstcodering tot manipulatie van de latente ruimte tot uiteindelijke decodering.

Deze tutorial leert je hoe je ComfyUI gebruikt met het Z Image Turbo-model op je GPU om hoogwaardige AI-afbeeldingen te genereren.

## Wat je leert

- Hoe je ComfyUI start en de Z-Image Turbo-template laadt
- Inzicht in de componenten van de diffusiepijplijn
- Afbeeldingen genereren en generatieparameters afstemmen
- Workflows opslaan en delen

## Het geheugen configureren

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten installeren

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Geef je gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Een virtuele omgeving maken
Open op Linux een terminal in de map van je keuze en voer de volgende opdracht uit om een venv te maken:

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


## ComfyUI starten

<!-- @device:halo_box -->
<!-- @os:windows -->
Om ComfyUI op Windows te starten, klik je op de ComfyUI Desktop Launcher die je op je bureaublad vindt. Volg de stappen om de lokale versie met AMD te installeren.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Klik vervolgens op de ComfyUI-knop bovenaan in het midden van de app. Hierdoor wordt een instellingentabblad geopend. Open het tabblad Storage en zorg ervoor dat de paden als volgt zijn ingesteld om toegang te krijgen tot de vooraf geïnstalleerde modellen.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Op de AMD Ryzen™ AI Halo draait ComfyUI in een vooraf gebouwde container waarvoor geen extra Python-installatie nodig is.

Om ComfyUI op Linux te starten, klik je op de ComfyUI-snelkoppeling in de taakbalk. Deze zou vanzelf in een browservenster moeten openen.
>**Tip**: ComfyUI en de bijbehorende modellen worden opgeslagen in `~/.local/share/ComfyUI/models`. Hier kun je handmatig workflows of nieuwe modellen toevoegen.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Om ComfyUI op Windows te starten, klik je gewoon op de ComfyUI-snelkoppeling op je bureaublad.
<!-- @os:end -->

<!-- @os:linux -->

Om ComfyUI te starten:

1. Zorg ervoor dat je je in de ComfyUI-directory bevindt.
2. Voer `python3 main.py --use-pytorch-cross-attention` uit

ComfyUI start een lokale webserver. Open je browser naar `http://127.0.0.1:8188` om toegang te krijgen tot de interface.

> **Tip**: Houd het terminalvenster open terwijl je ComfyUI gebruikt. Als je het sluit, stopt de server.
<!-- @os:end -->
<!-- @device:end -->


## De Z-Image Turbo-template vinden

Voordat je afbeeldingen kunt genereren, moet je de Z-Image Turbo-template laden. Zo vind je deze:

1. **Kijk naar de uiterst linkerrand van het scherm**—er loopt een verticale werkbalk van boven naar beneden aan de linkerkant van de app.

2. **Zoek het mapicoon**—in die linker werkbalk zoek je naar een icoon dat op een map lijkt. Als je erover zweeft, wordt het gelabeld als "Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klik op het mapicoon**—hiermee wordt het paneel Templates geopend.

4. **Zoek naar "Z-Image Turbo"**—gebruik de zoekbalk of blader door de beschikbare templates om de Z-Image Turbo Text To Image-workflow te vinden, en klik erop om deze te laden.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Modellen downloaden

<!-- @require:comfyui-models -->

## De interface begrijpen

Wanneer de Z-Image Turbo-template wordt geladen, zie je een canvas met 2 hoofdnodes. De eerste node heet 'Text to Image (Z-Image-Turbo)', en de tweede node is voor het bekijken van de afbeelding.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Klik in de Z-Image-node op de knop rechtsboven om de node uit te vouwen en de subgraaf te bekijken.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Pijplijncomponenten

De Z-Image Turbo-workflow gebruikt vier belangrijke modelcomponenten die samenwerken:

| Component | Rol |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Zet je tekstprompt om in embeddings die het diffusiemodel begrijpt |
| **Diffusion Model** (Z-Image Turbo) | Het kernneurale netwerk dat latente representaties iteratief ontruist tot afbeeldingen |
| **VAE** (Variational Autoencoder) | Codeert afbeeldingen van/naar latente ruimte (decodeert de uiteindelijke latents naar pixels) |
| **LoRA** (optioneel) | Lichtgewicht adapters die stijl of onderwerp aanpassen zonder het basismodel opnieuw te trainen |

Elke node in de workflow komt overeen met een van deze componenten. Data stroomt van links naar rechts: tekst → embeddings → gestuurde ontruising → latents → uiteindelijke afbeelding.
## Uw eerste afbeelding genereren

Het Z-Image Turbo-model is al geladen. Om een afbeelding te genereren:

1. **Voer uw prompt in** in de hoofd-Z-Image-node. Wees beschrijvend. Hier is een voorbeeld:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Optioneel)**: Bevestig of pas eventuele andere specifieke instellingen binnen de subgraph aan.
3. **Klik op de blauwe "Run Workflow"** in de rechterhoek (of druk op `Ctrl+Enter`)
4. Kijk hoe de nodes oplichten terwijl elke stap wordt uitgevoerd

De volledige uitvoering van de workflow zou in minder dan 30 seconden voltooid moeten zijn. Uw gegenereerde afbeelding verschijnt in de **Save Image**-node en wordt opgeslagen in de map `output/`.

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


## Generatieparameters aanpassen

### KSampler-instellingen

De KSampler-node regelt het kernproces van diffusie:

| Parameter | Wat het regelt | Aanbevolen voor Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Aantal denoising-iteraties | 4–10 (turbomodellen zijn gedistilleerd voor minder stappen) |
| **cfg** | Classifier-free guidance scale—hoe nauw de prompt wordt gevolgd | 1,0–2,0 (turbomodellen gebruiken zeer lage guidance) |
| **sampler_name** | Denoising-algoritme | `euler` en `res_multistep` werken goed voor turbomodellen |
| **scheduler** | Curve van het noise-schema | `normal` of `simple` |
| **seed** | Willekeurige seed voor reproduceerbaarheid | Stel vaste waarden in om een compositie te verfijnen |

### Afbeeldingsformaat

Om de uitvoerafmetingen aan te passen, zoekt u de **Empty Latent Image**-node en wijzigt u **width** en **height**. Houd de afmetingen op of onder 1024 pixels aan de langste zijde voor optimale kwaliteit.

### ModelSamplingAuraFlow

De **ModelSamplingAuraFlow**-node is een gespecialiseerde sampling-modifier die aanpast hoe het diffusieproces de noise-scheduling afhandelt. U ziet deze node verbonden met de modeluitvoer in de Z-Image Turbo-workflow.

| Parameter | Wat het regelt | Aanbevolen waarden |
|-----------|------------------|-------------------|
| **shift** | Past de timing van het noise-schema aan—hogere waarden verschuiven meer detailverfijning naar latere stappen | 1,0–4,0 (standaard is 3,0) |

Wanneer u **shift** moet aanpassen:

- **Lagere waarden (1,0–2,0)**: Sneller convergeren, goed voor eenvoudige composities
- **Hogere waarden (3,0–4,0)**: Geleidelijkere verfijning, kan fijne details in complexe scènes verbeteren

De AuraFlow-samplingmethode is specifiek ontworpen voor flow-matching-modellen zoals Z-Image Turbo, wat zorgt voor een correcte noise-verdeling gedurende het hele generatieproces.

## Werken met workflows

### Workflows opslaan

Klik op de knop **Save** in het menu om uw workflow te exporteren als JSON-bestand. Dit legt vast:

- Alle nodes en hun parameters
- Alle verbindingen tussen nodes
- Huidige prompttekst

### Workflows laden

Sleep een workflow-JSON-bestand naar het canvas, of gebruik **Load** in het menu. De Z-Image Turbo-workflow die u standaard ziet, wordt geladen vanuit een opgeslagen workflowbestand.

### Workflows delen

Workflows zijn op zichzelf staand—deel het JSON-bestand met collega's, en zij kunnen uw exacte configuratie reproduceren. Dit maakt ComfyUI uitstekend geschikt voor gezamenlijk experimenteren.

## Volgende stappen

- **Verken LoRA-nodes**: Pas stijl- of onderwerp-adapters toe zonder opnieuw te trainen
- **Voeg negatieve prompts toe**: Verbind een tweede CLIP Text Encode-node met de **negative** conditioneringsinvoer van KSampler om het model weg te sturen van ongewenste kenmerken zoals wazigheid, artefacten of watermerken
- **Bouw aangepaste workflows**: Koppel meerdere generaties aaneen, voeg upscaling toe, of maak afbeeldingsvariaties
- **Blader door community-workflows**: [ComfyUI-voorbeelden](https://github.com/comfyanonymous/ComfyUI_examples) bevat veel kant-en-klare workflows

De kracht van ComfyUI ligt in experimenteren: verbind nodes op verschillende manieren, pas parameters aan en observeer hoe elke wijziging de uitvoer beïnvloedt. Deze praktische verkenning bouwt intuïtie op voor hoe diffusiemodellen werken.

Bekijk voor meer informatie de [ComfyUI-documentatie](https://docs.comfy.org/).