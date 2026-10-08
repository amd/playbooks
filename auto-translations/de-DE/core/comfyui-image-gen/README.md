<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Übersicht

ComfyUI ist eine leistungsstarke, knotenbasierte Oberfläche für Stable Diffusion und andere Diffusionsmodelle. Im Gegensatz zu herkömmlichen Text-zu-Bild-Oberflächen mit einfachen Eingabefeldern stellt ComfyUI die gesamte Bildgenerierungs-Pipeline als visuellen Graphen dar und bietet dir eine feingranulare Kontrolle über jeden Schritt – von der Textcodierung über die Manipulation des latenten Raums bis hin zur finalen Decodierung.

Dieses Tutorial zeigt dir, wie du ComfyUI mit dem Z Image Turbo-Modell auf deiner GPU verwendest, um hochwertige KI-Bilder zu erzeugen.

## Was du lernen wirst

- Wie du ComfyUI startest und die Z-Image Turbo-Vorlage lädst
- Verständnis der Komponenten der Diffusions-Pipeline
- Bilder generieren und Generierungsparameter anpassen
- Workflows speichern und teilen

<!-- @device:halo_box,halo,stx,krk -->
## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Gewähre deinem Benutzer Zugriff auf GPU-Geräte** (melde dich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Eine virtuelle Umgebung erstellen
Öffne unter Linux ein Terminal im Verzeichnis deiner Wahl und führe den folgenden Befehl aus, um eine venv zu erstellen:

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


## ComfyUI starten

<!-- @device:halo_box -->
<!-- @os:windows -->
Um ComfyUI unter Windows zu starten, klicke auf den ComfyUI Desktop Launcher, der sich auf deinem Desktop befindet. Folge den Schritten, um die lokale Version mit AMD zu installieren.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Klicke anschließend auf die ComfyUI-Schaltfläche oben in der Mitte der App. Dadurch wird ein Einstellungstab geöffnet. Öffne den Tab „Storage“ und stelle sicher, dass die Pfade wie folgt eingestellt sind, um auf die vorinstallierten Modelle zuzugreifen.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Auf dem AMD Ryzen™ AI Halo läuft ComfyUI in einem vorgefertigten Container, der keine zusätzliche Python-Einrichtung erfordert.

Um ComfyUI unter Linux zu starten, klicke auf die ComfyUI-Verknüpfung in der Taskleiste. Es sollte sich von selbst in einem Browserfenster öffnen.
>**Tipp**: ComfyUI und seine Modelle werden unter `~/.local/share/ComfyUI/models` gespeichert. Dort kannst du manuell Workflows oder neue Modelle hinzufügen.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Um ComfyUI unter Windows zu starten, klicke einfach auf die ComfyUI-Verknüpfung auf deinem Desktop.
<!-- @os:end -->

<!-- @os:linux -->

So startest du ComfyUI:

1. Stelle sicher, dass du dich im ComfyUI-Verzeichnis befindest.
2. Führe `python3 main.py --use-pytorch-cross-attention` aus

ComfyUI startet einen lokalen Webserver. Öffne deinen Browser unter `http://127.0.0.1:8188`, um auf die Oberfläche zuzugreifen.

> **Tipp**: Lasse das Terminalfenster geöffnet, während du ComfyUI verwendest. Wenn du es schließt, wird der Server gestoppt.
<!-- @os:end -->
<!-- @device:end -->


## Die Z-Image Turbo-Vorlage finden

Bevor du Bilder generierst, musst du die Z-Image Turbo-Vorlage laden. So findest du sie:

1. **Schau an den äußersten linken Bildschirmrand** – dort verläuft eine vertikale Werkzeugleiste von oben nach unten am linken Rand der App.

2. **Finde das Ordnersymbol** – suche in dieser linken Werkzeugleiste nach einem Symbol, das wie ein Ordner aussieht. Wenn du mit der Maus darüberfährst, wird es als „Templates“ bezeichnet.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Klicke auf das Ordnersymbol** – dadurch öffnet sich das Templates-Panel.

4. **Suche nach „Z-Image Turbo“** – verwende die Suchleiste oder scrolle durch die verfügbaren Vorlagen, um den Workflow „Z-Image Turbo Text To Image“ zu finden, und klicke dann, um ihn zu laden.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Modelle herunterladen

<!-- @require:comfyui-models -->
<!-- @prereq:comfyui-models -->

## Die Oberfläche verstehen

Wenn die Z-Image Turbo-Vorlage geladen ist, siehst du eine Arbeitsfläche mit 2 Hauptknoten. Der erste Knoten heißt „Text to Image (Z-Image-Turbo)“, der zweite Knoten dient der Bildanzeige.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Klicke im Z-Image-Knoten oben rechts auf die Schaltfläche, um den Knoten zu erweitern und den Untergraphen anzuzeigen.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Pipeline-Komponenten

Der Z-Image Turbo-Workflow verwendet vier zentrale Modellkomponenten, die zusammenarbeiten:

| Komponente | Rolle |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Wandelt deinen Text-Prompt in Embeddings um, die das Diffusionsmodell versteht |
| **Diffusion Model** (Z-Image Turbo) | Das Kern-Neuronale Netzwerk, das latente Repräsentationen iterativ entrauscht und in Bilder umwandelt |
| **VAE** (Variational Autoencoder) | Codiert Bilder in den/aus dem latenten Raum (decodiert die finalen Latents in Pixel) |
| **LoRA** (optional) | Leichtgewichtige Adapter, die Stil oder Motiv verändern, ohne das Basismodell neu zu trainieren |

Jeder Knoten im Workflow entspricht einer dieser Komponenten. Der Datenfluss verläuft von links nach rechts: Text → Embeddings → gesteuerte Entrauschung → Latents → finales Bild.

## Dein erstes Bild generieren

Das Z-Image Turbo-Modell ist bereits geladen. So generierst du ein Bild:

1. **Gib deinen Prompt ein** im Haupt-Z-Image-Knoten. Sei dabei beschreibend. Hier ein Beispiel:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Optional)**: Bestätige oder passe andere spezifische Einstellungen innerhalb des Untergraphen an.
3. **Klicke auf das blaue „Run Workflow“** in der rechten Ecke (oder drücke `Ctrl+Enter`)
4. Beobachte, wie sich die Knoten hervorheben, während jeder Schritt ausgeführt wird

Die gesamte Ausführung des Workflows sollte in weniger als 30 Sekunden abgeschlossen sein. Dein generiertes Bild erscheint im Knoten **Save Image** und wird im Ordner `output/` gespeichert.

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


## Anpassen der Generierungsparameter
### KSampler-Einstellungen

Der KSampler-Node steuert den zentralen Diffusionsprozess:

| Parameter | Was er steuert | Empfohlen für Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Anzahl der Rauschunterdrückungsiterationen | 4–10 (Turbo-Modelle sind für weniger Schritte destilliert) |
| **cfg** | Classifier-Free-Guidance-Skala – wie genau dem Prompt gefolgt wird | 1,0–2,0 (Turbo-Modelle verwenden eine sehr niedrige Guidance) |
| **sampler_name** | Algorithmus zur Rauschunterdrückung | `euler` und `res_multistep` funktionieren gut für Turbo-Modelle |
| **scheduler** | Verlaufskurve des Rauschplans | `normal` oder `simple` |
| **seed** | Zufallswert für Reproduzierbarkeit | Feste Werte setzen, um eine Komposition iterativ zu verfeinern |

### Bildgröße

Um die Ausgabedimensionen anzupassen, suchen Sie den **Empty Latent Image**-Node und ändern Sie **width** und **height**. Halten Sie die Abmessungen für optimale Qualität bei oder unter 1024 Pixel auf der längsten Seite.

### ModelSamplingAuraFlow

Der **ModelSamplingAuraFlow**-Node ist ein spezialisierter Sampling-Modifikator, der steuert, wie der Diffusionsprozess mit der Rauschplanung umgeht. Sie sehen diesen Node im Z-Image-Turbo-Workflow mit dem Modellausgang verbunden.

| Parameter | Was er steuert | Empfohlene Werte |
|-----------|------------------|-------------------|
| **shift** | Passt das Timing des Rauschplans an – höhere Werte verlagern mehr Detailverfeinerung auf spätere Schritte | 1,0–4,0 (Standard ist 3,0) |

Wann **shift** angepasst werden sollte:

- **Niedrigere Werte (1,0–2,0)**: Schnellere Konvergenz, gut für einfache Kompositionen
- **Höhere Werte (3,0–4,0)**: Allmählichere Verfeinerung, kann feine Details in komplexen Szenen verbessern

Die AuraFlow-Sampling-Methode ist speziell für Flow-Matching-Modelle wie Z-Image Turbo konzipiert und sorgt für eine ordnungsgemäße Rauschverteilung während des gesamten Generierungsprozesses.

## Arbeiten mit Workflows

### Workflows speichern

Klicken Sie auf die Schaltfläche **Save** im Menü, um Ihren Workflow als JSON-Datei zu exportieren. Dies erfasst:

- Alle Nodes und ihre Parameter
- Alle Verbindungen zwischen Nodes
- Aktuellen Prompt-Text

### Workflows laden

Ziehen Sie eine Workflow-JSON-Datei auf die Arbeitsfläche oder verwenden Sie **Load** im Menü. Der standardmäßig angezeigte Z-Image-Turbo-Workflow wird aus einer gespeicherten Workflow-Datei geladen.

### Workflows teilen

Workflows sind in sich geschlossen – teilen Sie die JSON-Datei mit Kollegen, und diese können Ihre genaue Konfiguration reproduzieren. Das macht ComfyUI hervorragend geeignet für gemeinsames Experimentieren.

## Nächste Schritte

- **LoRA-Nodes erkunden**: Stil- oder Motiv-Adapter anwenden, ohne neu zu trainieren
- **Negative Prompts hinzufügen**: Verbinden Sie einen zweiten CLIP-Text-Encode-Node mit dem **negative**-Conditioning-Eingang des KSampler, um das Modell von unerwünschten Merkmalen wie Unschärfe, Artefakten oder Wasserzeichen wegzuführen
- **Eigene Workflows erstellen**: Mehrere Generierungen verketten, Upscaling hinzufügen oder Bildvarianten erstellen
- **Community-Workflows durchsuchen**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) bietet viele einsatzbereite Workflows

Die Stärke von ComfyUI liegt im Experimentieren: Verbinden Sie Nodes auf unterschiedliche Weise, passen Sie Parameter an und beobachten Sie, wie sich jede Änderung auf die Ausgabe auswirkt. Dieses praxisnahe Erkunden schafft ein Gespür dafür, wie Diffusionsmodelle funktionieren.

Weitere Informationen finden Sie in der [ComfyUI-Dokumentation](https://docs.comfy.org/).