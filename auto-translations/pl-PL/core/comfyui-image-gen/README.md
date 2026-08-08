<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

ComfyUI to zaawansowany, oparty na węzłach interfejs dla Stable Diffusion i innych modeli dyfuzyjnych. W przeciwieństwie do tradycyjnych interfejsów tekst-na-obraz z prostym polem promptu, ComfyUI udostępnia cały potok generowania obrazu jako wizualny graf, dając pełną kontrolę nad każdym etapem — od kodowania tekstu, przez manipulację przestrzenią latentną, aż po ostateczne dekodowanie.

Ten samouczek pokazuje, jak korzystać z ComfyUI z modelem Z Image Turbo na Twoim GPU, aby generować wysokiej jakości obrazy AI.

## Czego się nauczysz

- Jak uruchomić ComfyUI i wczytać szablon Z-Image Turbo
- Zrozumienie komponentów potoku dyfuzyjnego
- Generowanie obrazów i dostrajanie parametrów generacji
- Zapisywanie i udostępnianie przepływów pracy

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (aby to zadziałało, wyloguj się i zaloguj ponownie):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Tworzenie środowiska wirtualnego
W systemie Linux otwórz terminal w wybranym katalogu i uruchom poniższe polecenie, aby utworzyć venv:

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


## Uruchamianie ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Aby uruchomić ComfyUI w systemie Windows, kliknij Launcher ComfyUI Desktop znajdujący się na pulpicie. Postępuj zgodnie z krokami, aby zainstalować lokalną wersję z AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Następnie kliknij przycisk ComfyUI na środku u góry aplikacji. Otworzy się karta ustawień. Otwórz kartę Storage i upewnij się, że ścieżki są ustawione w następujący sposób, aby uzyskać dostęp do wstępnie zainstalowanych modeli.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Na AMD Ryzen™ AI Halo, ComfyUI działa w gotowym kontenerze, który nie wymaga dodatkowej konfiguracji Pythona.

Aby uruchomić ComfyUI w systemie Linux, kliknij skrót ComfyUI na pasku zadań. Powinien otworzyć się samodzielnie w oknie przeglądarki.
>**Wskazówka**: ComfyUI i jego modele są przechowywane w `~/.local/share/ComfyUI/models`. To tutaj możesz ręcznie dodawać przepływy pracy lub nowe modele.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Aby uruchomić ComfyUI w systemie Windows, po prostu kliknij skrót ComfyUI na pulpicie.
<!-- @os:end -->

<!-- @os:linux -->

Aby uruchomić ComfyUI:

1. Upewnij się, że znajdujesz się w katalogu ComfyUI. 
2. Uruchom `python3 main.py --use-pytorch-cross-attention`

ComfyUI uruchamia lokalny serwer WWW. Otwórz przeglądarkę pod adresem `http://127.0.0.1:8188`, aby uzyskać dostęp do interfejsu.

> **Wskazówka**: Podczas korzystania z ComfyUI pozostaw okno terminala otwarte. Zamknięcie go zatrzyma serwer.
<!-- @os:end -->
<!-- @device:end -->


## Znajdowanie szablonu Z-Image Turbo

Przed wygenerowaniem obrazów musisz wczytać szablon Z-Image Turbo. Oto jak go znaleźć:

1. **Spójrz na lewy skraj ekranu** — po lewej stronie aplikacji, od góry do dołu, biegnie pionowy pasek narzędzi.

2. **Znajdź ikonę folderu** — w tym lewym pasku narzędzi poszukaj ikony przypominającej folder. Po najechaniu na nią kursorem zobaczysz etykietę „Templates”.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Kliknij ikonę folderu** — otworzy się panel Templates.

4. **Wyszukaj „Z-Image Turbo”** — użyj paska wyszukiwania lub przewiń dostępne szablony, aby znaleźć przepływ pracy Z-Image Turbo Text To Image, a następnie kliknij, aby go wczytać.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Pobieranie modeli

<!-- @require:comfyui-models -->

## Zrozumienie interfejsu

Po wczytaniu szablonu Z-Image Turbo zobaczysz płótno z dwoma głównymi węzłami. Pierwszy węzeł nazywa się „Text to Image (Z-Image-Turbo)”, a drugi służy do podglądu obrazu. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


W węźle Z-Image kliknij przycisk w prawym górnym rogu, aby rozwinąć węzeł i zobaczyć podgraf.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Komponenty potoku

Przepływ pracy Z-Image Turbo wykorzystuje cztery kluczowe komponenty modelu, które współpracują ze sobą:

| Komponent | Rola |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Konwertuje Twój prompt tekstowy na osadzenia (embeddings) zrozumiałe dla modelu dyfuzyjnego |
| **Diffusion Model** (Z-Image Turbo) | Główna sieć neuronowa, która iteracyjnie usuwa szum z reprezentacji latentnych, przekształcając je w obrazy |
| **VAE** (Variational Autoencoder) | Koduje obrazy do/z przestrzeni latentnej (dekoduje ostateczne latenty na piksele) |
| **LoRA** (opcjonalnie) | Lekkie adaptery modyfikujące styl lub temat bez konieczności ponownego trenowania modelu bazowego |

Każdy węzeł w przepływie pracy odpowiada jednemu z tych komponentów. Dane przepływają od lewej do prawej: tekst → osadzenia → sterowane usuwanie szumu → latenty → końcowy obraz.
## Generowanie pierwszego obrazu

Model Z-Image Turbo jest już wczytany. Aby wygenerować obraz:

1. **Wpisz swój prompt** w głównym węźle Z-Image Node. Bądź opisowy. Oto przykład:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opcjonalnie)**: Potwierdź lub dostosuj inne konkretne ustawienia w podgrafie.
3. **Kliknij niebieski przycisk „Run Workflow”** w prawym rogu (lub naciśnij `Ctrl+Enter`)
4. Obserwuj, jak podświetlają się węzły w miarę wykonywania kolejnych kroków

Wykonanie całego przepływu pracy powinno zająć mniej niż 30 sekund. Wygenerowany obraz pojawi się w węźle **Save Image** i zostanie zapisany w folderze `output/`.

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


## Dostosowywanie parametrów generowania

### Ustawienia KSampler

Węzeł KSampler kontroluje podstawowy proces dyfuzji:

| Parametr | Co kontroluje | Zalecane dla Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Liczba iteracji odszumiania | 4–10 (modele turbo są destylowane pod kątem mniejszej liczby kroków) |
| **cfg** | Skala klasyfikator-free guidance—jak ściśle podążać za promptem | 1.0–2.0 (modele turbo używają bardzo niskiego guidance) |
| **sampler_name** | Algorytm odszumiania | `euler` i `res_multistep` działają dobrze w przypadku modeli turbo |
| **scheduler** | Krzywa harmonogramu szumu | `normal` lub `simple` |
| **seed** | Ziarno losowości dla powtarzalności | Ustaw stałe wartości, aby iterować nad kompozycją |

### Rozmiar obrazu

Aby dostosować wymiary wyjściowe, znajdź węzeł **Empty Latent Image** i zmodyfikuj **width** oraz **height**. Utrzymuj wymiary na poziomie 1024 pikseli lub mniej na dłuższym boku, aby uzyskać optymalną jakość.

### ModelSamplingAuraFlow

Węzeł **ModelSamplingAuraFlow** to specjalistyczny modyfikator próbkowania, który dostosowuje sposób, w jaki proces dyfuzji obsługuje harmonogramowanie szumu. Zobaczysz ten węzeł połączony z wyjściem modelu w przepływie pracy Z-Image Turbo.

| Parametr | Co kontroluje | Zalecane wartości |
|-----------|------------------|-------------------|
| **shift** | Dostosowuje harmonogram czasowy szumu—wyższe wartości przesuwają więcej dopracowywania szczegółów na późniejsze kroki | 1.0–4.0 (wartość domyślna to 3.0) |

Kiedy dostosować **shift**:

- **Niższe wartości (1.0–2.0)**: Szybsza zbieżność, dobra dla prostych kompozycji
- **Wyższe wartości (3.0–4.0)**: Bardziej stopniowe dopracowywanie, może poprawić drobne szczegóły w złożonych scenach

Metoda próbkowania AuraFlow jest specjalnie zaprojektowana dla modeli opartych na dopasowaniu przepływu (flow-matching), takich jak Z-Image Turbo, zapewniając prawidłowy rozkład szumu w całym procesie generowania.

## Praca z przepływami pracy

### Zapisywanie przepływów pracy

Kliknij przycisk **Save** w menu, aby wyeksportować przepływ pracy jako plik JSON. Zawiera on:

- Wszystkie węzły i ich parametry
- Wszystkie połączenia między węzłami
- Aktualny tekst promptu

### Wczytywanie przepływów pracy

Przeciągnij plik JSON z przepływem pracy na obszar roboczy lub użyj opcji **Load** z menu. Domyślnie wyświetlany przepływ pracy Z-Image Turbo jest wczytywany z zapisanego pliku przepływu pracy.

### Udostępnianie przepływów pracy

Przepływy pracy są samodzielne—udostępnij plik JSON współpracownikom, a będą mogli odtworzyć dokładnie taką samą konfigurację. Dzięki temu ComfyUI doskonale nadaje się do wspólnych eksperymentów.

## Następne kroki

- **Poznaj węzły LoRA**: Stosuj adaptery stylu lub tematu bez ponownego trenowania
- **Dodaj negatywne prompty**: Podłącz drugi węzeł CLIP Text Encode do wejścia kondycjonowania **negative** w KSampler, aby ukierunkować model z dala od niepożądanych elementów, takich jak rozmycie, artefakty czy znaki wodne
- **Twórz niestandardowe przepływy pracy**: Łącz wiele generacji, dodawaj upscaling lub twórz warianty obrazu
- **Przeglądaj przepływy pracy społeczności**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) zawiera wiele gotowych do użycia przepływów pracy

Siłą ComfyUI jest eksperymentowanie: łącz węzły w różny sposób, dostosowuj parametry i obserwuj, jak każda zmiana wpływa na wynik. Ta praktyczna eksploracja buduje intuicję dotyczącą działania modeli dyfuzyjnych.

Aby uzyskać więcej informacji, zapoznaj się z [dokumentacją ComfyUI](https://docs.comfy.org/).