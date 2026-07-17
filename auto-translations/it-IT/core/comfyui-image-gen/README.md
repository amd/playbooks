<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

ComfyUI è un'interfaccia potente basata su nodi per Stable Diffusion e altri modelli di diffusione. A differenza delle tradizionali interfacce text-to-image con semplici caselle di prompt, ComfyUI espone l'intero pipeline di generazione delle immagini come un grafo visivo, offrendoti un controllo dettagliato su ogni fase, dalla codifica del testo alla manipolazione dello spazio latente fino alla decodifica finale.

Questo tutorial ti insegna come utilizzare ComfyUI con il modello Z Image Turbo sulla tua GPU per generare immagini AI di alta qualità.

## Cosa Imparerai

- Come avviare ComfyUI e caricare il template Z-Image Turbo
- Comprensione dei componenti del pipeline di diffusione
- Generazione di immagini e ottimizzazione dei parametri di generazione
- Salvataggio e condivisione dei workflow

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esci e rientra affinché le modifiche abbiano effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Crea un Ambiente Virtuale
Su Linux, apri un terminale nella directory di tua scelta ed esegui il seguente comando per creare un venv:

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


## Avvio di ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Per avviare ComfyUI su Windows, fai clic sul launcher ComfyUI Desktop che si trova sul Desktop. Segui i passaggi per installare la versione locale con AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Quindi, fai clic sul pulsante ComfyUI nella parte superiore centrale dell'app. Si aprirà una scheda delle impostazioni. Apri la scheda Storage e assicurati che i percorsi siano impostati come segue per accedere ai modelli preinstallati.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Per avviare ComfyUI su Linux, fai clic sul collegamento ComfyUI nella barra delle applicazioni. Dovrebbe aprirsi automaticamente in una finestra del browser.
>**Suggerimento**: ComfyUI e i suoi modelli sono archiviati in `~/.local/share/ComfyUI/models`. Qui puoi aggiungere manualmente workflow o nuovi modelli.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Per avviare ComfyUI su Windows, fai semplicemente clic sul collegamento ComfyUI sul Desktop.
<!-- @os:end -->

<!-- @os:linux -->

Per avviare ComfyUI:

1. Assicurati di trovarti nella directory di ComfyUI. 
2. Esegui `python3 main.py --use-pytorch-cross-attention`

ComfyUI avvia un server web locale. Apri il browser all'indirizzo `http://127.0.0.1:8188` per accedere all'interfaccia.

> **Suggerimento**: Tieni aperta la finestra del terminale mentre usi ComfyUI. Chiuderla interromperà il server.
<!-- @os:end -->
<!-- @device:end -->


## Trovare il Template Z-Image Turbo

Prima di generare immagini, devi caricare il template Z-Image Turbo. Ecco come trovarlo:

1. **Guarda il bordo sinistro dello schermo**—c'è una barra degli strumenti verticale che va dall'alto verso il basso sul lato più a sinistra dell'app.

2. **Trova l'icona della cartella**—in quella barra degli strumenti sinistra, cerca un'icona che assomiglia a una cartella. Quando ci passi sopra con il mouse, è etichettata "Templates."

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Fai clic sull'icona della cartella**—si apre il pannello Templates.

4. **Cerca "Z-Image Turbo"**—usa la barra di ricerca o scorri tra i template disponibili per trovare il workflow Z-Image Turbo Text To Image, quindi fai clic per caricarlo.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Download dei Modelli

<!-- @require:comfyui-models -->

## Comprensione dell'Interfaccia

Quando il template Z-Image Turbo viene caricato, vedrai un canvas con 2 nodi principali. Il primo nodo si chiama 'Text to Image (Z-Image-Turbo)', e il secondo nodo serve per visualizzare l'immagine. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Sul nodo Z-Image, fai clic sul pulsante in alto a destra per espandere il nodo e visualizzare il sottografo.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Componenti del Pipeline

Il workflow Z-Image Turbo utilizza quattro componenti chiave del modello che lavorano insieme:

| Componente | Ruolo |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Converte il tuo prompt testuale in embedding comprensibili dal modello di diffusione |
| **Diffusion Model** (Z-Image Turbo) | La rete neurale principale che denoisa iterativamente le rappresentazioni latenti in immagini |
| **VAE** (Variational Autoencoder) | Codifica le immagini da/verso lo spazio latente (decodifica i latenti finali in pixel) |
| **LoRA** (opzionale) | Adattatori leggeri che modificano lo stile o il soggetto senza riaddestrare il modello base |

Ogni nodo nel workflow corrisponde a uno di questi componenti. I dati fluiscono da sinistra a destra: testo → embedding → denoising guidato → latenti → immagine finale.

## Generare la Tua Prima Immagine

Il modello Z-Image Turbo è già caricato. Per generare un'immagine:

1. **Inserisci il tuo prompt** nel nodo Z-Image principale. Sii descrittivo. Ecco un esempio:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Opzionale)**: Conferma o modifica eventuali altre impostazioni specifiche all'interno del sottografo.
3. **Fai clic sul blu "Run Workflow"** nell'angolo destro (o premi `Ctrl+Enter`)
4. Osserva i nodi evidenziarsi man mano che ogni passaggio viene eseguito

L'intera esecuzione del workflow dovrebbe completarsi in meno di 30 secondi. L'immagine generata appare nel nodo **Save Image** e viene salvata nella cartella `output/`.

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


## Regolazione dei Parametri di Generazione

### Impostazioni di KSampler

Il nodo KSampler controlla il processo di diffusione principale:

| Parametro | Cosa Controlla | Consigliato per Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Numero di iterazioni di denoising | 4–10 (i modelli turbo sono distillati per un numero inferiore di passaggi) |
| **cfg** | Scala di guidance classifier-free—quanto seguire fedelmente il prompt | 1.0–2.0 (i modelli turbo usano una guidance molto bassa) |
| **sampler_name** | Algoritmo di denoising | `euler` e `res_multistep` funzionano bene per i modelli turbo |
| **scheduler** | Curva del programma di rumore | `normal` o `simple` |
| **seed** | Seed casuale per la riproducibilità | Imposta valori fissi per iterare su una composizione |

### Dimensione dell'Immagine

Per regolare le dimensioni dell'output, trova il nodo **Empty Latent Image** e modifica **width** e **height**. Mantieni le dimensioni pari o inferiori a 1024 pixel sul lato più lungo per una qualità ottimale.

### ModelSamplingAuraFlow

Il nodo **ModelSamplingAuraFlow** è un modificatore di campionamento specializzato che regola il modo in cui il processo di diffusione gestisce la pianificazione del rumore. Vedrai questo nodo collegato all'output del modello nel workflow Z-Image Turbo.

| Parametro | Cosa Controlla | Valori Consigliati |
|-----------|------------------|-------------------|
| **shift** | Regola la tempistica del programma di rumore—valori più alti spostano il raffinamento dei dettagli verso i passaggi successivi | 1.0–4.0 (il valore predefinito è 3.0) |

Quando regolare **shift**:

- **Valori bassi (1.0–2.0)**: Convergenza più rapida, adatta per composizioni semplici
- **Valori alti (3.0–4.0)**: Raffinamento più graduale, può migliorare i dettagli fini in scene complesse

Il metodo di campionamento AuraFlow è specificamente progettato per modelli flow-matching come Z-Image Turbo, garantendo una distribuzione corretta del rumore durante l'intero processo di generazione.

## Lavorare con i Workflow

### Salvataggio dei Workflow

Fai clic sul pulsante **Save** nel menu per esportare il tuo workflow come file JSON. Questo acquisisce:

- Tutti i nodi e i loro parametri
- Tutte le connessioni tra i nodi
- Il testo del prompt corrente

### Caricamento dei Workflow

Trascina un file JSON del workflow sul canvas, oppure usa **Load** dal menu. Il workflow Z-Image Turbo che vedi per impostazione predefinita viene caricato da un file di workflow salvato.

### Condivisione dei Workflow

I workflow sono autonomi—condividi il file JSON con i colleghi e potranno riprodurre esattamente la tua configurazione. Questo rende ComfyUI eccellente per la sperimentazione collaborativa.

## Prossimi Passi

- **Esplora i nodi LoRA**: Applica adattatori di stile o soggetto senza riaddestrare
- **Aggiungi prompt negativi**: Collega un secondo nodo CLIP Text Encode all'input di condizionamento **negative** di KSampler per guidare il modello lontano da caratteristiche indesiderate come sfocatura, artefatti o filigrane
- **Crea workflow personalizzati**: Concatena più generazioni, aggiungi upscaling o crea variazioni di immagini
- **Sfoglia i workflow della community**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) contiene molti workflow pronti all'uso

Il punto di forza di ComfyUI è la sperimentazione: collega i nodi in modo diverso, regola i parametri e osserva come ogni modifica influisce sull'output. Questa esplorazione pratica sviluppa l'intuizione su come funzionano i modelli di diffusione.

Per ulteriori informazioni, consulta la [Documentazione di ComfyUI](https://docs.comfy.org/).