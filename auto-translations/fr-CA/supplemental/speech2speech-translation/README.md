<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Aperçu

La suite logicielle AMD ROCm™ et PyTorch forment un écosystème unifié pour l'IA sur appareil. Elle fonctionne à la fois sous Windows et Linux, avec une prise en charge officielle d'un large éventail d'appareils, y compris les APU Ryzen™ AI et les GPU Radeon™.

Ce guide vous apprendra à exécuter, entièrement en périphérie, une traduction voix-voix expressive, à faible latence et privée.

## Ce que vous apprendrez

- Comment configurer un environnement voix-voix
- Comment écrire du code Python pour charger et utiliser des modèles voix-voix
- Comment exécuter l'interface Gradio et expérimenter avec celle-ci

## Pourquoi utiliser la traduction voix-voix en temps réel?

- Élimine les frictions entre la traduction et les barrières linguistiques
- Transmet le ton, l'émotion et l'intention sans pauses maladroites
- Favorise la collaboration mondiale et une prise de décision plus rapide

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

### Créer un environnement virtuel

<!-- @os:linux -->
<!-- @device:halo_box -->
Sous Linux, ouvrez un terminal et exécutez l'invite suivante pour créer un venv avec ROCm+PyTorch déjà installé :

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

Sous Linux, ouvrez un terminal et exécutez l'invite suivante pour créer un venv :

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
Sous Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv avec ROCm+PyTorch déjà installé :

<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Astuce** : Les utilisateurs de Windows devront peut-être modifier leur stratégie d'exécution PowerShell (par exemple,
> en la définissant à RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Sous Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv :

<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Astuce** : Les utilisateurs de Windows devront peut-être modifier leur stratégie d'exécution PowerShell (par exemple,
> en la définissant à RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes PowerShell.

<!-- @device:end -->
<!-- @os:end -->

### Installation des dépendances de base

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Dépendances supplémentaires

Installez les dépendances de m4t à l'aide de pip :
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=300 setup=activate-venv hidden=True -->
```python
import importlib
import os
import sys

# Ensure local assets directory is importable
sys.path.insert(0, os.getcwd())

modules = [
    "torch",
    "torchaudio",
    "scipy",
    "soundfile",
    "gradio",
    "transformers",
    "safetensors",
    "sentencepiece",
    "accelerate",
    "tiktoken",
]

for module in modules:
    importlib.import_module(module)
    print(f"PASS: imported {module}")

from transformers import AutoProcessor, SeamlessM4Tv2Model
import lang_list
from lang_list import LANGUAGE_NAME_TO_CODE, ASR_TARGET_LANGUAGE_NAMES, S2ST_TARGET_LANGUAGE_NAMES

assert "English" in LANGUAGE_NAME_TO_CODE, "FAIL: English missing in LANGUAGE_NAME_TO_CODE"
assert len(S2ST_TARGET_LANGUAGE_NAMES) > 0, "FAIL: S2ST_TARGET_LANGUAGE_NAMES is empty"

print("PASS: imported local module lang_list")
print("PASS: key speech2speech imports work")
```
<!-- @test:end -->

<!-- @test:id=verify-scripts timeout=60 hidden=True -->
```python
import ast
import os
import sys

required_files = [
    "infer.py",
    "gradio_demo.py",
    "lang_list.py",
    "input1.wav",
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: All required files exist")

for script in ["infer.py", "gradio_demo.py", "lang_list.py"]:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->


## Configurer la démonstration voix-voix

#### En savoir plus sur seamless-m4t-v2

Consultez la [fiche du modèle](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) sur Hugging Face pour plus d'information.
Voici l'architecture technique des modèles voix-voix :
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Télécharger les scripts

Ce guide comprend des scripts prêts à l'emploi. Veuillez tous les télécharger dans le même répertoire que l'environnement que vous avez créé.

| Script | Description | Utilisation |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Génération de texte LLM de base | `python infer.py` |
| [input1.wav](assets/input1.wav) | Fichier audio d'exemple | S.O. |
| [lang_list.py](assets/lang_list.py) | Fichier de prise en charge des langues | S.O. |
| [gradio_demo.py](assets/gradio_demo.py) | Interface intuitive pour la traduction vocale | `python gradio_demo.py --no-share` |


### Commencer avec infer.py

Pour exécuter le script, lancez 
```bash
python infer.py
```
> **Remarque** : Vous pourriez voir des avertissements. Ceci est normal.
 
  
#### Explication du code
**Extrait 1 : Importation des dépendances nécessaires**

```python 
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"

import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio

from transformers import AutoProcessor, SeamlessM4Tv2Model

# ============ Configuration ============
DEFAULT_TARGET_LANGUAGE = "eng"

INPUT_AUDIO_PATH = "./input1.wav"
OUTPUT_AUDIO_PATH = "./out1.wav"

# Automatically downloads + caches via Hugging Face
MODEL_ID = "facebook/seamless-m4t-v2-large"

TARGET_SAMPLE_RATE = 16_000
```

**Extrait 2 : Chargement des modèles depuis HuggingFace**

Cette fonction prend en entrée un identifiant de modèle et télécharge le modèle s'il n'est pas déjà téléchargé. Elle retourne ensuite le processeur et le modèle pour la fonction suivante.
```python
def load_model(model_id: str, device: torch.device):
    start = time.time()

    print("Loading model (downloads automatically on first run)...")

    processor = AutoProcessor.from_pretrained(model_id)

    dtype = torch.float16 if device.type == "cuda" else torch.float32

    model = SeamlessM4Tv2Model.from_pretrained(model_id, torch_dtype=dtype).to(device)

    elapsed = time.time() - start
    print(f"Model loading duration: {elapsed:.2f} seconds")

    return processor, model
```

**Extrait 3 : Charger le fichier audio .wav en entrée et le prétraiter**

Cette fonction charge le clip audio et le rééchantillonne à la fréquence cible.
```python
def preprocess_audio(audio_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> torch.Tensor:

    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)

    # Convert to tensor [channels, samples]
    audio = torch.from_numpy(audio_np.T)

    # Resample if needed
    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)

    # Convert stereo -> mono
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    return audio
```

**Extrait 4 : Exécuter l'inférence**

Cette fonction exécute l'inférence avec le modèle et retourne le résultat généré.
```python
def run_inference(model, processor, audio: torch.Tensor, device: torch.device, target_lang: str = DEFAULT_TARGET_LANGUAGE):

    start = time.time()

    audio_inputs = processor(
        audio=audio.squeeze(0).cpu().numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    audio_inputs = {
        k: v.to(device) if isinstance(v, torch.Tensor) else v
        for k, v in audio_inputs.items()
    }

    with torch.inference_mode():
        output = model.generate(**audio_inputs, tgt_lang=target_lang)[0]

    audio_array = output.float().cpu().numpy().squeeze()

    elapsed = time.time() - start
    print(f"Inference duration: {elapsed:.2f} seconds")

    return audio_array, elapsed
```

**Extrait 5 : Enregistrer le fichier traduit**

Cette fonction enregistre le tableau audio dans un fichier .WAV. 
```python
def save_audio(audio_array: np.ndarray, output_path: str, sample_rate: int):
    if np.issubdtype(audio_array.dtype, np.floating):
        max_abs = np.max(np.abs(audio_array)) if audio_array.size else 0.0

        if max_abs > 1.0:
            audio_array = audio_array / max_abs

        audio_array = (audio_array * 32767.0).clip(-32768, 32767).astype(np.int16)

    scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

    print(f"Output saved to: {output_path}")
```

<!-- @os:windows -->
<!-- @test:id=infer-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
Remove-Item .\out1.wav -Force -ErrorAction SilentlyContinue

if (-not (Test-Path .\input1.wav)) { throw "FAIL: input1.wav not found in current directory" }

python .\infer.py
if ($LASTEXITCODE -ne 0) { throw "infer.py failed" }

if (-not (Test-Path .\out1.wav)) { throw "FAIL: out1.wav was not created" }
$file = Get-Item .\out1.wav
if ($file.Length -le 0) { throw "FAIL: out1.wav is empty" }

Write-Host "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=infer-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail
rm -f ./out1.wav

if [ ! -f ./input1.wav ]; then
  echo "FAIL: input1.wav not found in current directory"
  exit 1
fi

python ./infer.py

if [ ! -f ./out1.wav ]; then
  echo "FAIL: out1.wav was not created"
  exit 1
fi
if [ ! -s ./out1.wav ]; then
  echo "FAIL: out1.wav is empty"
  exit 1
fi

echo "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

### Exécuter la démonstration de l'interface Gradio :

Maintenant que vous avez exécuté un exemple de script de base, les instructions suivantes fournissent une interface utile qui s'appuie sur le code que nous avons écrit et qui facilite la traduction voix-voix en direct.

#### Exécuter Gradio localement

```bash
python ./gradio_demo.py --no-share
```
Ensuite, ouvrez votre navigateur Web à l'adresse `http://127.0.0.1:7860` pour accéder à l'interface.


### Exemple d'interface Gradio :

<p align="center">
  <img src="assets/gradio.png" alt="gradio UI" width="600"/>
</p>

<!-- @os:windows -->
<!-- @test:id=gradio-ui-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
'@

$tempPy = Join-Path $env:TEMP "gradio_ui_smoke_ci.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy

if ($LASTEXITCODE -ne 0) {
  Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
  throw "gradio UI smoke test failed"
}

Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=gradio-ui-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail

python - <<'PY'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
PY
```
<!-- @test:end --> 
<!-- @os:end -->


## Prochaines étapes

- Combinez des dizaines de langues pour une traduction rapide.
- Partagez votre démonstration avec d'autres : Ajoutez --share pour créer un lien public accessible à distance par n'importe qui, ou déployez de façon permanente à l'aide de Hugging Face Spaces

## Ressources

Voici quelques ressources supplémentaires pour en savoir plus sur la traduction voix-voix :  
* Le dépôt se trouve ici https://huggingface.co/facebook/seamless-m4t-v2-large 
* Recherche universitaire liée à « Seamless: Multilingual Expressive and Streaming Speech Translation »
* Partage et déploiement Gradio : [Guide de partage de votre application](https://www.gradio.app/guides/sharing-your-app) et [Déployer vers Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)