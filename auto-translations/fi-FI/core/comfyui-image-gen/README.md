<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

ComfyUI on tehokas, solmupohjainen käyttöliittymä Stable Diffusionille ja muille diffuusiomalleille. Toisin kuin perinteiset teksti-kuvaksi-käyttöliittymät yksinkertaisine kehotekenttineen, ComfyUI paljastaa koko kuvantuotannon putken visuaalisena graafina, mikä antaa sinulle tarkan hallinnan jokaisesta vaiheesta – tekstin koodauksesta latenttiavaruuden käsittelyyn ja lopulliseen dekoodaukseen.

Tämä opas opastaa, miten käytät ComfyUI:ta Z Image Turbo -mallin kanssa GPU:llasi korkealaatuisten tekoälykuvien tuottamiseen.

## Mitä opit

- Miten käynnistät ComfyUI:n ja lataat Z-Image Turbo -mallipohjan
- Diffuusioputken osien ymmärtäminen
- Kuvien tuottaminen ja generointiparametrien säätäminen
- Työnkulkujen tallentaminen ja jakaminen

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetusten määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Ohjelmistopäivitysten tarkistaminen

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

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
Avaa Linuxissa terminaali haluamaasi hakemistoon ja suorita seuraava komento venv-ympäristön luomiseksi:

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
Käynnistä ComfyUI Windowsissa napsauttamalla työpöydältäsi löytyvää ComfyUI Desktop -käynnistintä. Seuraa ohjeita AMD:n paikallisen version asentamiseksi.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Napsauta sitten sovelluksen yläkeskellä olevaa ComfyUI-painiketta. Tämä avaa asetusvälilehden. Avaa Tallennustila-välilehti ja varmista, että polut on asetettu seuraavasti, jotta pääset käsiksi esiasennettuihin malleihin.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
AMD Ryzen™ AI Halo -laitteilla ComfyUI toimii valmiiksi rakennetussa kontissa, joka ei vaadi lisää Python-asetuksia.

Käynnistä ComfyUI Linuxissa napsauttamalla ComfyUI-pikakuvaketta tehtäväpalkista. Sen pitäisi avautua itsestään selainikkunaan.
>**Vinkki**: ComfyUI ja sen mallit tallennetaan polkuun `~/.local/share/ComfyUI/models`. Sieltä voit lisätä työnkulkuja tai uusia malleja manuaalisesti.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Käynnistä ComfyUI Windowsissa napsauttamalla yksinkertaisesti työpöydälläsi olevaa ComfyUI-pikakuvaketta.
<!-- @os:end -->

<!-- @os:linux -->

Käynnistä ComfyUI seuraavasti:

1. Varmista, että olet ComfyUI-hakemistossa. 
2. Suorita `python3 main.py --use-pytorch-cross-attention`

ComfyUI käynnistää paikallisen verkkopalvelimen. Avaa selaimessasi osoite `http://127.0.0.1:8188` päästäksesi käyttöliittymään.

> **Vinkki**: Pidä terminaali-ikkuna auki käyttäessäsi ComfyUI:ta. Sen sulkeminen pysäyttää palvelimen.
<!-- @os:end -->
<!-- @device:end -->


## Z-Image Turbo -mallipohjan löytäminen

Ennen kuvien tuottamista sinun täytyy ladata Z-Image Turbo -mallipohja. Näin löydät sen:

1. **Katso näytön äärimmäistä vasenta reunaa** — sovelluksen vasemmassa laidassa kulkee pystysuuntainen työkalupalkki ylhäältä alas.

2. **Etsi kansiokuvake** — etsi vasemmasta työkalupalkista kuvake, joka näyttää kansiolta. Kun viet hiiren sen päälle, sen nimi on "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Napsauta kansiokuvaketta** — tämä avaa Templates-paneelin.

4. **Etsi "Z-Image Turbo"** — käytä hakupalkkia tai selaa saatavilla olevia mallipohjia löytääksesi Z-Image Turbo Text To Image -työnkulun ja napsauta sitä ladataksesi sen.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Mallien lataaminen

<!-- @require:comfyui-models -->

## Käyttöliittymän ymmärtäminen

Kun Z-Image Turbo -mallipohja latautuu, näet piirtoalueen, jossa on 2 pääsolmua. Ensimmäinen solmu on nimeltään 'Text to Image (Z-Image-Turbo)', ja toinen solmu on kuvan tarkastelua varten. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Napsauta Z-Image-solmun oikeasta yläkulmasta löytyvää painiketta laajentaaksesi solmun ja nähdäksesi alagraafin.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Putken osat

Z-Image Turbo -työnkulku käyttää neljää keskeistä mallikomponenttia, jotka toimivat yhdessä:

| Komponentti | Rooli |
|-----------|------|
| **Tekstinkoodain** (Qwen 3 4B) | Muuntaa tekstikehotteesi upotuksiksi (embeddings), joita diffuusiomalli ymmärtää |
| **Diffuusiomalli** (Z-Image Turbo) | Ydinneuroverkko, joka poistaa iteratiivisesti kohinaa latenttiesityksistä muodostaen kuvia |
| **VAE** (Variaatioautoenkooderi) | Koodaa kuvia latenttiavaruuteen ja takaisin (dekoodaa lopulliset latentit pikseleiksi) |
| **LoRA** (valinnainen) | Kevyitä sovittimia, jotka muokkaavat tyyliä tai aihetta ilman perusmallin uudelleenkoulutusta |

Jokainen työnkulun solmu vastaa yhtä näistä komponenteista. Data virtaa vasemmalta oikealle: teksti → upotukset → ohjattu kohinanpoisto → latentit → lopullinen kuva.

## Ensimmäisen kuvan tuottaminen

Z-Image Turbo -malli on jo ladattu. Tuottaaksesi kuvan:

1. **Kirjoita kehotteesi** pääasialliseen Z-Image-solmuun. Ole kuvaileva. Tässä esimerkki:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Valinnainen)**: Vahvista tai säädä muita erityisasetuksia alagraafissa.
3. **Napsauta sinistä "Run Workflow" -painiketta** oikeassa kulmassa (tai paina `Ctrl+Enter`)
4. Seuraa, kuinka solmut korostuvat kunkin vaiheen suorituksen aikana

Koko työnkulun suorituksen pitäisi valmistua alle 30 sekunnissa. Tuotettu kuvasi näkyy **Save Image** -solmussa ja tallennetaan `output/`-kansioon.

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
print("history status:", json.dumps(entry.get("status", {})))  # surfaces the ComfyUI node/execution error
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
print("history status:", json.dumps(entry.get("status", {})))  # surfaces the ComfyUI node/execution error
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


## Generointiparametrien säätäminen
### KSampler-asetukset

KSampler-solmu ohjaa diffuusioprosessin ydintä:

| Parametri | Mitä se ohjaa | Suositus Z-Image Turbolle |
|-----------|------------------|-------------------------------|
| **steps** | Kohinanpoistoiteraatioiden määrä | 4–10 (turbo-mallit on tislattu käyttämään vähemmän vaiheita) |
| **cfg** | Classifier-free guidance -asteikko – kuinka tarkasti kehotetta seurataan | 1,0–2,0 (turbo-mallit käyttävät hyvin matalaa ohjausta) |
| **sampler_name** | Kohinanpoistoalgoritmi | `euler` ja `res_multistep` toimivat hyvin turbo-malleille |
| **scheduler** | Kohinan aikataulukäyrä | `normal` tai `simple` |
| **seed** | Satunnaissiemen toistettavuutta varten | Aseta kiinteät arvot koostumuksen iterointia varten |

### Kuvan koko

Jos haluat säätää tulostuksen mittasuhteita, etsi **Empty Latent Image** -solmu ja muokkaa **width**- ja **height**-arvoja. Pidä mitat enintään 1024 pikselissä pisimmältä sivulta parhaan laadun saavuttamiseksi.

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow**-solmu on erikoistunut näytteistysmuunnin, joka säätää sitä, miten diffuusioprosessi käsittelee kohinan aikataulutusta. Näet tämän solmun liitettynä mallin ulostuloon Z-Image Turbo -työnkulussa.

| Parametri | Mitä se ohjaa | Suositellut arvot |
|-----------|------------------|-------------------|
| **shift** | Säätää kohinan aikataulun ajoitusta – korkeammat arvot siirtävät enemmän yksityiskohtien viimeistelyä myöhempiin vaiheisiin | 1,0–4,0 (oletusarvo on 3,0) |

Milloin **shift**-arvoa kannattaa säätää:

- **Matalammat arvot (1,0–2,0)**: Nopeampi konvergenssi, sopii yksinkertaisiin koostumuksiin
- **Korkeammat arvot (3,0–4,0)**: Asteittaisempi viimeistely, voi parantaa hienoja yksityiskohtia monimutkaisissa kohtauksissa

AuraFlow-näytteistysmenetelmä on suunniteltu erityisesti flow-matching-malleille, kuten Z-Image Turbolle, varmistaen kohinan asianmukaisen jakautumisen koko generointiprosessin ajan.

## Työnkulkujen käyttäminen

### Työnkulkujen tallentaminen

Napsauta valikon **Save**-painiketta viedäksesi työnkulkusi JSON-tiedostona. Tämä tallentaa:

- Kaikki solmut ja niiden parametrit
- Kaikki solmujen väliset yhteydet
- Nykyisen kehoteteksin

### Työnkulkujen lataaminen

Vedä työnkulun JSON-tiedosto canvasille, tai käytä valikon **Load**-toimintoa. Oletuksena näkyvä Z-Image Turbo -työnkulku on ladattu tallennetusta työnkulkutiedostosta.

### Työnkulkujen jakaminen

Työnkulut ovat itsenäisiä kokonaisuuksia – jaa JSON-tiedosto kollegoiden kanssa, niin he voivat toistaa täsmälleen saman asetuksesi. Tämä tekee ComfyUI:sta erinomaisen työkalun yhteistyössä tapahtuvaan kokeiluun.

## Seuraavat vaiheet

- **Tutustu LoRA-solmuihin**: Ota käyttöön tyyli- tai aihesovittimia ilman uudelleenkoulutusta
- **Lisää negatiivisia kehotteita**: Yhdistä toinen CLIP Text Encode -solmu KSamplerin **negative**-konditiointituloon ohjataksesi mallia pois ei-toivotuista piirteistä, kuten sumeudesta, artefakteista tai vesileimoista
- **Rakenna mukautettuja työnkulkuja**: Ketjuta useita generointeja, lisää suurentamista tai luo kuvavariaatioita
- **Selaa yhteisön työnkulkuja**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) -sivustolla on paljon käyttövalmiita työnkulkuja

ComfyUI:n vahvuus on kokeilu: yhdistä solmuja eri tavoin, säädä parametreja ja tarkkaile, miten jokainen muutos vaikuttaa lopputulokseen. Tämä käytännönläheinen tutkiminen kehittää intuitiota siitä, miten diffuusiomallit toimivat.

Lisätietoja saat [ComfyUI-dokumentaatiosta](https://docs.comfy.org/).