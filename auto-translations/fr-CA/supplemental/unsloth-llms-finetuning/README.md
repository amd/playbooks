<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Aperçu

Ce guide pratique explique comment effectuer un ajustement fin (fine-tuning) local d'un modèle de langage avec Unsloth sur du matériel AMD.

Il utilise un exemple court d'ajustement fin supervisé (SFT) avec des adaptateurs LoRA sur `unsloth/gemma-4-E4B-it`, à l'aide d'un sous-ensemble de l'ensemble de données `mlabonne/FineTome-100k`. L'objectif est de vous présenter un flux de travail simple de bout en bout couvrant la configuration, l'entraînement, l'inférence et l'enregistrement du résultat ajusté.

L'exemple est conçu pour être pratique et facile à modifier, afin que vous puissiez l'utiliser comme point de départ pour vos propres ensembles de données et modèles.

## Ce que vous apprendrez

- Comment configurer l'environnement Unsloth
- Comment effectuer l'ajustement fin d'un LLM à l'aide du SFT avec Unsloth
- Comment enregistrer le résultat ajusté dans le stockage local

<!-- @device:halo,stx,krk -->
> **Remarque :** Les techniques d'ajustement fin présentées dans ce guide pratique nécessitent au moins **64 Go de mémoire RAM système**, dont au moins **24 Go doivent être disponibles pour le GPU** (ces 24 Go font partie des 64 Go, et ne s'y ajoutent pas).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Remarque :** Les techniques d'ajustement fin présentées dans ce guide pratique nécessitent au moins **24 Go de mémoire GPU totale** et **32 Go de mémoire RAM système**.
> - Sous Windows, la mémoire GPU totale combine la mémoire vidéo (VRAM) dédiée de la carte graphique avec la mémoire GPU partagée (empruntée à la RAM système).
> - Par conséquent, les cartes disposant de moins de 24 Go de VRAM dédiée peuvent tout de même exécuter ce guide pratique en utilisant la mémoire GPU partagée pour combler la différence.
<!-- @os:end -->

<!-- @os:linux -->
> **Remarque :** Les techniques d'ajustement fin présentées dans ce guide pratique nécessitent une carte graphique disposant d'au moins **24 Go de mémoire GPU dédiée** et de **32 Go de mémoire RAM système**.
> - Sous Linux, l'entraînement s'exécute entièrement dans la mémoire VRAM dédiée de la carte graphique.
> - Il n'y a pas de bascule vers la mémoire GPU partagée (RAM système) lorsque la VRAM est épuisée.
> - Les cartes disposant de moins de 24 Go de VRAM dédiée manqueront de mémoire pendant l'entraînement sous Linux, même si le système dispose d'une grande quantité de RAM.
<!-- @os:end -->
<!-- @device:end -->

## Pourquoi Unsloth?

Unsloth facilite l'exécution de l'ajustement fin de LLM sur du matériel local en réduisant l'utilisation de la mémoire et en accélérant l'entraînement par rapport à une configuration standard.

Dans ce guide pratique, nous utilisons Unsloth avec le **SFT basé sur LoRA**. Cela signifie que le modèle de base demeure en grande partie figé, tandis qu'un ensemble beaucoup plus petit de poids d'adaptateur est entraîné. Cette approche convient bien au développement local, car elle est plus légère qu'un ajustement fin complet et permet d'itérer plus rapidement.

Unsloth prend également en charge d'autres approches d'entraînement, notamment QLoRA et les flux de travail d'apprentissage par renforcement. Ce guide pratique se concentre d'abord sur l'approche la plus simple : un petit exemple d'ajustement fin LoRA que les utilisateurs peuvent exécuter, comprendre et étendre.

<!-- @device:halo_box,halo,stx,krk -->
## Configuration de la mémoire

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des logiciels prérequis

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Créer un environnement virtuel

<!-- @os:linux -->
<!-- @device:halo_box -->
Ouvrez un terminal et créez un environnement venv avec le logiciel AMD ROCm™ et PyTorch déjà installés :
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

Ouvrez un terminal et créez un environnement venv :
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque :** Python 3.13 est requis pour Windows.

<!-- @device:halo_box -->
Ouvrez un terminal PowerShell et créez un environnement virtuel :
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Ouvrez un terminal PowerShell et créez un environnement virtuel :
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installation des dépendances de base
<!-- @require:driver -->

> **Important :** Unsloth ne prend pas encore en charge la version 2.13 de PyTorch fournie avec ROCm 10. Pour ce guide pratique, installez **ROCm 7.14 avec PyTorch 2.12** à l'aide des commandes ci-dessous. N'utilisez pas les paquets ROCm 10 / PyTorch 2.13.

**Installez PyTorch avec la prise en charge du logiciel AMD ROCm™** dans l'environnement virtuel créé :

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Pour les autres appareils, veuillez consulter la [documentation ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) pour obtenir les instructions complètes.

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Dépendances supplémentaires

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Remarque :** Pendant l'importation, Unsloth peut tester des voies d'accélération facultatives `bitsandbytes`. Sur certaines versions de ROCm, vous pourriez voir un message tel que `bitsandbytes library load error: Configured ROCm binary not found`. Ce guide pratique utilise l'ajustement fin LoRA standard avec `optim="adamw_torch"`, nous ne dépendons donc pas de l'optimiseur `bitsandbytes` ni de QLoRA 4 bits. Ce message peut être ignoré sans problème.

<!-- @os:windows -->
> **Remarque :** Sous Windows ROCm, Unsloth affichera plusieurs avertissements au démarrage — consultez la section [Avertissements connus](#known-warnings) ci-dessous. Ils peuvent tous être ignorés sans problème; l'entraînement fonctionne correctement.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Télécharger le script d'ajustement fin Unsloth

Plutôt que d'exécuter manuellement chaque étape, ce guide pratique fournit un script clair, de bout en bout, ici : [test_unsloth.py](assets/test_unsloth.py).

Exécutez le code suivant pour lancer le script :

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Le reste du guide pratique passera en revue, sur le plan conceptuel, chaque étape importante du script.

## Fonctionnement

Le script test_unsloth.py effectue les étapes suivantes :
* **Chargement du modèle** : Charge unsloth/gemma-4-E4B-it à l'aide de FastModel.
* **Préparation des données** : Normalise l'ensemble de données (par exemple, FineTome-100k) et applique le modèle de conversation (chat template) de Gemma-4.
* **Application de LoRA** : Ajoute des adaptateurs aux modules de langage, d'attention et MLP pour un entraînement efficace.
* **Entraînement** : Utilise SFTTrainer avec un masquage de perte limité aux réponses.
* **Inférence** : Exécute un test de génération rapide pour vérifier la performance.
* **Enregistrement** : Exporte les adaptateurs LoRA localement.
## Configuration clé

Vous pouvez modifier les constantes suivantes pour personnaliser votre exécution :

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemple du message de bienvenue d'Unsloth et de la sortie lors du chargement des poids du modèle :

![alt text](assets/welcome.png)

## Préparer l'ensemble de données

Nous utilisons un sous-ensemble de :
```text
mlabonne/FineTome-100k
```
L'ensemble de données est : 
* Converti au format de clavardage
* Traité à l'aide du modèle de gabarit de clavardage Gemma-4
* Nettoyé afin de supprimer les jetons BOS en double

## Entraîner le modèle

Le script exécute une courte démonstration d'entraînement, avec les paramètres suivants :
- ~50 étapes
- Petite taille de lot
- Accumulation de gradient

Pendant l'entraînement, vous verrez des journaux comme suit :

![alt text](assets/training.png)


## Sauvegarde et déploiement

### Sauvegarde locale (LoRA)

Le script sauvegarde automatiquement les adaptateurs LoRA dans OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Enregistrer le modèle fusionné (pour vLLM) 

<!-- @os:windows -->
> **Remarque :** vLLM ne prend pas en charge Windows. Pour déployer votre modèle finement ajusté sur Windows, utilisez llama.cpp (voir [Exporter en GGUF](#export-gguf-for-llamacpp) ci-dessous) ou transférez le modèle fusionné vers une machine Linux exécutant vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Pour le déploiement avec vLLM, fusionnez les adaptateurs dans un modèle complet :
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Exporter en GGUF (pour llama.cpp)

Convertissez directement en GGUF pour l'inférence locale :
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Avertissements connus

Ces avertissements sont affichés par Unsloth au démarrage sur Windows ROCm et peuvent tous être ignorés sans danger :

| Avertissement | Raison | Sans danger à ignorer? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes n'a pas de version Windows ROCm | Oui — ce guide utilise `adamw_torch`, et non bnb |
| `No ROCm platform found for torch.distributed` | ROCm sur Windows ne prend pas en charge l'entraînement distribué | Oui — l'entraînement sur un seul GPU n'est pas touché |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth signale les versions non-Linux | Oui — Windows ROCm fonctionne pour le SFT sur un seul GPU |
| `triton is not available` | Triton n'a pas de version Windows | Oui — Unsloth revient aux noyaux PyTorch |

L'entraînement se déroulera correctement malgré ces avertissements.
<!-- @os:end -->

## Prochaines étapes
- Essayez [Unsloth Studio](https://unsloth.ai/docs/new/studio), une interface graphique intuitive pour Unsloth
- Entraînez sur vos propres ensembles de données spécifiques
- Essayez le réglage fin avec différents hyperparamètres
- Déployez avec vLLM ou llama.cpp
- Essayez QLoRA pour une configuration utilisant moins de mémoire

## Ressources

Voici quelques ressources supplémentaires pour en apprendre davantage sur Unsloth et le réglage fin :

* [Documentation d'Unsloth](https://docs.unsloth.ai)

* [Dépôt GitHub d'Unsloth](https://github.com/unslothai/unsloth)

* [Guide de réglage fin d'Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)