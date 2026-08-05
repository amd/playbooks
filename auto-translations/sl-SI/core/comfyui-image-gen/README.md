<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

ComfyUI je zmogljiv, na vozliščih temelječ vmesnik za Stable Diffusion in druge difuzijske modele. Za razliko od tradicionalnih vmesnikov za pretvorbo besedila v sliko z enostavnimi poljI za vnos poziva, ComfyUI prikaže celoten cevovod za generiranje slik kot vizualni graf, kar vam omogoča natančen nadzor nad vsakim korakom, od kodiranja besedila do manipulacije latentnega prostora do končnega dekodiranja.

Ta vadnica vas nauči, kako uporabljati ComfyUI z modelom Z Image Turbo na svojem GPU-ju za generiranje visokokakovostnih slik z umetno inteligenco.

## Kaj se boste naučili

- Kako zagnati ComfyUI in naložiti predlogo Z-Image Turbo
- Razumevanje komponent difuzijskega cevovoda
- Generiranje slik in prilagajanje parametrov generiranja
- Shranjevanje in deljenje delovnih tokov

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Nameščanje potrebne programske opreme

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Dodelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev se odjavite in ponovno prijavite):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Ustvarite virtualno okolje
V sistemu Linux odprite terminal v mapi po vaši izbiri in zaženite naslednji ukaz za ustvarjanje venv:

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


## Zagon ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Za zagon ComfyUI v sistemu Windows kliknite zaganjalnik ComfyUI Desktop, ki ga najdete na namizju. Sledite korakom za namestitev lokalne različice z AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Nato kliknite gumb ComfyUI na sredini vrha aplikacije. S tem se odpre zavihek z nastavitvami. Odprite zavihek Storage in preverite, ali so poti nastavljene, kot sledi, da boste lahko dostopali do vnaprej nameščenih modelov.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Na AMD Ryzen™ AI Halo se ComfyUI izvaja v vnaprej pripravljenem vsebniku, ki ne zahteva dodatne nastavitve Python.

Za zagon ComfyUI v sistemu Linux kliknite bližnjico ComfyUI v opravilni vrstici. Odpreti bi se moralo samodejno v oknu brskalnika.
>**Nasvet**: ComfyUI in njegovi modeli so shranjeni na `~/.local/share/ComfyUI/models`. Tu lahko ročno dodate delovne tokove ali nove modele.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Za zagon ComfyUI v sistemu Windows preprosto kliknite bližnjico ComfyUI na namizju.
<!-- @os:end -->

<!-- @os:linux -->

Za zagon ComfyUI:

1. Prepričajte se, da ste v mapi ComfyUI. 
2. Zaženite `python3 main.py --use-pytorch-cross-attention`

ComfyUI zažene lokalni spletni strežnik. Odprite brskalnik na `http://127.0.0.1:8188` za dostop do vmesnika.

> **Nasvet**: Med uporabo ComfyUI naj bo terminalsko okno odprto. Če ga zaprete, se strežnik ustavi.
<!-- @os:end -->
<!-- @device:end -->


## Iskanje predloge Z-Image Turbo

Preden začnete generirati slike, morate naložiti predlogo Z-Image Turbo. Tukaj je opisano, kako jo najdete:

1. **Poglejte na skrajni levi rob zaslona** — tam je navpična orodna vrstica, ki poteka od vrha do dna na skrajno levi strani aplikacije.

2. **Poiščite ikono mape** — v tej levi orodni vrstici poiščite ikono, ki je videti kot mapa. Ko nanjo pomaknete kazalec, je označena z "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Kliknite ikono mape** — s tem se odpre podokno s predlogami (Templates).

4. **Poiščite "Z-Image Turbo"** — uporabite iskalno vrstico ali se pomikajte po razpoložljivih predlogah, da najdete delovni tok Z-Image Turbo Text To Image, nato pa kliknite, da ga naložite.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Prenos modelov

<!-- @require:comfyui-models -->

## Razumevanje vmesnika

Ko se naloži predloga Z-Image Turbo, boste videli platno z 2 glavnima vozliščema. Prvo vozlišče se imenuje 'Text to Image (Z-Image-Turbo)', drugo vozlišče pa je namenjeno ogledu slike. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


V vozlišču Z-Image kliknite gumb zgoraj desno, da razširite vozlišče in vidite podgraf.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Komponente cevovoda

Delovni tok Z-Image Turbo uporablja štiri ključne komponente modela, ki delujejo skupaj:

| Komponenta | Vloga |
|-----------|------|
| **Kodirnik besedila** (Qwen 3 4B) | Pretvori vaš besedilni poziv v vdelave (embeddings), ki jih razume difuzijski model |
| **Difuzijski model** (Z-Image Turbo) | Osrednja nevronska mreža, ki iterativno odstranjuje šum iz latentnih predstavitev in jih spreminja v slike |
| **VAE** (Variacijski avtokoder) | Kodira slike v latentni prostor in iz njega (dekodira končne latente v piksle) |
| **LoRA** (neobvezno) | Lahki adapterji, ki spremenijo slog ali motiv brez ponovnega učenja osnovnega modela |

Vsako vozlišče v delovnem toku ustreza eni od teh komponent. Podatki potekajo od leve proti desni: besedilo → vdelave → vodeno odstranjevanje šuma → latenti → končna slika.
## Ustvarjanje prve slike

Model Z-Image Turbo je že naložen. Za ustvarjanje slike:

1. **Vnesite svoj poziv** v glavno vozlišče Z-Image. Bodite opisni. Tukaj je primer:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Neobvezno)**: Potrdite ali prilagodite katere koli druge specifične nastavitve znotraj podgrafa.
3. **Kliknite modri gumb »Run Workflow«** v desnem kotu (ali pritisnite `Ctrl+Enter`)
4. Opazujte, kako se vozlišča osvetlijo ob izvajanju vsakega koraka

Celotno izvajanje poteka opravila naj bi bilo zaključeno v manj kot 30 sekundah. Vaša ustvarjena slika se prikaže v vozlišču **Save Image** in se shrani v mapo `output/`.

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


## Prilagajanje parametrov ustvarjanja

### Nastavitve KSampler

Vozlišče KSampler nadzoruje osrednji postopek difuzije:

| Parameter | Kaj nadzoruje | Priporočeno za Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Število iteracij odstranjevanja šuma | 4–10 (turbo modeli so destilirani za manjše število korakov) |
| **cfg** | Lestvica vodenja brez klasifikatorja (classifier-free guidance) – kako natančno slediti pozivu | 1,0–2,0 (turbo modeli uporabljajo zelo nizko vodenje) |
| **sampler_name** | Algoritem odstranjevanja šuma | `euler` in `res_multistep` dobro delujeta za turbo modele |
| **scheduler** | Krivulja razporeda šuma | `normal` ali `simple` |
| **seed** | Naključno seme za ponovljivost | Nastavite fiksne vrednosti za ponavljanje kompozicije |

### Velikost slike

Za prilagoditev izhodnih dimenzij poiščite vozlišče **Empty Latent Image** in spremenite **width** in **height**. Za optimalno kakovost naj bodo dimenzije na daljši strani enake ali manjše od 1024 slikovnih pik.

### ModelSamplingAuraFlow

Vozlišče **ModelSamplingAuraFlow** je specializiran modifikator vzorčenja, ki prilagaja, kako postopek difuzije obravnava razporejanje šuma. To vozlišče boste videli povezano z izhodom modela v poteku dela Z-Image Turbo.

| Parameter | Kaj nadzoruje | Priporočene vrednosti |
|-----------|------------------|-------------------|
| **shift** | Prilagaja časovno razporeditev šuma – višje vrednosti premaknejo več izpopolnjevanja podrobnosti na kasnejše korake | 1,0–4,0 (privzeta vrednost je 3,0) |

Kdaj prilagoditi **shift**:

- **Nižje vrednosti (1,0–2,0)**: Hitrejša konvergenca, primerno za preproste kompozicije
- **Višje vrednosti (3,0–4,0)**: Postopnejše izpopolnjevanje, lahko izboljša drobne podrobnosti pri kompleksnih prizorih

Metoda vzorčenja AuraFlow je posebej zasnovana za modele z ujemanjem toka (flow-matching), kot je Z-Image Turbo, kar zagotavlja pravilno porazdelitev šuma skozi celoten postopek ustvarjanja.

## Delo s poteki dela

### Shranjevanje potekov dela

Kliknite gumb **Save** v meniju, da izvozite potek dela kot datoteko JSON. To zajame:

- Vsa vozlišča in njihove parametre
- Vse povezave med vozlišči
- Trenutno besedilo poziva

### Nalaganje potekov dela

Povlecite datoteko JSON s potekom dela na platno ali uporabite **Load** iz menija. Potek dela Z-Image Turbo, ki ga vidite privzeto, je naložen iz shranjene datoteke poteka dela.

### Deljenje potekov dela

Poteki dela so samostojni – delite datoteko JSON s sodelavci in ti bodo lahko ponovili vašo natančno nastavitev. To naredi ComfyUI odlično orodje za skupno eksperimentiranje.

## Naslednji koraki

- **Raziščite vozlišča LoRA**: Uporabite prilagojevalnike sloga ali predmeta brez ponovnega učenja
- **Dodajte negativne pozive**: Povežite drugo vozlišče CLIP Text Encode z vhodom pogojevanja **negative** vozlišča KSampler, da model usmerite stran od nezaželenih lastnosti, kot so zamegljenost, artefakti ali vodni žigi
- **Zgradite prilagojene poteke dela**: Povežite več ustvarjanj v verigo, dodajte povečanje ločljivosti ali ustvarite variacije slik
- **Prebrskajte poteke dela skupnosti**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) vsebuje veliko pripravljenih potekov dela za takojšnjo uporabo

Moč ComfyUI je v eksperimentiranju: povežite vozlišča na drugačne načine, prilagajajte parametre in opazujte, kako vsaka sprememba vpliva na izhod. To praktično raziskovanje gradi intuicijo o delovanju difuzijskih modelov.

Za več informacij si oglejte [ComfyUI Documentation](https://docs.comfy.org/).