<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

ComfyUI je výkonné rozhranie pre Stable Diffusion a iné difúzne modely založené na uzloch. Na rozdiel od tradičných rozhraní text-na-obrázok s jednoduchými poľami pre výzvy, ComfyUI sprístupňuje celý pipeline generovania obrázkov ako vizuálny graf, čo vám dáva podrobnú kontrolu nad každým krokom od kódovania textu cez manipuláciu s latentným priestorom až po finálne dekódovanie.

Tento tutoriál vás naučí, ako používať ComfyUI s modelom Z Image Turbo na vašom GPU na generovanie vysokokvalitných obrázkov pomocou umelej inteligencie.

## Čo sa naučíte

- Ako spustiť ComfyUI a načítať šablónu Z-Image Turbo
- Pochopenie komponentov difúzneho pipeline
- Generovanie obrázkov a ladenie parametrov generovania
- Ukladanie a zdieľanie pracovných postupov

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie zmien sa odhláste a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Vytvorenie virtuálneho prostredia
Na Linuxe otvorte terminál v adresári podľa vášho výberu a spustite nasledujúci príkaz na vytvorenie venv:

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


## Spustenie ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Ak chcete spustiť ComfyUI v systéme Windows, kliknite na spúšťač ComfyUI Desktop, ktorý sa nachádza na vašej ploche. Postupujte podľa krokov na inštaláciu lokálnej verzie s AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Potom kliknite na tlačidlo ComfyUI v hornej strednej časti aplikácie. Otvorí sa karta nastavení. Otvorte kartu Úložisko a uistite sa, že cesty sú nastavené nasledovne pre prístup k vopred nainštalovaným modelom.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Ak chcete spustiť ComfyUI v systéme Linux, kliknite na skratku ComfyUI na paneli úloh. Malo by sa automaticky otvoriť v okne prehliadača.
>**Tip**: ComfyUI a jeho modely sú uložené v `~/.local/share/ComfyUI/models`. Tu môžete manuálne pridávať pracovné postupy alebo nové modely.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Ak chcete spustiť ComfyUI v systéme Windows, jednoducho kliknite na skratku ComfyUI na vašej ploche.
<!-- @os:end -->

<!-- @os:linux -->

Spustenie ComfyUI:

1. Uistite sa, že sa nachádzate v adresári ComfyUI. 
2. Spustite `python3 main.py --use-pytorch-cross-attention`

ComfyUI spustí lokálny webový server. Otvorte prehliadač na adrese `http://127.0.0.1:8188` pre prístup k rozhraniu.

> **Tip**: Počas používania ComfyUI nechajte okno terminálu otvorené. Jeho zatvorením sa server zastaví.
<!-- @os:end -->
<!-- @device:end -->


## Vyhľadanie šablóny Z-Image Turbo

Pred generovaním obrázkov musíte načítať šablónu Z-Image Turbo. Tu je postup, ako ju nájsť:

1. **Pozrite sa na úplne ľavý okraj obrazovky** — na úplne ľavej strane aplikácie sa nachádza zvislý panel nástrojov prechádzajúci zhora nadol.

2. **Nájdite ikonu priečinka** — na tomto ľavom paneli nástrojov vyhľadajte ikonu, ktorá vyzerá ako priečinok. Po umiestnení kurzora myši na ňu sa zobrazí popis „Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Kliknite na ikonu priečinka** — otvorí sa panel Šablóny.

4. **Vyhľadajte „Z-Image Turbo"** — použite vyhľadávací panel alebo prechádzajte dostupnými šablónami, nájdite pracovný postup Z-Image Turbo Text To Image a kliknite na neho pre načítanie.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Sťahovanie modelov

<!-- @require:comfyui-models -->

## Pochopenie rozhrania

Po načítaní šablóny Z-Image Turbo uvidíte plátno s 2 hlavnými uzlami. Prvý uzol sa nazýva „Text to Image (Z-Image-Turbo)" a druhý uzol slúži na zobrazenie obrázka. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Na uzle Z-Image kliknite na tlačidlo v pravom hornom rohu pre rozbalenie uzla a zobrazenie podgrafu.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Komponenty pipeline

Pracovný postup Z-Image Turbo využíva štyri kľúčové modelové komponenty, ktoré spolupracujú:

| Komponent | Úloha |
|-----------|------|
| **Textový enkodér** (Qwen 3 4B) | Konvertuje váš textový prompt na vektory, ktorým difúzny model rozumie |
| **Difúzny model** (Z-Image Turbo) | Základná neurónová sieť, ktorá iteratívne odstraňuje šum z latentných reprezentácií a vytvára obrázky |
| **VAE** (Variačný autoenkodér) | Kóduje obrázky do/z latentného priestoru (dekóduje finálne latenty na pixely) |
| **LoRA** (voliteľné) | Ľahké adaptéry, ktoré upravujú štýl alebo predmet bez opätovného trénovania základného modelu |

Každý uzol v pracovnom postupe zodpovedá jednému z týchto komponentov. Dáta prúdia zľava doprava: text → vektory → riadené odstraňovanie šumu → latenty → finálny obrázok.

## Generovanie prvého obrázka

Model Z-Image Turbo je už načítaný. Postup generovania obrázka:

1. **Zadajte svoj prompt** v hlavnom uzle Z-Image. Buďte opisní. Tu je príklad:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Voliteľné)**: Potvrďte alebo upravte ďalšie konkrétne nastavenia v rámci podgrafu.
3. **Kliknite na modré tlačidlo „Run Workflow"** v pravom rohu (alebo stlačte `Ctrl+Enter`)
4. Sledujte, ako sa uzly zvýrazňujú pri vykonávaní každého kroku

Celé vykonanie pracovného postupu by malo trvať menej ako 30 sekúnd. Vygenerovaný obrázok sa zobrazí v uzle **Save Image** a uloží sa do priečinka `output/`.

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


## Úprava parametrov generovania

### Nastavenia KSampler

Uzol KSampler riadi základný difúzny proces:

| Parameter | Čo riadi | Odporúčané pre Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Počet iterácií odstraňovania šumu | 4–10 (turbo modely sú destilované pre menší počet krokov) |
| **cfg** | Škála voľného navádzania klasifikátorom — ako presne sledovať prompt | 1,0–2,0 (turbo modely používajú veľmi nízke navádzanie) |
| **sampler_name** | Algoritmus odstraňovania šumu | `euler` a `res_multistep` fungujú dobre pre turbo modely |
| **scheduler** | Krivka rozvrhu šumu | `normal` alebo `simple` |
| **seed** | Náhodné semeno pre reprodukovateľnosť | Nastavte pevné hodnoty pre iteráciu na kompozícii |

### Veľkosť obrázka

Ak chcete upraviť výstupné rozmery, nájdite uzol **Empty Latent Image** a upravte **width** a **height**. Pre optimálnu kvalitu udržujte rozmery na úrovni 1024 pixelov alebo menej na dlhšej strane.

### ModelSamplingAuraFlow

Uzol **ModelSamplingAuraFlow** je špecializovaný modifikátor vzorkovania, ktorý upravuje spôsob, akým difúzny proces spracováva rozvrh šumu. Tento uzol uvidíte prepojený s výstupom modelu v pracovnom postupe Z-Image Turbo.

| Parameter | Čo riadi | Odporúčané hodnoty |
|-----------|------------------|-------------------|
| **shift** | Upravuje časovanie rozvrhu šumu — vyššie hodnoty posúvajú viac dolaďovania detailov do neskorších krokov | 1,0–4,0 (predvolená hodnota je 3,0) |

Kedy upraviť **shift**:

- **Nižšie hodnoty (1,0–2,0)**: Rýchlejšia konvergencia, vhodné pre jednoduché kompozície
- **Vyššie hodnoty (3,0–4,0)**: Postupnejšie dolaďovanie, môže zlepšiť jemné detaily v zložitých scénach

Metóda vzorkovania AuraFlow je špeciálne navrhnutá pre modely s prúdovým párovaním, ako je Z-Image Turbo, čím zabezpečuje správne rozloženie šumu počas celého procesu generovania.

## Práca s pracovnými postupmi

### Ukladanie pracovných postupov

Kliknite na tlačidlo **Save** v ponuke pre export pracovného postupu ako súboru JSON. Toto zachytí:

- Všetky uzly a ich parametre
- Všetky prepojenia medzi uzlami
- Aktuálny text promptu

### Načítanie pracovných postupov

Presuňte súbor JSON pracovného postupu na plátno alebo použite **Load** z ponuky. Pracovný postup Z-Image Turbo, ktorý vidíte predvolene, je načítaný zo uloženého súboru pracovného postupu.

### Zdieľanie pracovných postupov

Pracovné postupy sú samostatné — zdieľajte súbor JSON s kolegami a oni môžu reprodukovať vaše presné nastavenie. Vďaka tomu je ComfyUI výborný nástroj pre spoločné experimentovanie.

## Ďalšie kroky

- **Preskúmajte uzly LoRA**: Aplikujte adaptéry štýlu alebo predmetu bez opätovného trénovania
- **Pridajte negatívne prompty**: Prepojte druhý uzol CLIP Text Encode so vstupom **negative** podmienenia uzla KSampler, aby ste model nasmerovali od nežiaducich prvkov, ako sú rozmazanie, artefakty alebo vodoznaky
- **Vytvárajte vlastné pracovné postupy**: Reťazte viacero generovaní, pridajte zväčšovanie rozlíšenia alebo vytvárajte variácie obrázkov
- **Prehliadajte pracovné postupy komunity**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) obsahuje mnoho pracovných postupov pripravených na použitie

Silnou stránkou ComfyUI je experimentovanie: prepájajte uzly rôznymi spôsobmi, upravujte parametre a sledujte, ako každá zmena ovplyvňuje výstup. Toto praktické skúmanie buduje intuíciu pre to, ako difúzne modely fungujú.

Pre viac informácií si pozrite [dokumentáciu ComfyUI](https://docs.comfy.org/).