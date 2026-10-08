<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Το ComfyUI είναι ένα ισχυρό, βασισμένο σε κόμβους περιβάλλον για το Stable Diffusion και άλλα μοντέλα διάχυσης. Σε αντίθεση με τα παραδοσιακά περιβάλλοντα μετατροπής κειμένου σε εικόνα με απλά πλαίσια προτροπών, το ComfyUI εκθέτει ολόκληρο τον αγωγό δημιουργίας εικόνων ως οπτικό γράφημα, δίνοντάς σας λεπτομερή έλεγχο σε κάθε βήμα, από την κωδικοποίηση κειμένου μέχρι τον χειρισμό του λανθάνοντος χώρου και την τελική αποκωδικοποίηση.

Αυτό το σεμινάριο σας διδάσκει πώς να χρησιμοποιείτε το ComfyUI με το μοντέλο Z Image Turbo στην GPU σας για να δημιουργήσετε εικόνες υψηλής ποιότητας με τεχνητή νοημοσύνη.

## Τι Θα Μάθετε

- Πώς να εκκινήσετε το ComfyUI και να φορτώσετε το πρότυπο Z-Image Turbo
- Κατανόηση των στοιχείων του αγωγού διάχυσης
- Δημιουργία εικόνων και ρύθμιση παραμέτρων δημιουργίας
- Αποθήκευση και κοινή χρήση ροών εργασίας

<!-- @device:halo_box,halo,stx,krk -->
## Ρύθμιση της Διαμόρφωσης Μνήμης

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και συνδεθείτε ξανά για να ενεργοποιηθεί αυτό):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Δημιουργία Εικονικού Περιβάλλοντος
Σε Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και εκτελέστε την παρακάτω εντολή για να δημιουργήσετε ένα venv:

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


## Εκκίνηση του ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Για να εκκινήσετε το ComfyUI σε Windows, κάντε κλικ στην εφαρμογή εκκίνησης ComfyUI Desktop Launcher που βρίσκεται στην επιφάνεια εργασίας σας. Ακολουθήστε τα βήματα για να εγκαταστήσετε την τοπική έκδοση με AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Στη συνέχεια, κάντε κλικ στο κουμπί ComfyUI στο επάνω-μεσαίο μέρος της εφαρμογής. Αυτό θα ανοίξει μια καρτέλα ρυθμίσεων. Ανοίξτε την καρτέλα Storage και βεβαιωθείτε ότι οι διαδρομές έχουν ρυθμιστεί ως εξής για να έχετε πρόσβαση στα προεγκατεστημένα μοντέλα.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Στο AMD Ryzen™ AI Halo, το ComfyUI εκτελείται σε ένα προκατασκευασμένο container που δεν απαιτεί πρόσθετη ρύθμιση Python.

Για να εκκινήσετε το ComfyUI σε Linux, κάντε κλικ στη συντόμευση ComfyUI στη γραμμή εργασιών. Θα πρέπει να ανοίξει αυτόματα σε ένα παράθυρο περιηγητή.
>**Συμβουλή**: Το ComfyUI και τα μοντέλα του αποθηκεύονται στο `~/.local/share/ComfyUI/models`. Εδώ μπορείτε να προσθέσετε χειροκίνητα ροές εργασίας ή νέα μοντέλα.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Για να εκκινήσετε το ComfyUI σε Windows, απλώς κάντε κλικ στη συντόμευση ComfyUI στην επιφάνεια εργασίας σας.
<!-- @os:end -->

<!-- @os:linux -->

Για να εκκινήσετε το ComfyUI:

1. Βεβαιωθείτε ότι βρίσκεστε μέσα στον κατάλογο ComfyUI.
2. Εκτελέστε `python3 main.py --use-pytorch-cross-attention`

Το ComfyUI εκκινεί έναν τοπικό διακομιστή ιστού. Ανοίξτε τον περιηγητή σας στη διεύθυνση `http://127.0.0.1:8188` για να αποκτήσετε πρόσβαση στο περιβάλλον εργασίας.

> **Συμβουλή**: Κρατήστε το παράθυρο τερματικού ανοιχτό ενώ χρησιμοποιείτε το ComfyUI. Αν το κλείσετε, θα διακοπεί ο διακομιστής.
<!-- @os:end -->
<!-- @device:end -->


## Εύρεση του Προτύπου Z-Image Turbo

Πριν από τη δημιουργία εικόνων, πρέπει να φορτώσετε το πρότυπο Z-Image Turbo. Δείτε πώς να το βρείτε:

1. **Κοιτάξτε στο αριστερό άκρο της οθόνης**—υπάρχει μια κάθετη γραμμή εργαλείων που εκτείνεται από πάνω προς τα κάτω στην αριστερή πλευρά της εφαρμογής.

2. **Βρείτε το εικονίδιο φακέλου**—σε αυτή την αριστερή γραμμή εργαλείων, αναζητήστε ένα εικονίδιο που μοιάζει με φάκελο. Όταν τοποθετείτε τον δείκτη πάνω του, φέρει την ετικέτα «Templates».

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Κάντε κλικ στο εικονίδιο φακέλου**—αυτό ανοίγει τον πίνακα Templates.

4. **Αναζητήστε το «Z-Image Turbo»**—χρησιμοποιήστε τη γραμμή αναζήτησης ή πραγματοποιήστε κύλιση στα διαθέσιμα πρότυπα για να βρείτε τη ροή εργασίας Z-Image Turbo Text To Image, και στη συνέχεια κάντε κλικ για να τη φορτώσετε.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Λήψη Μοντέλων

<!-- @require:comfyui-models -->
<!-- @prereq:comfyui-models -->

## Κατανόηση του Περιβάλλοντος Εργασίας

Όταν φορτωθεί το πρότυπο Z-Image Turbo, θα δείτε έναν καμβά με 2 κύριους κόμβους. Ο πρώτος κόμβος ονομάζεται 'Text to Image (Z-Image-Turbo)', και ο δεύτερος κόμβος χρησιμεύει για την προβολή της εικόνας.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Στον κόμβο Z-Image, κάντε κλικ στο επάνω δεξιά κουμπί για να επεκτείνετε τον κόμβο και να δείτε το υπο-γράφημα.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Στοιχεία του Αγωγού

Η ροή εργασίας Z-Image Turbo χρησιμοποιεί τέσσερα βασικά στοιχεία μοντέλου που συνεργάζονται μεταξύ τους:

| Στοιχείο | Ρόλος |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Μετατρέπει την προτροπή κειμένου σας σε ενσωματώσεις (embeddings) που κατανοεί το μοντέλο διάχυσης |
| **Diffusion Model** (Z-Image Turbo) | Το βασικό νευρωνικό δίκτυο που αφαιρεί επαναληπτικά τον θόρυβο από λανθάνουσες αναπαραστάσεις για να παραχθούν εικόνες |
| **VAE** (Variational Autoencoder) | Κωδικοποιεί εικόνες προς/από τον λανθάνοντα χώρο (αποκωδικοποιεί τις τελικές λανθάνουσες τιμές σε εικονοστοιχεία) |
| **LoRA** (προαιρετικό) | Ελαφροί προσαρμογείς που τροποποιούν το στυλ ή το θέμα χωρίς να απαιτείται επανεκπαίδευση του βασικού μοντέλου |

Κάθε κόμβος στη ροή εργασίας αντιστοιχεί σε ένα από αυτά τα στοιχεία. Τα δεδομένα ρέουν από τα αριστερά προς τα δεξιά: κείμενο → ενσωματώσεις → καθοδηγούμενη αφαίρεση θορύβου → λανθάνουσες τιμές → τελική εικόνα.

## Δημιουργία της Πρώτης σας Εικόνας

Το μοντέλο Z-Image Turbo είναι ήδη φορτωμένο. Για να δημιουργήσετε μια εικόνα:

1. **Εισαγάγετε την προτροπή σας** στον κύριο κόμβο Z-Image. Να είστε περιγραφικοί. Ακολουθεί ένα παράδειγμα:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Προαιρετικό)**: Επιβεβαιώστε ή προσαρμόστε τυχόν άλλες συγκεκριμένες ρυθμίσεις μέσα στο υπο-γράφημα.
3. **Κάντε κλικ στο μπλε «Run Workflow»** στην επάνω δεξιά γωνία (ή πατήστε `Ctrl+Enter`)
4. Παρατηρήστε τους κόμβους να επισημαίνονται καθώς εκτελείται κάθε βήμα

Η εκτέλεση ολόκληρης της ροής εργασίας θα πρέπει να ολοκληρωθεί σε λιγότερο από 30 δευτερόλεπτα. Η εικόνα που δημιουργήσατε εμφανίζεται στον κόμβο **Save Image** και αποθηκεύεται στον φάκελο `output/`.

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


## Προσαρμογή Παραμέτρων Δημιουργίας
### Ρυθμίσεις KSampler

Ο κόμβος KSampler ελέγχει τη βασική διαδικασία diffusion:

| Παράμετρος | Τι Ελέγχει | Προτεινόμενο για Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Αριθμός επαναλήψεων denoising | 4–10 (τα turbo μοντέλα είναι distilled για λιγότερα βήματα) |
| **cfg** | Κλίμακα classifier-free guidance—πόσο στενά ακολουθεί το prompt | 1.0–2.0 (τα turbo μοντέλα χρησιμοποιούν πολύ χαμηλή καθοδήγηση) |
| **sampler_name** | Αλγόριθμος denoising | Τα `euler` και `res_multistep` λειτουργούν καλά για turbo μοντέλα |
| **scheduler** | Καμπύλη χρονοδιαγράμματος θορύβου | `normal` ή `simple` |
| **seed** | Τυχαίος σπόρος για αναπαραγωγιμότητα | Ορίστε σταθερές τιμές για να επαναλάβετε μια σύνθεση |

### Μέγεθος Εικόνας

Για να προσαρμόσετε τις διαστάσεις εξόδου, βρείτε τον κόμβο **Empty Latent Image** και τροποποιήστε τα **width** και **height**. Διατηρήστε τις διαστάσεις στα ή κάτω από τα 1024 pixel στη μεγαλύτερη πλευρά για βέλτιστη ποιότητα.

### ModelSamplingAuraFlow

Ο κόμβος **ModelSamplingAuraFlow** είναι ένας εξειδικευμένος τροποποιητής sampling που προσαρμόζει τον τρόπο με τον οποίο η διαδικασία diffusion διαχειρίζεται το χρονοδιάγραμμα θορύβου. Θα δείτε αυτόν τον κόμβο συνδεδεμένο με την έξοδο του μοντέλου στη ροή εργασίας Z-Image Turbo.

| Παράμετρος | Τι Ελέγχει | Προτεινόμενες Τιμές |
|-----------|------------------|-------------------|
| **shift** | Προσαρμόζει τον χρονισμό του χρονοδιαγράμματος θορύβου—υψηλότερες τιμές μεταφέρουν περισσότερη βελτίωση λεπτομέρειας σε μεταγενέστερα βήματα | 1.0–4.0 (η προεπιλογή είναι 3.0) |

Πότε να προσαρμόσετε το **shift**:

- **Χαμηλότερες τιμές (1.0–2.0)**: Ταχύτερη σύγκλιση, καλή για απλές συνθέσεις
- **Υψηλότερες τιμές (3.0–4.0)**: Πιο σταδιακή βελτίωση, μπορεί να βελτιώσει τις λεπτομέρειες σε περίπλοκες σκηνές

Η μέθοδος sampling AuraFlow έχει σχεδιαστεί ειδικά για μοντέλα flow-matching όπως το Z-Image Turbo, διασφαλίζοντας σωστή κατανομή θορύβου σε όλη τη διαδικασία παραγωγής.

## Εργασία με Ροές Εργασίας

### Αποθήκευση Ροών Εργασίας

Κάντε κλικ στο κουμπί **Save** στο μενού για να εξάγετε τη ροή εργασίας σας ως αρχείο JSON. Αυτό καταγράφει:

- Όλους τους κόμβους και τις παραμέτρους τους
- Όλες τις συνδέσεις μεταξύ κόμβων
- Το τρέχον κείμενο prompt

### Φόρτωση Ροών Εργασίας

Σύρετε ένα αρχείο JSON ροής εργασίας στον καμβά, ή χρησιμοποιήστε το **Load** από το μενού. Η ροή εργασίας Z-Image Turbo που βλέπετε από προεπιλογή φορτώνεται από ένα αποθηκευμένο αρχείο ροής εργασίας.

### Κοινή Χρήση Ροών Εργασίας

Οι ροές εργασίας είναι αυτόνομες—μοιραστείτε το αρχείο JSON με συναδέλφους, και εκείνοι μπορούν να αναπαράγουν ακριβώς τη ρύθμισή σας. Αυτό καθιστά το ComfyUI εξαιρετικό για συνεργατικό πειραματισμό.

## Επόμενα Βήματα

- **Εξερευνήστε κόμβους LoRA**: Εφαρμόστε προσαρμογείς στυλ ή θέματος χωρίς επανεκπαίδευση
- **Προσθέστε αρνητικά prompts**: Συνδέστε έναν δεύτερο κόμβο CLIP Text Encode στην είσοδο εξαρτημάτων **negative** του KSampler για να καθοδηγήσετε το μοντέλο μακριά από ανεπιθύμητα χαρακτηριστικά όπως θόλωμα, artifacts, ή watermarks
- **Δημιουργήστε προσαρμοσμένες ροές εργασίας**: Αλυσιδώστε πολλαπλές παραγωγές, προσθέστε upscaling, ή δημιουργήστε παραλλαγές εικόνας
- **Περιηγηθείτε σε ροές εργασίας της κοινότητας**: Το [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) έχει πολλές έτοιμες προς χρήση ροές εργασίας

Το δυνατό σημείο του ComfyUI είναι ο πειραματισμός: συνδέστε κόμβους διαφορετικά, προσαρμόστε παραμέτρους, και παρατηρήστε πώς κάθε αλλαγή επηρεάζει την έξοδο. Αυτή η πρακτική εξερεύνηση οικοδομεί διαίσθηση για το πώς λειτουργούν τα μοντέλα diffusion.

Για περισσότερες πληροφορίες, δείτε το [ComfyUI Documentation](https://docs.comfy.org/).