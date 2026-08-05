<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

ComfyUI er et kraftig, nodebasert grensesnitt for Stable Diffusion og andre diffusjonsmodeller. I motsetning til tradisjonelle tekst-til-bilde-grensesnitt med enkle promptbokser, eksponerer ComfyUI hele bildegenereringspipelinen som en visuell graf, noe som gir deg finkornet kontroll over hvert trinn fra tekstkoding til manipulasjon av latent rom til endelig dekoding.

Denne opplæringen lærer deg hvordan du bruker ComfyUI med Z Image Turbo-modellen på GPU-en din for å generere AI-bilder av høy kvalitet.

## Hva du vil lære

- Hvordan starte ComfyUI og laste inn Z-Image Turbo-malen
- Forstå komponentene i diffusjonspipelinen
- Generere bilder og justere genereringsparametere
- Lagre og dele arbeidsflyter

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Opprett et virtuelt miljø
På Linux åpner du en terminal i katalogen du ønsker, og kjører følgende kommando for å opprette et venv:

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


## Starte ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
For å starte ComfyUI på Windows, klikk på ComfyUI Desktop Launcher som finnes på skrivebordet ditt. Følg trinnene for å installere den lokale versjonen med AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Klikk deretter på ComfyUI-knappen øverst i midten av appen. Dette åpner en innstillingsfane. Åpne Storage-fanen og kontroller at banene er satt som følger for å få tilgang til de forhåndsinstallerte modellene.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
På AMD Ryzen™ AI Halo kjører ComfyUI i en forhåndsbygget container som ikke krever noe ekstra Python-oppsett.

For å starte ComfyUI på Linux, klikk på ComfyUI-snarveien i oppgavelinjen. Den skal åpne seg selv i et nettleservindu.
>**Tips**: ComfyUI og modellene lagres i `~/.local/share/ComfyUI/models`. Her kan du manuelt legge til arbeidsflyter eller nye modeller.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
For å starte ComfyUI på Windows, klikk bare på ComfyUI-snarveien på skrivebordet ditt.
<!-- @os:end -->

<!-- @os:linux -->

For å starte ComfyUI:

1. Sørg for at du er i ComfyUI-katalogen. 
2. Kjør `python3 main.py --use-pytorch-cross-attention`

ComfyUI starter en lokal webserver. Åpne nettleseren din på `http://127.0.0.1:8188` for å få tilgang til grensesnittet.

> **Tips**: Hold terminalvinduet åpent mens du bruker ComfyUI. Hvis du lukker det, stopper serveren.
<!-- @os:end -->
<!-- @device:end -->


## Finne Z-Image Turbo-malen

Før du genererer bilder, må du laste inn Z-Image Turbo-malen. Slik finner du den:

1. **Se helt til venstre på skjermen** – det er en vertikal verktøylinje som går fra topp til bunn på venstre side av appen.

2. **Finn mappeikonet** – i verktøylinjen til venstre, se etter et ikon som ser ut som en mappe. Når du holder musepekeren over det, er det merket «Templates».

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klikk på mappeikonet** – dette åpner Templates-panelet.

4. **Søk etter «Z-Image Turbo»** – bruk søkefeltet eller bla gjennom de tilgjengelige malene for å finne arbeidsflyten Z-Image Turbo Text To Image, og klikk deretter for å laste den inn.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Laste ned modeller

<!-- @require:comfyui-models -->

## Forstå grensesnittet

Når Z-Image Turbo-malen lastes inn, ser du et lerret med 2 hovednoder. Den første noden heter «Text to Image (Z-Image-Turbo)», og den andre noden er for å vise bildet. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


På Z-Image-noden klikker du på knappen øverst til høyre for å utvide noden og se subgrafen.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Pipelinekomponenter

Z-Image Turbo-arbeidsflyten bruker fire viktige modellkomponenter som fungerer sammen:

| Komponent | Rolle |
|-----------|------|
| **Tekstkoder** (Qwen 3 4B) | Konverterer tekstprompten din til embeddinger som diffusjonsmodellen forstår |
| **Diffusjonsmodell** (Z-Image Turbo) | Det sentrale nevrale nettverket som iterativt fjerner støy fra latente representasjoner til bilder |
| **VAE** (Variational Autoencoder) | Koder bilder til/fra latent rom (dekoder de endelige latentene til piksler) |
| **LoRA** (valgfritt) | Lettvektsadaptere som endrer stil eller motiv uten å trene basismodellen på nytt |

Hver node i arbeidsflyten tilsvarer én av disse komponentene. Data flyter fra venstre til høyre: tekst → embeddinger → veiledet støyfjerning → latenter → endelig bilde.
## Generere ditt første bilde

Z-Image Turbo-modellen er allerede lastet inn. Slik genererer du et bilde:

1. **Skriv inn ledeteksten din** i hoved-Z-Image-noden. Vær beskrivende. Her er et eksempel:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Valgfritt)**: Bekreft eller juster andre spesifikke innstillinger i undergrafen.
3. **Klikk på den blå "Run Workflow"** i høyre hjørne (eller trykk `Ctrl+Enter`)
4. Se hvordan nodene lyser opp etter hvert som hvert trinn utføres

Hele arbeidsflytkjøringen bør fullføres på under 30 sekunder. Det genererte bildet ditt vises i **Save Image**-noden og lagres i mappen `output/`.

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


## Justere genereringsparametere

### KSampler-innstillinger

KSampler-noden styrer selve diffusjonsprosessen:

| Parameter | Hva den styrer | Anbefalt for Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Antall støyfjerningsiterasjoner | 4–10 (turbo-modeller er destillert for færre steg) |
| **cfg** | Klassifiseringsfri veiledningsskala – hvor nøye ledeteksten følges | 1,0–2,0 (turbo-modeller bruker svært lav veiledning) |
| **sampler_name** | Algoritme for støyfjerning | `euler` og `res_multistep` fungerer godt for turbo-modeller |
| **scheduler** | Kurve for støyplan | `normal` eller `simple` |
| **seed** | Tilfeldig frø for reproduserbarhet | Sett faste verdier for å iterere på en komposisjon |

### Bildestørrelse

For å justere utdatadimensjonene, finn **Empty Latent Image**-noden og endre **width** og **height**. Hold dimensjonene på eller under 1024 piksler på den lengste siden for optimal kvalitet.

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow**-noden er en spesialisert samplingsmodifikator som justerer hvordan diffusjonsprosessen håndterer støyplanlegging. Du vil se denne noden koblet til modellutdataen i Z-Image Turbo-arbeidsflyten.

| Parameter | Hva den styrer | Anbefalte verdier |
|-----------|------------------|-------------------|
| **shift** | Justerer tidspunktet for støyplanen – høyere verdier flytter mer detaljforbedring til senere steg | 1,0–4,0 (standard er 3,0) |

Når du bør justere **shift**:

- **Lavere verdier (1,0–2,0)**: Raskere konvergens, godt egnet for enkle komposisjoner
- **Høyere verdier (3,0–4,0)**: Mer gradvis forbedring, kan forbedre finere detaljer i komplekse scener

AuraFlow-samplingsmetoden er spesielt utviklet for flow-matching-modeller som Z-Image Turbo, og sikrer riktig støyfordeling gjennom hele genereringsprosessen.

## Arbeide med arbeidsflyter

### Lagre arbeidsflyter

Klikk på **Save**-knappen i menyen for å eksportere arbeidsflyten din som en JSON-fil. Dette fanger opp:

- Alle noder og deres parametere
- Alle koblinger mellom noder
- Gjeldende ledetekst

### Laste inn arbeidsflyter

Dra en arbeidsflyt-JSON-fil til lerretet, eller bruk **Load** fra menyen. Z-Image Turbo-arbeidsflyten du ser som standard, er lastet inn fra en lagret arbeidsflytfil.

### Dele arbeidsflyter

Arbeidsflyter er selvstendige – del JSON-filen med kolleger, så kan de gjenskape ditt nøyaktige oppsett. Dette gjør ComfyUI utmerket for felles eksperimentering.

## Neste steg

- **Utforsk LoRA-noder**: Bruk stil- eller emnetilpassere uten å trene på nytt
- **Legg til negative ledetekster**: Koble en andre CLIP Text Encode-node til **negative**-konditioneringsinngangen på KSampler for å styre modellen bort fra uønskede trekk som uskarphet, artefakter eller vannmerker
- **Bygg egendefinerte arbeidsflyter**: Kjed sammen flere genereringer, legg til oppskalering, eller lag bildevariasjoner
- **Bla gjennom fellesskapets arbeidsflyter**: [ComfyUI-eksempler](https://github.com/comfyanonymous/ComfyUI_examples) har mange klare arbeidsflyter du kan bruke direkte

ComfyUIs styrke er eksperimentering: koble noder på forskjellige måter, juster parametere, og observer hvordan hver endring påvirker resultatet. Denne praktiske utforskningen bygger intuisjon for hvordan diffusjonsmodeller fungerer.

For mer informasjon, se [ComfyUI-dokumentasjonen](https://docs.comfy.org/).