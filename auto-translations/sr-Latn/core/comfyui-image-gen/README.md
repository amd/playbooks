<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj vodič koristi posebne oznake koje GitHub ne može da prikaže. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->

## Pregled

ComfyUI je moćan, čvorno zasnovan interfejs za Stable Diffusion i druge difuzione modele. Za razliku od tradicionalnih interfejsa za pretvaranje teksta u sliku sa jednostavnim poljima za unos, ComfyUI izlaže ceo pipeline generisanja slike kao vizuelni graf, dajući vam preciznu kontrolu nad svakim korakom, od enkodiranja teksta preko manipulacije latentnim prostorom do finalnog dekodiranja.

Ovaj vodič vas uči kako da koristite ComfyUI sa modelom Z Image Turbo na vašem GPU-u kako biste generisali visokokvalitetne AI slike.

## Šta ćete naučiti

- Kako da pokrenete ComfyUI i učitate Z-Image Turbo šablon
- Razumevanje komponenti difuzionog pipeline-a
- Generisanje slika i podešavanje parametara generisanja
- Čuvanje i deljenje radnih tokova

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje neophodnog softvera

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Dodelite vašem korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Kreiranje virtuelnog okruženja
Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pokrenite sledeću komandu da biste kreirali venv:

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


## Pokretanje ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Da biste pokrenuli ComfyUI na Windows-u, kliknite na ComfyUI Desktop Launcher koji se nalazi na vašoj radnoj površini. Pratite korake da biste instalirali lokalnu verziju sa AMD-om.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Zatim kliknite na dugme ComfyUI na vrhu sredine aplikacije. Ovo će otvoriti karticu sa podešavanjima. Otvorite karticu Storage i uverite se da su putanje podešene na sledeći način kako biste pristupili unapred instaliranim modelima.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Da biste pokrenuli ComfyUI na Linux-u, kliknite na ComfyUI prečicu na taskbar-u. Trebalo bi da se sam otvori u prozoru pregledača.
>**Savet**: ComfyUI i njegovi modeli se čuvaju na `~/.local/share/ComfyUI/models`. Ovde možete ručno da dodate radne tokove ili nove modele.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Da biste pokrenuli ComfyUI na Windows-u, jednostavno kliknite na ComfyUI prečicu na vašoj radnoj površini.
<!-- @os:end -->

<!-- @os:linux -->

Da biste pokrenuli ComfyUI:

1. Uverite se da se nalazite u ComfyUI direktorijumu. 
2. Pokrenite `python3 main.py --use-pytorch-cross-attention`

ComfyUI pokreće lokalni veb server. Otvorite pregledač na `http://127.0.0.1:8188` da biste pristupili interfejsu.

> **Savet**: Ostavite prozor terminala otvorenim dok koristite ComfyUI. Zatvaranje prozora će zaustaviti server.
<!-- @os:end -->
<!-- @device:end -->


## Pronalaženje Z-Image Turbo šablona

Pre generisanja slika, potrebno je da učitate Z-Image Turbo šablon. Evo kako da ga pronađete:

1. **Pogledajte na krajnjoj levoj ivici ekrana** — tu se nalazi vertikalna traka sa alatkama koja se pruža od vrha do dna na krajnjoj levoj strani aplikacije.

2. **Pronađite ikonicu fascikle** — u toj levoj traci sa alatkama, potražite ikonicu koja liči na fasciklu. Kada pređete mišem preko nje, označena je kao "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Kliknite na ikonicu fascikle** — ovo otvara panel Templates.

4. **Pretražite "Z-Image Turbo"** — koristite traku za pretragu ili skrolujte kroz dostupne šablone da biste pronašli radni tok Z-Image Turbo Text To Image, a zatim kliknite da ga učitate.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Preuzimanje modela

<!-- @require:comfyui-models -->

## Razumevanje interfejsa

Kada se učita Z-Image Turbo šablon, videćete platno sa 2 glavna čvora. Prvi čvor se zove 'Text to Image (Z-Image-Turbo)', a drugi čvor služi za pregled slike. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Na Z-Image čvoru, kliknite na dugme u gornjem desnom uglu da biste proširili čvor i videli podgraf.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Komponente pipeline-a

Radni tok Z-Image Turbo koristi četiri ključne komponente modela koje rade zajedno:

| Komponenta | Uloga |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Pretvara vaš tekstualni prompt u embedding-e koje difuzioni model razume |
| **Diffusion Model** (Z-Image Turbo) | Osnovna neuronska mreža koja iterativno uklanja šum iz latentnih reprezentacija i pretvara ih u slike |
| **VAE** (Variational Autoencoder) | Enkoduje slike u/iz latentnog prostora (dekoduje finalne latente u piksele) |
| **LoRA** (opciono) | Lagani adapteri koji menjaju stil ili subjekat bez ponovnog treniranja osnovnog modela |

Svaki čvor u radnom toku odgovara jednoj od ovih komponenti. Podaci teku sleva nadesno: tekst → embedding-i → vođeno uklanjanje šuma → latenti → finalna slika.

## Generisanje vaše prve slike

Model Z-Image Turbo je već učitan. Da biste generisali sliku:

1. **Unesite vaš prompt** u glavni Z-Image čvor. Budite deskriptivni. Evo primera:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opciono)**: Potvrdite ili prilagodite bilo koja druga specifična podešavanja unutar podgrafa.
3. **Kliknite na plavo dugme "Run Workflow"** u desnom uglu (ili pritisnite `Ctrl+Enter`)
4. Posmatrajte kako se čvorovi osvetljavaju dok se svaki korak izvršava

Ceo radni tok bi trebalo da se izvrši za manje od 30 sekundi. Vaša generisana slika se pojavljuje u čvoru **Save Image** i čuva se u fascikli `output/`.

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


## Podešavanje parametara generisanja
### Podešavanja KSampler-a

Čvor KSampler kontroliše osnovni proces difuzije:

| Parametar | Šta kontroliše | Preporučeno za Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Broj iteracija uklanjanja šuma | 4–10 (turbo modeli su destilovani za manji broj koraka) |
| **cfg** | Skala vođenja bez klasifikatora (classifier-free guidance) — koliko blisko se prati prompt | 1.0–2.0 (turbo modeli koriste veoma nisko vođenje) |
| **sampler_name** | Algoritam za uklanjanje šuma | `euler` i `res_multistep` dobro funkcionišu za turbo modele |
| **scheduler** | Kriva rasporeda šuma | `normal` ili `simple` |
| **seed** | Nasumično seme za reproduktivnost | Postavite fiksne vrednosti da biste iterirali na kompoziciji |

### Veličina slike

Da biste podesili dimenzije izlaza, pronađite čvor **Empty Latent Image** i izmenite **width** i **height**. Držite dimenzije na ili ispod 1024 piksela na najdužoj strani radi optimalnog kvaliteta.

### ModelSamplingAuraFlow

Čvor **ModelSamplingAuraFlow** je specijalizovani modifikator uzorkovanja koji podešava kako proces difuzije obrađuje raspored šuma. Videćete ovaj čvor povezan sa izlazom modela u Z-Image Turbo radnom toku.

| Parametar | Šta kontroliše | Preporučene vrednosti |
|-----------|------------------|-------------------|
| **shift** | Podešava tajming rasporeda šuma — veće vrednosti prebacuju više usavršavanja detalja na kasnije korake | 1.0–4.0 (podrazumevano je 3.0) |

Kada podesiti **shift**:

- **Niže vrednosti (1.0–2.0)**: Brža konvergencija, dobro za jednostavne kompozicije
- **Više vrednosti (3.0–4.0)**: Postepenije usavršavanje, može poboljšati fine detalje u složenim scenama

Metod uzorkovanja AuraFlow je posebno dizajniran za modele koji koriste flow-matching, poput Z-Image Turbo, obezbeđujući pravilnu raspodelu šuma tokom celog procesa generisanja.

## Rad sa radnim tokovima

### Čuvanje radnih tokova

Kliknite na dugme **Save** u meniju da biste izvezli svoj radni tok kao JSON fajl. Ovo obuhvata:

- Sve čvorove i njihove parametre
- Sve veze između čvorova
- Trenutni tekst prompta

### Učitavanje radnih tokova

Prevucite JSON fajl radnog toka na platno, ili koristite **Load** iz menija. Z-Image Turbo radni tok koji podrazumevano vidite učitan je iz sačuvanog fajla radnog toka.

### Deljenje radnih tokova

Radni tokovi su samostalni — podelite JSON fajl sa kolegama, i oni mogu reprodukovati vaše tačno podešavanje. Ovo čini ComfyUI odličnim za zajedničko eksperimentisanje.

## Sledeći koraci

- **Istražite LoRA čvorove**: Primenite adaptere za stil ili subjekat bez ponovnog treniranja
- **Dodajte negativne promptove**: Povežite drugi CLIP Text Encode čvor sa **negative** ulazom za kondicioniranje na KSampler-u da biste usmerili model dalje od neželjenih karakteristika poput zamućenja, artefakata ili vodenih žigova
- **Napravite prilagođene radne tokove**: Povežite više generisanja u lanac, dodajte uvećanje rezolucije ili kreirajte varijacije slika
- **Pregledajte radne tokove zajednice**: [ComfyUI primeri](https://github.com/comfyanonymous/ComfyUI_examples) sadrže mnoge spremne radne tokove za korišćenje

Snaga ComfyUI-ja leži u eksperimentisanju: povezujte čvorove na različite načine, podešavajte parametre i posmatrajte kako svaka promena utiče na izlaz. Ovo praktično istraživanje gradi intuiciju o tome kako funkcionišu difuzioni modeli.

Za više informacija, pogledajte [ComfyUI dokumentaciju](https://docs.comfy.org/).