<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

ComfyUI je výkonné rozhranie založené na uzloch pre Stable Diffusion a ďalšie difúzne modely. Na rozdiel od tradičných rozhraní na generovanie obrázkov z textu s jednoduchými poliami na zadávanie promptov, ComfyUI zobrazuje celý pipeline generovania obrázkov ako vizuálny graf, čo vám dáva podrobnú kontrolu nad každým krokom – od kódovania textu cez manipuláciu s latentným priestorom až po finálne dekódovanie.

Tento návod vás naučí, ako používať ComfyUI s modelom Z Image Turbo na vašom GPU na generovanie kvalitných obrázkov pomocou AI.

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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (aby sa táto zmena prejavila, odhláste sa a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Vytvorenie virtuálneho prostredia
V systéme Linux otvorte terminál v priečinku podľa vlastného výberu a spustite nasledujúci príkaz na vytvorenie venv:

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
Ak chcete spustiť ComfyUI v systéme Windows, kliknite na ComfyUI Desktop Launcher, ktorý nájdete na pracovnej ploche. Postupujte podľa krokov na inštaláciu lokálnej verzie s AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Potom kliknite na tlačidlo ComfyUI v hornej strednej časti aplikácie. Otvorí sa tým karta nastavení. Otvorte kartu Storage a uistite sa, že cesty sú nastavené nasledovne, aby ste mali prístup k predinštalovaným modelom.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Na AMD Ryzen™ AI Halo beží ComfyUI v preddefinovanom kontajneri, ktorý nevyžaduje žiadne ďalšie nastavenie Pythonu.

Ak chcete spustiť ComfyUI v systéme Linux, kliknite na skratku ComfyUI na paneli úloh. Malo by sa samo otvoriť v okne prehliadača.
>**Tip**: ComfyUI a jeho modely sú uložené v priečinku `~/.local/share/ComfyUI/models`. Sem môžete manuálne pridávať pracovné postupy alebo nové modely.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Ak chcete spustiť ComfyUI v systéme Windows, jednoducho kliknite na skratku ComfyUI na pracovnej ploche.
<!-- @os:end -->

<!-- @os:linux -->

Ak chcete spustiť ComfyUI:

1. Uistite sa, že sa nachádzate v priečinku ComfyUI. 
2. Spustite `python3 main.py --use-pytorch-cross-attention`

ComfyUI spustí lokálny webový server. Otvorte prehliadač na adrese `http://127.0.0.1:8188`, aby ste získali prístup k rozhraniu.

> **Tip**: Počas používania ComfyUI nechajte okno terminálu otvorené. Jeho zatvorenie zastaví server.
<!-- @os:end -->
<!-- @device:end -->


## Vyhľadanie šablóny Z-Image Turbo

Pred generovaním obrázkov musíte načítať šablónu Z-Image Turbo. Postup, ako ju nájsť:

1. **Pozrite sa na úplný ľavý okraj obrazovky** — na najľavejšej strane aplikácie sa nachádza zvislý panel s nástrojmi, ktorý beží zhora nadol.

2. **Nájdite ikonu priečinka** — na tomto ľavom paneli s nástrojmi vyhľadajte ikonu, ktorá vyzerá ako priečinok. Po prejdení kurzorom nad ňou sa zobrazí popisok „Templates“.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Kliknite na ikonu priečinka** — otvorí sa tým panel Templates.

4. **Vyhľadajte „Z-Image Turbo“** — použite vyhľadávacie pole alebo prechádzajte dostupnými šablónami, kým nenájdete pracovný postup Z-Image Turbo Text To Image, a kliknutím ho načítajte.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Sťahovanie modelov

<!-- @require:comfyui-models -->

## Pochopenie rozhrania

Keď sa načíta šablóna Z-Image Turbo, uvidíte plátno s 2 hlavnými uzlami. Prvý uzol sa nazýva „Text to Image (Z-Image-Turbo)“ a druhý uzol slúži na zobrazenie obrázka. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Na uzle Z-Image kliknite na tlačidlo vpravo hore, čím uzol rozbalíte a zobrazíte podgraf.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Komponenty pipeline

Pracovný postup Z-Image Turbo používa štyri kľúčové komponenty modelu, ktoré spolupracujú:

| Komponent | Úloha |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Prevádza váš textový vstup (prompt) na vnorenia (embeddings), ktorým rozumie difúzny model |
| **Diffusion Model** (Z-Image Turbo) | Hlavná neurónová sieť, ktorá iteratívne odstraňuje šum z latentných reprezentácií a vytvára z nich obrázky |
| **VAE** (Variational Autoencoder) | Kóduje obrázky do/z latentného priestoru (dekóduje výsledné latentné vektory na pixely) |
| **LoRA** (voliteľné) | Ľahké adaptéry, ktoré upravujú štýl alebo tému bez nutnosti pretrénovania základného modelu |

Každý uzol v pracovnom postupe zodpovedá jednému z týchto komponentov. Dáta prúdia zľava doprava: text → vnorenia → riadené odstraňovanie šumu → latentné vektory → výsledný obrázok.
## Generovanie prvého obrázka

Model Z-Image Turbo je už načítaný. Ak chcete vygenerovať obrázok:

1. **Zadajte svoj prompt** do hlavného uzla Z-Image Node. Buďte popisní. Tu je príklad:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Voliteľné)**: Potvrďte alebo upravte akékoľvek ďalšie špecifické nastavenia v rámci podgrafu.
3. **Kliknite na modré tlačidlo „Run Workflow"** v pravom rohu (alebo stlačte `Ctrl+Enter`)
4. Sledujte, ako sa uzly zvýrazňujú počas vykonávania jednotlivých krokov

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

Uzol KSampler riadi jadro procesu difúzie:

| Parameter | Čo riadi | Odporúčané pre Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Počet iterácií odšumovania | 4 – 10 (turbo modely sú destilované pre menší počet krokov) |
| **cfg** | Škála bezklasifikátorového vedenia (classifier-free guidance) – ako presne sa má dodržiavať prompt | 1,0 – 2,0 (turbo modely používajú veľmi nízke vedenie) |
| **sampler_name** | Algoritmus odšumovania | `euler` a `res_multistep` fungujú dobre pre turbo modely |
| **scheduler** | Krivka rozvrhu šumu | `normal` alebo `simple` |
| **seed** | Náhodné zrno pre reprodukovateľnosť | Nastavte pevné hodnoty na iteráciu kompozície |

### Veľkosť obrázka

Ak chcete upraviť výstupné rozmery, nájdite uzol **Empty Latent Image** a upravte hodnoty **width** a **height**. Udržujte rozmery na úrovni 1024 pixelov alebo menej na najdlhšej strane pre optimálnu kvalitu.

### ModelSamplingAuraFlow

Uzol **ModelSamplingAuraFlow** je špecializovaný modifikátor vzorkovania, ktorý upravuje spôsob, akým proces difúzie spracúva rozvrhovanie šumu. Tento uzol uvidíte pripojený k výstupu modelu v pracovnom postupe Z-Image Turbo.

| Parameter | Čo riadi | Odporúčané hodnoty |
|-----------|------------------|-------------------|
| **shift** | Upravuje časovanie rozvrhu šumu – vyššie hodnoty presúvajú viac zdokonaľovania detailov do neskorších krokov | 1,0 – 4,0 (predvolená hodnota je 3,0) |

Kedy upraviť **shift**:

- **Nižšie hodnoty (1,0 – 2,0)**: Rýchlejšia konvergencia, vhodné pre jednoduché kompozície
- **Vyššie hodnoty (3,0 – 4,0)**: Postupnejšie zdokonaľovanie, môže zlepšiť jemné detaily v zložitých scénach

Metóda vzorkovania AuraFlow je špeciálne navrhnutá pre modely s párovaním toku (flow-matching), ako je Z-Image Turbo, čím zaisťuje správne rozloženie šumu počas celého procesu generovania.

## Práca s pracovnými postupmi

### Ukladanie pracovných postupov

Kliknutím na tlačidlo **Save** v menu exportujete svoj pracovný postup ako súbor JSON. Tento súbor zachytáva:

- Všetky uzly a ich parametre
- Všetky prepojenia medzi uzlami
- Aktuálny text promptu

### Načítanie pracovných postupov

Presuňte súbor JSON s pracovným postupom na plátno alebo použite možnosť **Load** v menu. Predvolene zobrazený pracovný postup Z-Image Turbo je načítaný z uloženého súboru pracovného postupu.

### Zdieľanie pracovných postupov

Pracovné postupy sú samostatné – zdieľajte súbor JSON s kolegami a oni dokážu presne zreprodukovať vaše nastavenie. Vďaka tomu je ComfyUI vynikajúci nástroj na spoluprácu a experimentovanie.

## Ďalšie kroky

- **Preskúmajte uzly LoRA**: Aplikujte štýlové alebo predmetové adaptéry bez opätovného trénovania
- **Pridajte negatívne prompty**: Pripojte druhý uzol CLIP Text Encode k vstupu **negative** podmieňovania uzla KSampler, aby ste model nasmerovali preč od nežiaducich vlastností, ako je rozmazanie, artefakty alebo vodoznaky
- **Vytvárajte vlastné pracovné postupy**: Zreťazte viacero generovaní, pridajte zväčšovanie rozlíšenia (upscaling) alebo vytvárajte variácie obrázkov
- **Prehliadajte pracovné postupy komunity**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) obsahuje množstvo pripravených pracovných postupov na okamžité použitie

Silnou stránkou ComfyUI je experimentovanie: pripájajte uzly rôznymi spôsobmi, upravujte parametre a sledujte, ako každá zmena ovplyvňuje výstup. Táto praktická skúsenosť buduje intuíciu pre pochopenie fungovania difúznych modelov.

Ďalšie informácie nájdete v [dokumentácii ComfyUI](https://docs.comfy.org/).