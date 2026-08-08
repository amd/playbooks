<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Aperçu

ComfyUI est une interface puissante, basée sur des nœuds, pour Stable Diffusion et d'autres modèles de diffusion. Contrairement aux interfaces traditionnelles de texte-vers-image avec de simples zones de saisie, ComfyUI expose l'ensemble du pipeline de génération d'images sous forme de graphe visuel, vous offrant un contrôle précis sur chaque étape, de l'encodage du texte à la manipulation de l'espace latent jusqu'au décodage final.

Ce tutoriel vous apprend à utiliser ComfyUI avec le modèle Z Image Turbo sur votre GPU pour générer des images IA de haute qualité.

## Ce que vous allez apprendre

- Comment lancer ComfyUI et charger le modèle Z-Image Turbo
- Comprendre les composants du pipeline de diffusion
- Générer des images et ajuster les paramètres de génération
- Enregistrer et partager des workflows

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

#### Créer un environnement virtuel
Sous Linux, ouvrez un terminal dans le répertoire de votre choix et exécutez la commande suivante pour créer un venv :

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


## Lancement de ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
Pour lancer ComfyUI sous Windows, cliquez sur le lanceur ComfyUI Desktop situé sur votre bureau. Suivez les étapes pour installer la version locale avec AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

Ensuite, cliquez sur le bouton ComfyUI en haut au centre de l'application. Cela ouvrira un onglet de paramètres. Ouvrez l'onglet Storage et assurez-vous que les chemins sont définis comme suit pour accéder aux modèles préinstallés.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Sur AMD Ryzen™ AI Halo, ComfyUI s'exécute dans un conteneur préconfiguré qui ne nécessite aucune configuration Python supplémentaire.

Pour lancer ComfyUI sous Linux, cliquez sur le raccourci ComfyUI dans la barre des tâches. Il devrait s'ouvrir automatiquement dans une fenêtre de navigateur.
>**Astuce** : ComfyUI et ses modèles sont stockés dans `~/.local/share/ComfyUI/models`. C'est ici que vous pouvez ajouter manuellement des workflows ou de nouveaux modèles.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Pour lancer ComfyUI sous Windows, cliquez simplement sur le raccourci ComfyUI sur votre bureau.
<!-- @os:end -->

<!-- @os:linux -->

Pour lancer ComfyUI :

1. Assurez-vous d'être dans le répertoire ComfyUI. 
2. Exécutez `python3 main.py --use-pytorch-cross-attention`

ComfyUI démarre un serveur web local. Ouvrez votre navigateur à l'adresse `http://127.0.0.1:8188` pour accéder à l'interface.

> **Astuce** : Gardez la fenêtre du terminal ouverte pendant l'utilisation de ComfyUI. La fermer arrêtera le serveur.
<!-- @os:end -->
<!-- @device:end -->


## Trouver le modèle Z-Image Turbo

Avant de générer des images, vous devez charger le modèle Z-Image Turbo. Voici comment le trouver :

1. **Regardez le bord gauche de l'écran**—il y a une barre d'outils verticale qui s'étend de haut en bas sur le côté gauche de l'application.

2. **Trouvez l'icône de dossier**—dans cette barre d'outils gauche, recherchez une icône ressemblant à un dossier. Lorsque vous survolez cette icône, elle est intitulée « Templates ».

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **Cliquez sur l'icône de dossier**—cela ouvre le panneau Templates.

4. **Recherchez « Z-Image Turbo »**—utilisez la barre de recherche ou parcourez les modèles disponibles pour trouver le workflow Z-Image Turbo Text To Image, puis cliquez pour le charger.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## Téléchargement des modèles

<!-- @require:comfyui-models -->

## Comprendre l'interface

Lorsque le modèle Z-Image Turbo se charge, vous verrez un canevas avec 2 nœuds principaux. Le premier nœud s'appelle « Text to Image (Z-Image-Turbo) », et le second sert à visualiser l'image. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Sur le nœud Z-Image, cliquez sur le bouton en haut à droite pour développer le nœud et voir le sous-graphe.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### Composants du pipeline

Le workflow Z-Image Turbo utilise quatre composants de modèle clés qui fonctionnent ensemble :

| Composant | Rôle |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | Convertit votre invite textuelle en embeddings compris par le modèle de diffusion |
| **Diffusion Model** (Z-Image Turbo) | Le réseau neuronal principal qui débruite de manière itérative les représentations latentes en images |
| **VAE** (Variational Autoencoder) | Encode les images vers/depuis l'espace latent (décode les latents finaux en pixels) |
| **LoRA** (optionnel) | Adaptateurs légers qui modifient le style ou le sujet sans réentraîner le modèle de base |

Chaque nœud du workflow correspond à l'un de ces composants. Les données circulent de gauche à droite : texte → embeddings → débruitage guidé → latents → image finale.
## Génération de votre première image

Le modèle Z-Image Turbo est déjà chargé. Pour générer une image :

1. **Saisissez votre prompt** dans le nœud principal Z-Image. Soyez descriptif. Voici un exemple :
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(Facultatif)** : Confirmez ou ajustez tout autre paramètre spécifique au sein du sous-graphe.
3. **Cliquez sur le bouton bleu « Run Workflow »** dans le coin droit (ou appuyez sur `Ctrl+Enter`)
4. Observez les nœuds se mettre en surbrillance au fur et à mesure de l'exécution de chaque étape

L'exécution complète du workflow doit prendre moins de 30 secondes. L'image générée apparaît dans le nœud **Save Image** et est enregistrée dans le dossier `output/`.

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


## Ajustement des paramètres de génération

### Paramètres du KSampler

Le nœud KSampler contrôle le processus de diffusion principal :

| Paramètre | Ce qu'il contrôle | Recommandé pour Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | Nombre d'itérations de débruitage | 4–10 (les modèles turbo sont distillés pour nécessiter moins d'étapes) |
| **cfg** | Échelle de guidage sans classificateur (classifier-free guidance)—à quel point suivre fidèlement le prompt | 1.0–2.0 (les modèles turbo utilisent un guidage très faible) |
| **sampler_name** | Algorithme de débruitage | `euler` et `res_multistep` fonctionnent bien pour les modèles turbo |
| **scheduler** | Courbe du schéma de bruit | `normal` ou `simple` |
| **seed** | Graine aléatoire pour la reproductibilité | Définissez des valeurs fixes pour itérer sur une composition |

### Taille de l'image

Pour ajuster les dimensions de sortie, trouvez le nœud **Empty Latent Image** et modifiez **width** et **height**. Conservez des dimensions égales ou inférieures à 1024 pixels sur le côté le plus long pour une qualité optimale.

### ModelSamplingAuraFlow

Le nœud **ModelSamplingAuraFlow** est un modificateur d'échantillonnage spécialisé qui ajuste la manière dont le processus de diffusion gère le calendrier de bruit. Vous verrez ce nœud connecté à la sortie du modèle dans le workflow Z-Image Turbo.

| Paramètre | Ce qu'il contrôle | Valeurs recommandées |
|-----------|------------------|-------------------|
| **shift** | Ajuste le calendrier temporel du bruit—des valeurs plus élevées repoussent davantage l'affinement des détails vers les étapes suivantes | 1.0–4.0 (la valeur par défaut est 3.0) |

Quand ajuster **shift** :

- **Valeurs plus basses (1.0–2.0)** : Convergence plus rapide, adaptée aux compositions simples
- **Valeurs plus élevées (3.0–4.0)** : Affinement plus progressif, peut améliorer les détails fins dans les scènes complexes

La méthode d'échantillonnage AuraFlow est spécifiquement conçue pour les modèles à correspondance de flux (flow-matching) comme Z-Image Turbo, garantissant une distribution de bruit adéquate tout au long du processus de génération.

## Travailler avec les workflows

### Enregistrement des workflows

Cliquez sur le bouton **Save** dans le menu pour exporter votre workflow sous forme de fichier JSON. Cela capture :

- Tous les nœuds et leurs paramètres
- Toutes les connexions entre les nœuds
- Le texte de prompt actuel

### Chargement des workflows

Faites glisser un fichier JSON de workflow sur le canevas, ou utilisez **Load** depuis le menu. Le workflow Z-Image Turbo affiché par défaut est chargé à partir d'un fichier de workflow enregistré.

### Partage des workflows

Les workflows sont autonomes—partagez le fichier JSON avec vos collègues, et ils pourront reproduire exactement votre configuration. Cela fait de ComfyUI un excellent outil pour l'expérimentation collaborative.

## Étapes suivantes

- **Explorez les nœuds LoRA** : Appliquez des adaptateurs de style ou de sujet sans réentraînement
- **Ajoutez des prompts négatifs** : Connectez un second nœud CLIP Text Encode à l'entrée de conditionnement **negative** du KSampler pour orienter le modèle à l'écart des caractéristiques indésirables comme le flou, les artefacts ou les filigranes
- **Créez des workflows personnalisés** : Enchaînez plusieurs générations, ajoutez de l'upscaling, ou créez des variations d'images
- **Parcourez les workflows de la communauté** : [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) propose de nombreux workflows prêts à l'emploi

La force de ComfyUI réside dans l'expérimentation : connectez les nœuds différemment, ajustez les paramètres, et observez comment chaque changement affecte le résultat. Cette exploration pratique développe votre intuition sur le fonctionnement des modèles de diffusion.

Pour plus d'informations, consultez la [documentation ComfyUI](https://docs.comfy.org/).