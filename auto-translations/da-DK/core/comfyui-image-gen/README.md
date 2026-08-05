<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

ComfyUI er en kraftfuld, node-baseret grænseflade til Stable Diffusion og andre diffusionsmodeller. I modsætning til traditionelle tekst-til-billede-grænseflader med simple promptbokse eksponerer ComfyUI hele billedgenereringspipelinen som en visuel graf, hvilket giver dig detaljeret kontrol over hvert trin fra tekstkodning til manipulation af det latente rum til den endelige dekodning.

Denne tutorial lærer dig, hvordan du bruger ComfyUI med Z Image Turbo-modellen på din GPU til at generere AI-billeder af høj kvalitet.

## Hvad du vil lære

- Sådan starter du ComfyUI og indlæser Z-Image Turbo-skabelonen
- Forståelse af diffusionspipelinens komponenter
- Generering af billeder og finjustering af genereringsparametre
- Gemning og deling af workflows

## Konfiguration af hukommelse

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af nødvendig software

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen, for at dette træder i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Opret et virtuelt miljø
På Linux skal du åbne en terminal i den mappe, du ønsker, og køre følgende kommando for at oprette et venv:

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


## Start af ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
For at starte ComfyUI på Windows skal du klikke på ComfyUI Desktop Launcher, som findes på dit skrivebord. Følg trinnene for at installere den lokale version med AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Klik derefter på ComfyUI-knappen øverst i midten af appen. Dette åbner en indstillingsfane. Åbn fanen Storage, og sørg for, at stierne er indstillet som følger for at få adgang til de forudinstallerede modeller.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
På AMD Ryzen™ AI Halo kører ComfyUI i en forudbygget container, der ikke kræver yderligere Python-opsætning.

For at starte ComfyUI på Linux skal du klikke på ComfyUI-genvejen i proceslinjen. Den bør åbne af sig selv i et browservindue.
>**Tip**: ComfyUI og dets modeller gemmes i `~/.local/share/ComfyUI/models`. Det er her, du manuelt kan tilføje workflows eller nye modeller.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
For at starte ComfyUI på Windows skal du blot klikke på ComfyUI-genvejen på dit skrivebord.
<!-- @os:end -->

<!-- @os:linux -->

For at starte ComfyUI:

1. Sørg for, at du befinder dig i ComfyUI-mappen.
2. Kør `python3 main.py --use-pytorch-cross-attention`

ComfyUI starter en lokal webserver. Åbn din browser på `http://127.0.0.1:8188` for at få adgang til grænsefladen.

> **Tip**: Hold terminalvinduet åbent, mens du bruger ComfyUI. Hvis du lukker det, stopper serveren.
<!-- @os:end -->
<!-- @device:end -->


## Sådan finder du Z-Image Turbo-skabelonen

Før du genererer billeder, skal du indlæse Z-Image Turbo-skabelonen. Sådan finder du den:

1. **Se på den yderste venstre kant af skærmen** — der er en lodret værktøjslinje, der løber fra top til bund på venstre side af appen.

2. **Find mappeikonet** — i den venstre værktøjslinje skal du kigge efter et ikon, der ligner en mappe. Når du holder musen over det, er det mærket "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klik på mappeikonet** — dette åbner panelet Templates.

4. **Søg efter "Z-Image Turbo"** — brug søgefeltet, eller rul gennem de tilgængelige skabeloner for at finde Z-Image Turbo Text To Image-workflowet, og klik derefter for at indlæse det.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Download af modeller

<!-- @require:comfyui-models -->

## Forståelse af grænsefladen

Når Z-Image Turbo-skabelonen indlæses, ser du et lærred med 2 hovednoder. Den første node kaldes 'Text to Image (Z-Image-Turbo)', og den anden node bruges til at se billedet.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


På Z-Image-noden skal du klikke på knappen øverst til højre for at udvide noden og se undergrafen.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Pipelinekomponenter

Z-Image Turbo-workflowet bruger fire vigtige modelkomponenter, der arbejder sammen:

| Komponent | Rolle |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Konverterer din tekstprompt til embeddings, som diffusionsmodellen forstår |
| **Diffusion Model** (Z-Image Turbo) | Det centrale neurale netværk, der iterativt fjerner støj fra latente repræsentationer og omdanner dem til billeder |
| **VAE** (Variational Autoencoder) | Koder billeder til/fra det latente rum (dekoder de endelige latenter til pixels) |
| **LoRA** (valgfri) | Letvægtsadaptere, der ændrer stil eller motiv uden at gentræne den underliggende model |

Hver node i workflowet svarer til en af disse komponenter. Data flyder fra venstre mod højre: tekst → embeddings → guidet støjfjernelse → latenter → endeligt billede.
## Generering af dit første billede

Z-Image Turbo-modellen er allerede indlæst. Sådan genererer du et billede:

1. **Indtast din prompt** i den primære Z-Image Node. Vær beskrivende. Her er et eksempel:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Valgfrit)**: Bekræft eller finjuster andre specifikke indstillinger i subgraph'en.
3. **Klik på den blå "Run Workflow"** i det højre hjørne (eller tryk på `Ctrl+Enter`)
4. Se, hvordan noderne fremhæves, mens hvert trin udføres

Hele workflow-udførelsen skal være færdig på under 30 sekunder. Dit genererede billede vises i **Save Image**-noden og gemmes i mappen `output/`.

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


## Justering af genereringsparametre

### KSampler-indstillinger

KSampler-noden styrer den centrale diffusionsproces:

| Parameter | Hvad den styrer | Anbefalet til Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Antal denoising-iterationer | 4–10 (turbo-modeller er destilleret til færre trin) |
| **cfg** | Classifier-free guidance scale—hvor tæt der følges prompten | 1.0–2.0 (turbo-modeller bruger meget lav guidance) |
| **sampler_name** | Denoising-algoritme | `euler` og `res_multistep` fungerer godt til turbo-modeller |
| **scheduler** | Kurve for støjplan | `normal` eller `simple` |
| **seed** | Tilfældigt seed til reproducerbarhed | Angiv faste værdier for at iterere på en komposition |

### Billedstørrelse

For at justere outputdimensionerne, find **Empty Latent Image**-noden og rediger **width** og **height**. Hold dimensionerne på eller under 1024 pixels på den længste side for optimal kvalitet.

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow**-noden er en specialiseret sampling-modifikator, der justerer, hvordan diffusionsprocessen håndterer støjplanlægning. Du vil se denne node forbundet til modeloutputtet i Z-Image Turbo-workflowet.

| Parameter | Hvad den styrer | Anbefalede værdier |
|-----------|------------------|-------------------|
| **shift** | Justerer timingen for støjplanen—højere værdier flytter mere detaljeforfining til senere trin | 1.0–4.0 (standard er 3.0) |

Hvornår **shift** skal justeres:

- **Lavere værdier (1.0–2.0)**: Hurtigere konvergens, godt til enkle kompositioner
- **Højere værdier (3.0–4.0)**: Mere gradvis forfining, kan forbedre finere detaljer i komplekse scener

AuraFlow-sampling-metoden er specifikt designet til flow-matching-modeller som Z-Image Turbo og sikrer korrekt støjfordeling gennem hele genereringsprocessen.

## Arbejde med workflows

### Gemme workflows

Klik på **Save**-knappen i menuen for at eksportere dit workflow som en JSON-fil. Dette gemmer:

- Alle noder og deres parametre
- Alle forbindelser mellem noder
- Nuværende prompt-tekst

### Indlæse workflows

Træk en workflow-JSON-fil ind på lærredet, eller brug **Load** fra menuen. Det Z-Image Turbo-workflow, du ser som standard, er indlæst fra en gemt workflow-fil.

### Deling af workflows

Workflows er selvstændige—del JSON-filen med kolleger, så kan de genskabe din nøjagtige opsætning. Dette gør ComfyUI fremragende til kollaborativ eksperimentering.

## Næste skridt

- **Udforsk LoRA-noder**: Anvend stil- eller emnetilpassere uden gentræning
- **Tilføj negative prompts**: Forbind en anden CLIP Text Encode-node til KSamplers **negative**-conditioning-input for at styre modellen væk fra uønskede træk som slør, artefakter eller vandmærker
- **Byg brugerdefinerede workflows**: Kæd flere genereringer sammen, tilføj opskalering, eller opret billedvariationer
- **Gennemse community-workflows**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) har mange brugsklare workflows

ComfyUIs styrke er eksperimentering: forbind noder på forskellige måder, juster parametre, og observer hvordan hver ændring påvirker outputtet. Denne praktiske udforskning opbygger intuition for, hvordan diffusionsmodeller fungerer.

For yderligere information, se [ComfyUI-dokumentationen](https://docs.comfy.org/).