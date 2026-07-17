<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

ComfyUI on tehokas, solmupohjainen käyttöliittymä Stable Diffusionille ja muille diffuusiomalleille. Toisin kuin perinteiset tekstistä kuvaksi -käyttöliittymät yksinkertaisine kehotekenttineen, ComfyUI esittää koko kuvanluontiprosessin visuaalisena graafina, antaen sinulle tarkan hallinnan jokaisesta vaiheesta tekstin koodauksesta latenttiavaruuden käsittelyyn ja lopulliseen dekoodaukseen.

Tämä opas opettaa sinulle, kuinka käyttää ComfyUI:ta Z Image Turbo -mallin kanssa GPU:llasi korkealaatuisten tekoälykuvien luomiseen.

## Mitä opit

- Kuinka käynnistää ComfyUI ja ladata Z-Image Turbo -malli
- Diffuusioprosessin komponenttien ymmärtäminen
- Kuvien luominen ja luontiparametrien säätäminen
- Työnkulkujen tallentaminen ja jakaminen

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Luo virtuaaliympäristö
Linuxissa avaa pääte haluamassasi hakemistossa ja suorita seuraava komento venv:n luomiseksi:

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


## ComfyUI:n käynnistäminen

<!-- @device:halo_box -->
<!-- @os:windows -->
Käynnistä ComfyUI Windowsissa napsauttamalla työpöydällä olevaa ComfyUI Desktop Launcher -kuvaketta. Seuraa ohjeita asentaaksesi paikallisen version AMD:n kanssa.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Napsauta sitten sovelluksen yläkeskellä olevaa ComfyUI-painiketta. Tämä avaa asetusvalilehden. Avaa Tallennus-välilehti ja varmista, että polut on asetettu seuraavasti, jotta voit käyttää esiasennettuja malleja.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Käynnistä ComfyUI Linuxissa napsauttamalla tehtäväpalkin ComfyUI-pikakuvaketta. Sen pitäisi avautua automaattisesti selainikkunassa.
>**Vinkki**: ComfyUI ja sen mallit on tallennettu hakemistoon `~/.local/share/ComfyUI/models`. Tänne voit lisätä manuaalisesti työnkulkuja tai uusia malleja.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Käynnistä ComfyUI Windowsissa napsauttamalla työpöydällä olevaa ComfyUI-pikakuvaketta.
<!-- @os:end -->

<!-- @os:linux -->

ComfyUI:n käynnistäminen:

1. Varmista, että olet ComfyUI-hakemistossa. 
2. Suorita `python3 main.py --use-pytorch-cross-attention`

ComfyUI käynnistää paikallisen verkkopalvelimen. Avaa selaimesi osoitteeseen `http://127.0.0.1:8188` päästäksesi käyttöliittymään.

> **Vinkki**: Pidä pääteikkuna auki ComfyUI:ta käyttäessäsi. Sen sulkeminen pysäyttää palvelimen.
<!-- @os:end -->
<!-- @device:end -->


## Z-Image Turbo -mallin löytäminen

Ennen kuvien luomista sinun täytyy ladata Z-Image Turbo -malli. Näin löydät sen:

1. **Katso näytön vasenta reunaa**—vasemmassa reunassa kulkee pystysuora työkalupalkki ylhäältä alas.

2. **Etsi kansioikoni**—vasemmasta työkalupalkista etsi kansion näköinen kuvake. Kun viet hiiren sen päälle, se on merkitty "Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Napsauta kansioikonia**—tämä avaa Mallit-paneelin.

4. **Etsi "Z-Image Turbo"**—käytä hakupalkkia tai selaa käytettävissä olevia malleja löytääksesi Z-Image Turbo Text To Image -työnkulun, ja napsauta ladataksesi sen.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Mallien lataaminen

<!-- @require:comfyui-models -->

## Käyttöliittymän ymmärtäminen

Kun Z-Image Turbo -malli latautuu, näet kankaan, jossa on 2 pääsolmua. Ensimmäinen solmu on nimeltään 'Text to Image (Z-Image-Turbo)', ja toinen solmu on kuvan katselua varten.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Napsauta Z-Image-solmussa oikeassa yläkulmassa olevaa painiketta laajentaaksesi solmun ja nähdäksesi aligraafin.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Prosessin komponentit

Z-Image Turbo -työnkulku käyttää neljää keskeistä mallikomponenttia, jotka toimivat yhdessä:

| Komponentti | Rooli |
|-----------|------|
| **Tekstikooderi** (Qwen 3 4B) | Muuntaa tekstikehotteesi upotuksiksi, joita diffuusiomalli ymmärtää |
| **Diffuusiomalli** (Z-Image Turbo) | Ydinneuroverkko, joka iteratiivisesti poistaa kohinaa latenttirepresentaatioista kuviksi |
| **VAE** (Variational Autoencoder) | Koodaa kuvia latenttiavaruuteen ja sieltä pois (dekoodaa lopulliset latentit pikseleiksi) |
| **LoRA** (valinnainen) | Kevyet adapterit, jotka muokkaavat tyyliä tai aihetta ilman perusmallin uudelleenkoulutusta |

Jokainen työnkulun solmu vastaa yhtä näistä komponenteista. Data virtaa vasemmalta oikealle: teksti → upotukset → ohjattu kohinanpoisto → latentit → lopullinen kuva.

## Ensimmäisen kuvasi luominen

Z-Image Turbo -malli on jo ladattu. Kuvan luominen:

1. **Kirjoita kehotteesi** pääasialliseen Z-Image-solmuun. Ole kuvaava. Tässä on esimerkki:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Valinnainen)**: Vahvista tai säädä muita erityisasetuksia aligraafin sisällä.
3. **Napsauta sinistä "Run Workflow"** -painiketta oikeassa kulmassa (tai paina `Ctrl+Enter`)
4. Seuraa, kuinka solmut korostuvat jokaisen vaiheen suoritutuessa

Koko työnkulun suorittamisen pitäisi valmistua alle 30 sekunnissa. Luotu kuvasi näkyy **Save Image** -solmussa ja tallennetaan `output/`-kansioon.

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


## Luontiparametrien säätäminen

### KSampler-asetukset

KSampler-solmu ohjaa diffuusioprosessin ydintä:

| Parametri | Mitä se ohjaa | Suositus Z-Image Turbolle |
|-----------|------------------|-------------------------------|
| **steps** | Kohinanpoistoiteraatioiden määrä | 4–10 (turbomallit on tislattu vähemmille vaiheille) |
| **cfg** | Luokittelijavapaa ohjausskaala—kuinka tarkasti seurataan kehoa | 1.0–2.0 (turbomallit käyttävät hyvin matalaa ohjausta) |
| **sampler_name** | Kohinanpoistoalgoritmi | `euler` ja `res_multistep` toimivat hyvin turbomalleille |
| **scheduler** | Kohinaaikataulukäyrä | `normal` tai `simple` |
| **seed** | Satunnaissiemen toistettavuutta varten | Aseta kiinteät arvot koostumuksen iterointia varten |

### Kuvan koko

Säätääksesi tulostekokoa, etsi **Empty Latent Image** -solmu ja muokkaa **width**- ja **height**-arvoja. Pidä mitat enintään 1024 pikselissä pisimmällä sivulla optimaalisen laadun saavuttamiseksi.

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow**-solmu on erikoistunut näytteenottomuokkain, joka säätää diffuusioprosessin kohinaaikataulutusta. Näet tämän solmun yhdistettynä mallin ulostuloon Z-Image Turbo -työnkulussa.

| Parametri | Mitä se ohjaa | Suositellut arvot |
|-----------|------------------|-------------------|
| **shift** | Säätää kohinaaikataulun ajoitusta—korkeammat arvot siirtävät enemmän yksityiskohtien tarkennusta myöhempiin vaiheisiin | 1.0–4.0 (oletus on 3.0) |

Milloin säätää **shift**-arvoa:

- **Matalammat arvot (1.0–2.0)**: Nopeampi konvergenssi, hyvä yksinkertaisille koostumuksille
- **Korkeammat arvot (3.0–4.0)**: Asteittaisempi tarkentuminen, voi parantaa hienojen yksityiskohtien toistoa monimutkaisissa kohtauksissa

AuraFlow-näytteenottomenetelmä on suunniteltu erityisesti virtaussovitusmalleja, kuten Z-Image Turboa, varten, varmistaen asianmukaisen kohinajakauman koko luontiprosessin ajan.

## Työnkulkujen käyttäminen

### Työnkulkujen tallentaminen

Napsauta valikossa olevaa **Save**-painiketta viedäksesi työnkulkusi JSON-tiedostona. Tämä tallentaa:

- Kaikki solmut ja niiden parametrit
- Kaikki solmujen väliset yhteydet
- Nykyisen kehotetekstin

### Työnkulkujen lataaminen

Vedä työnkulun JSON-tiedosto kankaalle tai käytä valikon **Load**-toimintoa. Oletuksena näkemäsi Z-Image Turbo -työnkulku ladataan tallennetusta työnkulkutiedostosta.

### Työnkulkujen jakaminen

Työnkulut ovat itsenäisiä—jaa JSON-tiedosto kollegoiden kanssa, ja he voivat toistaa täsmälleen saman asetuksesi. Tämä tekee ComfyUI:sta erinomaisen yhteistyöhön perustuvaan kokeiluun.

## Seuraavat askeleet

- **Tutustu LoRA-solmuihin**: Käytä tyyli- tai aiheadaptereita ilman uudelleenkoulutusta
- **Lisää negatiivisia kehotteita**: Yhdistä toinen CLIP Text Encode -solmu KSamplerin **negative**-ehdoitussyötteeseen ohjataksesi mallia pois ei-toivotuista ominaisuuksista, kuten sumentumisesta, artefakteista tai vesileimasta
- **Rakenna mukautettuja työnkulkuja**: Ketjuta useita luonteja, lisää suurennus tai luo kuvavariaatioita
- **Selaa yhteisön työnkulkuja**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) sisältää monia käyttövalmiita työnkulkuja

ComfyUI:n vahvuus on kokeilu: yhdistä solmuja eri tavoin, säädä parametreja ja tarkkaile, miten jokainen muutos vaikuttaa tulokseen. Tämä käytännön tutkiminen rakentaa intuitiota siitä, miten diffuusiomallit toimivat.

Lisätietoja löydät [ComfyUI-dokumentaatiosta](https://docs.comfy.org/).