<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

ComfyUI är ett kraftfullt, nodbaserat gränssnitt för Stable Diffusion och andra diffusionsmodeller. Till skillnad från traditionella text-till-bild-gränssnitt med enkla promptrutor exponerar ComfyUI hela bildgenereringspipelinen som ett visuellt diagram, vilket ger dig detaljerad kontroll över varje steg från textkodning till manipulation av latent rymd till slutlig avkodning.

Den här handledningen lär dig hur du använder ComfyUI med Z Image Turbo-modellen på din GPU för att generera högkvalitativa AI-bilder.

## Vad du kommer att lära dig

- Hur du startar ComfyUI och laddar Z-Image Turbo-mallen
- Förståelse för komponenter i diffusionspipelinen
- Generera bilder och justera genereringsparametrar
- Spara och dela arbetsflöden

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera programvarukrav

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Skapa en virtuell miljö
På Linux, öppna en terminal i valfri katalog och kör följande kommando för att skapa en venv:

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


## Starta ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
För att starta ComfyUI på Windows, klicka på ComfyUI Desktop-startprogrammet som finns på ditt skrivbord. Följ stegen för att installera den lokala versionen med AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Klicka sedan på ComfyUI-knappen längst upp i mitten av appen. Detta öppnar en inställningsflik. Öppna fliken Lagring och se till att sökvägarna är inställda enligt följande för att komma åt de förinstallerade modellerna.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
För att starta ComfyUI på Linux, klicka på ComfyUI-genvägen i aktivitetsfältet. Den bör öppnas automatiskt i ett webbläsarfönster.
>**Tips**: ComfyUI och dess modeller lagras på `~/.local/share/ComfyUI/models`. Det är här du manuellt kan lägga till arbetsflöden eller nya modeller.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
För att starta ComfyUI på Windows, klicka helt enkelt på ComfyUI-genvägen på ditt skrivbord.
<!-- @os:end -->

<!-- @os:linux -->

Så här startar du ComfyUI:

1. Se till att du befinner dig i ComfyUI-katalogen. 
2. Kör `python3 main.py --use-pytorch-cross-attention`

ComfyUI startar en lokal webbserver. Öppna din webbläsare och gå till `http://127.0.0.1:8188` för att komma åt gränssnittet.

> **Tips**: Håll terminalfönstret öppet medan du använder ComfyUI. Om du stänger det stoppas servern.
<!-- @os:end -->
<!-- @device:end -->


## Hitta Z-Image Turbo-mallen

Innan du genererar bilder måste du ladda Z-Image Turbo-mallen. Så här hittar du den:

1. **Titta längst till vänster på skärmen**—det finns ett vertikalt verktygsfält som löper uppifrån och ned på appens yttersta vänstra sida.

2. **Hitta mappikonen**—i det vänstra verktygsfältet, leta efter en ikon som ser ut som en mapp. När du håller muspekaren över den visas etiketten "Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klicka på mappikonen**—detta öppnar panelen Templates.

4. **Sök efter "Z-Image Turbo"**—använd sökfältet eller bläddra igenom de tillgängliga mallarna för att hitta arbetsflödet Z-Image Turbo Text To Image, och klicka sedan för att ladda det.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Ladda ned modeller

<!-- @require:comfyui-models -->

## Förstå gränssnittet

När Z-Image Turbo-mallen laddas ser du en arbetsyta med 2 huvudnoder. Den första noden kallas 'Text to Image (Z-Image-Turbo)', och den andra noden används för att visa bilden. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


På Z-Image-noden klickar du på knappen längst upp till höger för att expandera noden och se undergrafen.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Pipelinekomponenter

Z-Image Turbo-arbetsflödet använder fyra viktiga modellkomponenter som samverkar:

| Komponent | Roll |
|-----------|------|
| **Textkodare** (Qwen 3 4B) | Konverterar din textprompt till inbäddningar som diffusionsmodellen förstår |
| **Diffusionsmodell** (Z-Image Turbo) | Det centrala neurala nätverket som iterativt avbrusrar latenta representationer till bilder |
| **VAE** (Variationell autoenkodare) | Kodar bilder till/från latent rymd (avkodar de slutliga latentvärdena till pixlar) |
| **LoRA** (valfritt) | Lättviktsadaptrar som modifierar stil eller motiv utan att träna om basmodellen |

Varje nod i arbetsflödet motsvarar en av dessa komponenter. Data flödar från vänster till höger: text → inbäddningar → guidad avbrusning → latenta värden → slutlig bild.

## Generera din första bild

Z-Image Turbo-modellen är redan laddad. Så här genererar du en bild:

1. **Ange din prompt** i huvud-Z-Image-noden. Var beskrivande. Här är ett exempel:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Valfritt)**: Bekräfta eller justera eventuella andra specifika inställningar i undergrafen.
3. **Klicka på den blå "Run Workflow"**-knappen i det högra hörnet (eller tryck på `Ctrl+Enter`)
4. Se noderna markeras när varje steg körs

Hela arbetsflödeskörningen bör slutföras på mindre än 30 sekunder. Din genererade bild visas i noden **Save Image** och sparas i mappen `output/`.

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


## Justera genereringsparametrar

### KSampler-inställningar

KSampler-noden styr den centrala diffusionsprocessen:

| Parameter | Vad den styr | Rekommenderat för Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Antal avbrusningsiterationer | 4–10 (turbomodeller är destillerade för färre steg) |
| **cfg** | Klassificeringsfri vägledningsskala—hur noga modellen följer prompten | 1,0–2,0 (turbomodeller använder mycket låg vägledning) |
| **sampler_name** | Avbrusningsalgoritm | `euler` och `res_multistep` fungerar bra för turbomodeller |
| **scheduler** | Kurva för brusschema | `normal` eller `simple` |
| **seed** | Slumpmässigt frö för reproducerbarhet | Ange fasta värden för att iterera på en komposition |

### Bildstorlek

För att justera utdatadimensioner, hitta noden **Empty Latent Image** och ändra **width** och **height**. Håll dimensionerna vid eller under 1024 pixlar på den längsta sidan för optimal kvalitet.

### ModelSamplingAuraFlow

Noden **ModelSamplingAuraFlow** är en specialiserad samplingsmodifierare som justerar hur diffusionsprocessen hanterar brusschemaläggning. Du ser den här noden ansluten till modellutdata i Z-Image Turbo-arbetsflödet.

| Parameter | Vad den styr | Rekommenderade värden |
|-----------|------------------|-------------------|
| **shift** | Justerar tidpunkten för brusschemat—högre värden skjuter mer detaljförfining till senare steg | 1,0–4,0 (standard är 3,0) |

När du bör justera **shift**:

- **Lägre värden (1,0–2,0)**: Snabbare konvergens, bra för enkla kompositioner
- **Högre värden (3,0–4,0)**: Mer gradvis förfining, kan förbättra fina detaljer i komplexa scener

AuraFlow-samplingsmetoden är specifikt utformad för flödesmatchningsmodeller som Z-Image Turbo och säkerställer korrekt brusfördelning under hela genereringsprocessen.

## Arbeta med arbetsflöden

### Spara arbetsflöden

Klicka på knappen **Save** i menyn för att exportera ditt arbetsflöde som en JSON-fil. Detta sparar:

- Alla noder och deras parametrar
- Alla anslutningar mellan noder
- Aktuell prompttext

### Ladda arbetsflöden

Dra en JSON-fil med arbetsflöde till arbetsytan, eller använd **Load** från menyn. Z-Image Turbo-arbetsflödet som visas som standard laddas från en sparad arbetsflödesfil.

### Dela arbetsflöden

Arbetsflöden är självständiga—dela JSON-filen med kollegor så kan de återskapa din exakta konfiguration. Detta gör ComfyUI utmärkt för samarbetsbaserad experimentering.

## Nästa steg

- **Utforska LoRA-noder**: Tillämpa stil- eller motivadaptrar utan att träna om
- **Lägg till negativa prompter**: Anslut en andra CLIP Text Encode-nod till den **negativa** konditioneringsingången på KSampler för att styra modellen bort från oönskade egenskaper som oskärpa, artefakter eller vattenstämplar
- **Bygg anpassade arbetsflöden**: Kedja ihop flera genereringar, lägg till uppskalning eller skapa bildvariationer
- **Bläddra bland communityarbetsflöden**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) har många färdiga arbetsflöden

ComfyUI:s styrka ligger i experimentering: anslut noder på olika sätt, justera parametrar och observera hur varje förändring påverkar resultatet. Denna praktiska utforskning bygger intuition för hur diffusionsmodeller fungerar.

För mer information, se [ComfyUI-dokumentationen](https://docs.comfy.org/).