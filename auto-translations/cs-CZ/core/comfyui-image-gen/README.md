<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

ComfyUI je výkonné, uzlově orientované rozhraní pro Stable Diffusion a další difuzní modely. Na rozdíl od tradičních rozhraní text-to-image s jednoduchými poli pro zadání promptu ComfyUI zpřístupňuje celý pipeline generování obrázků jako vizuální graf, což vám dává jemnou kontrolu nad každým krokem od kódování textu přes manipulaci s latentním prostorem až po finální dekódování.

Tento tutoriál vás naučí, jak používat ComfyUI s modelem Z Image Turbo na vaší GPU pro generování vysoce kvalitních AI obrázků.

## Co se naučíte

- Jak spustit ComfyUI a načíst šablonu Z-Image Turbo
- Pochopení komponent difuzního pipeline
- Generování obrázků a ladění parametrů generování
- Ukládání a sdílení workflow

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace požadovaného softwaru

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udělte svému uživateli přístup k zařízením GPU** (aby se to projevilo, odhlaste se a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Vytvoření virtuálního prostředí
Na Linuxu otevřete terminál v adresáři dle vlastního výběru a spuštěním následujícího příkazu vytvořte venv:

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


## Spuštění ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Pro spuštění ComfyUI na Windows klikněte na spouštěč ComfyUI Desktop Launcher, který najdete na ploše. Postupujte podle kroků a nainstalujte lokální verzi s AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Poté klikněte na tlačítko ComfyUI v horní části aplikace uprostřed. Otevře se karta nastavení. Otevřete kartu Storage a ujistěte se, že jsou cesty nastaveny následovně, aby byl umožněn přístup k předinstalovaným modelům.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Na zařízení AMD Ryzen™ AI Halo běží ComfyUI v předpřipraveném kontejneru, který nevyžaduje žádné další nastavení Pythonu.

Pro spuštění ComfyUI na Linuxu klikněte na zkratku ComfyUI na hlavním panelu. Měla by se sama otevřít v okně prohlížeče.
>**Tip**: ComfyUI a jeho modely jsou uloženy v `~/.local/share/ComfyUI/models`. Zde můžete ručně přidávat workflow nebo nové modely.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Pro spuštění ComfyUI na Windows jednoduše klikněte na zkratku ComfyUI na ploše.
<!-- @os:end -->

<!-- @os:linux -->

Pro spuštění ComfyUI:

1. Ujistěte se, že se nacházíte v adresáři ComfyUI. 
2. Spusťte `python3 main.py --use-pytorch-cross-attention`

ComfyUI spustí lokální webový server. Otevřete prohlížeč na adrese `http://127.0.0.1:8188` pro přístup k rozhraní.

> **Tip**: Ponechte okno terminálu otevřené během používání ComfyUI. Jeho zavřením se server zastaví.
<!-- @os:end -->
<!-- @device:end -->


## Vyhledání šablony Z-Image Turbo

Než začnete generovat obrázky, musíte načíst šablonu Z-Image Turbo. Postup je následující:

1. **Podívejte se na zcela levý okraj obrazovky** – na nejlevější straně aplikace probíhá svislý panel nástrojů odshora dolů.

2. **Najděte ikonu složky** – v tomto levém panelu nástrojů vyhledejte ikonu, která vypadá jako složka. Po najetí myší je označena „Templates“.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klikněte na ikonu složky** – tím se otevře panel Templates.

4. **Vyhledejte „Z-Image Turbo“** – použijte vyhledávací pole nebo procházejte dostupné šablony, dokud nenajdete workflow Z-Image Turbo Text To Image, poté na něj kliknutím proveďte jeho načtení.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Stahování modelů

<!-- @require:comfyui-models -->

## Pochopení rozhraní

Po načtení šablony Z-Image Turbo uvidíte plátno se 2 hlavními uzly. První uzel se jmenuje „Text to Image (Z-Image-Turbo)“ a druhý uzel slouží k zobrazení obrázku. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Na uzlu Z-Image klikněte na tlačítko vpravo nahoře, čímž uzel rozbalíte a zobrazíte podgraf.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Komponenty pipeline

Workflow Z-Image Turbo využívá čtyři klíčové komponenty modelu, které spolupracují:

| Komponenta | Role |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Převádí váš textový prompt na embeddingy, kterým difuzní model rozumí |
| **Diffusion Model** (Z-Image Turbo) | Základní neuronová síť, která iterativně odšumuje latentní reprezentace na obrázky |
| **VAE** (Variational Autoencoder) | Kóduje obrázky do/z latentního prostoru (dekóduje finální latenty na pixely) |
| **LoRA** (volitelné) | Lehké adaptéry, které upravují styl nebo předmět bez nutnosti přeučování základního modelu |

Každý uzel ve workflow odpovídá jedné z těchto komponent. Data proudí zleva doprava: text → embeddingy → řízené odšumování → latenty → finální obrázek.
## Generování prvního obrázku

Model Z-Image Turbo je již načten. Generování obrázku:

1. **Zadejte svůj prompt** do hlavního uzlu Z-Image Node. Buďte popisní. Zde je příklad:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Volitelné)**: Potvrďte nebo upravte další konkrétní nastavení uvnitř podgrafu.
3. **Klikněte na modré tlačítko „Run Workflow“** v pravém rohu (nebo stiskněte `Ctrl+Enter`)
4. Sledujte, jak se jednotlivé uzly zvýrazňují při provádění každého kroku

Provedení celého pracovního postupu by mělo trvat méně než 30 sekund. Vygenerovaný obrázek se zobrazí v uzlu **Save Image** a uloží se do složky `output/`.

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


## Úprava parametrů generování

### Nastavení KSampler

Uzel KSampler řídí základní proces difúze:

| Parametr | Co ovlivňuje | Doporučeno pro Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Počet iterací odšumování | 4–10 (turbo modely jsou destilovány pro nižší počet kroků) |
| **cfg** | Míra bezklasifikačního vedení (classifier-free guidance) – jak přesně se má dodržet prompt | 1,0–2,0 (turbo modely používají velmi nízké vedení) |
| **sampler_name** | Algoritmus odšumování | `euler` a `res_multistep` fungují dobře pro turbo modely |
| **scheduler** | Křivka šumového plánu | `normal` nebo `simple` |
| **seed** | Náhodné počáteční číslo pro reprodukovatelnost | Nastavte pevné hodnoty pro iterování nad kompozicí |

### Velikost obrázku

Pro úpravu výstupních rozměrů najděte uzel **Empty Latent Image** a upravte hodnoty **width** a **height**. Pro optimální kvalitu udržujte rozměry na 1024 pixelech nebo méně na delší straně.

### ModelSamplingAuraFlow

Uzel **ModelSamplingAuraFlow** je specializovaný modifikátor vzorkování, který upravuje způsob, jakým proces difúze zpracovává plánování šumu. Tento uzel uvidíte připojený k výstupu modelu v pracovním postupu Z-Image Turbo.

| Parametr | Co ovlivňuje | Doporučené hodnoty |
|-----------|------------------|-------------------|
| **shift** | Upravuje časování šumového plánu – vyšší hodnoty posouvají více zpřesnění detailů do pozdějších kroků | 1,0–4,0 (výchozí hodnota je 3,0) |

Kdy upravit **shift**:

- **Nižší hodnoty (1,0–2,0)**: Rychlejší konvergence, vhodné pro jednoduché kompozice
- **Vyšší hodnoty (3,0–4,0)**: Postupnější zpřesňování, může zlepšit jemné detaily ve složitých scénách

Metoda vzorkování AuraFlow je navržena speciálně pro modely s párováním toku (flow-matching), jako je Z-Image Turbo, a zajišťuje správné rozložení šumu v průběhu celého procesu generování.

## Práce s pracovními postupy

### Ukládání pracovních postupů

Kliknutím na tlačítko **Save** v nabídce exportujete svůj pracovní postup jako soubor JSON. Ten obsahuje:

- Všechny uzly a jejich parametry
- Všechna propojení mezi uzly
- Aktuální text promptu

### Načítání pracovních postupů

Přetáhněte soubor JSON s pracovním postupem na plátno, nebo použijte možnost **Load** v nabídce. Pracovní postup Z-Image Turbo, který vidíte ve výchozím nastavení, je načten z uloženého souboru pracovního postupu.

### Sdílení pracovních postupů

Pracovní postupy jsou samostatné – stačí sdílet soubor JSON s kolegy a ti mohou přesně zopakovat vaše nastavení. Díky tomu je ComfyUI vynikající pro společné experimentování.

## Další kroky

- **Prozkoumejte uzly LoRA**: Aplikujte stylové nebo předmětové adaptéry bez nutnosti opětovného trénování
- **Přidejte negativní prompty**: Připojte druhý uzel CLIP Text Encode ke vstupu **negative** conditioning v KSampleru, abyste model nasměrovali pryč od nežádoucích prvků, jako je rozmazání, artefakty nebo vodoznaky
- **Vytvářejte vlastní pracovní postupy**: Řetězte více generování, přidejte zvětšování rozlišení nebo vytvářejte varianty obrázků
- **Procházejte komunitní pracovní postupy**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) obsahuje mnoho připravených pracovních postupů

Síla ComfyUI spočívá v experimentování: propojujte uzly různými způsoby, upravujte parametry a sledujte, jak každá změna ovlivňuje výstup. Tento praktický přístup buduje intuici pro fungování difúzních modelů.

Další informace naleznete v [dokumentaci ComfyUI](https://docs.comfy.org/).