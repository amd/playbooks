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

Ce guide pratique montre comment procéder au réglage fin (fine-tuning) local d'un modèle de langage avec Unsloth sur du matériel AMD.

Il utilise un court exemple de réglage fin supervisé (Supervised Fine-Tuning, SFT) avec des adaptateurs LoRA sur `unsloth/gemma-4-E4B-it`, en utilisant un sous-ensemble du jeu de données `mlabonne/FineTome-100k`. L'objectif est de vous fournir un flux de travail complet et simple qui couvre la configuration, l'entraînement, l'inférence et l'enregistrement du résultat du réglage fin.

L'exemple est conçu pour être pratique et facile à modifier, afin que vous puissiez l'utiliser comme point de départ pour vos propres jeux de données et modèles.

## Ce que vous allez apprendre

- Comment configurer l'environnement Unsloth
- Comment effectuer le réglage fin d'un LLM à l'aide du SFT avec Unsloth
- Comment enregistrer le résultat du réglage fin en stockage local

<!-- @device:halo,stx,krk -->
> **Remarque :** Les techniques de réglage fin présentées dans ce guide pratique nécessitent au moins **64 Go de mémoire vive système**, dont au moins **24 Go doivent être disponibles pour le GPU** (les 24 Go font partie des 64 Go, et ne s'y ajoutent pas).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Remarque :** Les techniques de réglage fin présentées dans ce guide pratique nécessitent au moins **24 Go de mémoire GPU totale** et **32 Go de mémoire vive système**.
> - Sous Windows, la mémoire GPU totale combine la VRAM dédiée de la carte graphique avec la mémoire GPU partagée (empruntée à la mémoire vive système).
> - Par conséquent, les cartes disposant de moins de 24 Go de VRAM dédiée peuvent tout de même exécuter ce guide pratique en utilisant la mémoire GPU partagée pour compenser la différence.
<!-- @os:end -->

<!-- @os:linux -->
> **Remarque :** Les techniques de réglage fin présentées dans ce guide pratique nécessitent une carte graphique disposant d'au moins **24 Go de mémoire GPU dédiée** et **32 Go de mémoire vive système**.
> - Sous Linux, l'entraînement s'exécute entièrement dans la VRAM dédiée de la carte graphique.
> - Il n'y a pas de repli vers la mémoire GPU partagée (mémoire vive système) lorsque la VRAM est épuisée.
> - Les cartes disposant de moins de 24 Go de VRAM dédiée manqueront de mémoire pendant l'entraînement sous Linux, même si le système dispose de beaucoup de mémoire vive.
<!-- @os:end -->
<!-- @device:end -->

## Pourquoi Unsloth?

Unsloth facilite l'exécution du réglage fin des LLM sur du matériel local en réduisant l'utilisation de la mémoire et en accélérant l'entraînement par rapport à une configuration standard.

Dans ce guide pratique, nous utilisons Unsloth avec le **SFT basé sur LoRA**. Cela signifie que le modèle de base reste en grande partie figé, tandis qu'un ensemble beaucoup plus restreint de poids d'adaptateurs est entraîné. Cette approche convient bien au développement local, car elle est plus légère qu'un réglage fin complet et permet d'itérer plus rapidement.

Unsloth prend également en charge d'autres approches d'entraînement, notamment QLoRA et les flux de travail d'apprentissage par renforcement. Ce guide pratique se concentre d'abord sur le chemin le plus simple : un petit exemple de réglage fin LoRA que les utilisateurs peuvent exécuter, comprendre et étendre.

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
Ouvrez un terminal et créez un venv avec le logiciel AMD ROCm™ et PyTorch déjà installés :
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous puis reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

Ouvrez un terminal et créez un venv :
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
<!-- @require:pytorch,driver -->

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Remarque :** Pendant l'importation, Unsloth peut sonder les chemins d'accélération optionnels de `bitsandbytes`. Sur certaines versions de ROCm, vous pourriez voir un message tel que `bitsandbytes library load error: Configured ROCm binary not found`. Ce guide pratique utilise le réglage fin LoRA standard avec `optim="adamw_torch"`, nous ne dépendons donc pas de l'optimiseur `bitsandbytes` ni du QLoRA en 4 bits. Ce message peut être ignoré sans risque.

<!-- @os:windows -->
> **Remarque :** Sous ROCm sur Windows, Unsloth affichera plusieurs avertissements au démarrage — voir la section [Avertissements connus](#known-warnings) ci-dessous. Ils peuvent tous être ignorés sans risque; l'entraînement fonctionne correctement.
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

## Télécharger le script de réglage fin Unsloth

Plutôt que d'exécuter manuellement chaque étape, ce guide pratique fournit un script propre et complet ici : [test_unsloth.py](assets/test_unsloth.py).

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

Le reste du guide pratique passera en revue, de manière conceptuelle, chaque étape principale du script. 

## Fonctionnement

Le script test_unsloth.py effectue les étapes suivantes :
* **Chargement du modèle** : Charge unsloth/gemma-4-E4B-it à l'aide de FastModel.
* **Préparation des données** : Normalise le jeu de données (p. ex. FineTome-100k) et applique le gabarit de conversation Gemma-4.
* **Application de LoRA** : Ajoute des adaptateurs aux modules de langage, d'attention et MLP pour un entraînement efficace.
* **Entraînement** : Utilise SFTTrainer avec un masquage de la perte limité aux réponses.
* **Inférence** : Exécute un test de génération rapide pour vérifier la performance.
* **Enregistrement** : Exporte les adaptateurs LoRA localement.

## Configuration principale

Vous pouvez modifier les constantes suivantes pour personnaliser votre exécution :

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemple du message de bienvenue d'Unsloth et de la sortie lors du chargement des poids du modèle :

![texte alternatif](assets/welcome.png)

## Préparer le jeu de données

Nous utilisons un sous-ensemble de :
```text
mlabonne/FineTome-100k
```
Le jeu de données est : 
* Converti au format de conversation
* Traité à l'aide du gabarit de conversation Gemma-4
* Nettoyé pour supprimer les jetons BOS en double

## Entraîner le modèle

Le script exécute une courte démonstration d'entraînement, avec les paramètres suivants :
- environ 50 étapes
- Petite taille de lot
- Accumulation de gradient

Pendant l'entraînement, vous verrez des journaux tels que :

![texte alternatif](assets/training.png)


## Enregistrement et déploiement

### Enregistrement local (LoRA)

Le script enregistre automatiquement les adaptateurs LoRA dans le OUTPUT_DIR.
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
> **Remarque :** vLLM ne prend pas en charge Windows. Pour déployer votre modèle affiné sur Windows, utilisez llama.cpp (voir [Exporter en GGUF](#export-gguf-for-llamacpp) ci-dessous) ou transférez le modèle fusionné vers une machine Linux exécutant vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Pour le déploiement avec vLLM, fusionnez les adaptateurs en un modèle complet :
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

Ces avertissements sont affichés par Unsloth au démarrage sur Windows ROCm et peuvent tous être ignorés en toute sécurité :

| Avertissement | Raison | Peut être ignoré? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes n'a pas de build Windows ROCm | Oui — ce guide utilise `adamw_torch`, et non bnb |
| `No ROCm platform found for torch.distributed` | ROCm sur Windows ne prend pas en charge l'entraînement distribué | Oui — l'entraînement sur un seul GPU n'est pas touché |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth signale les builds non-Linux | Oui — Windows ROCm fonctionne pour le SFT sur un seul GPU |
| `triton is not available` | Triton n'a pas de build Windows | Oui — Unsloth revient aux noyaux PyTorch |

L'entraînement se déroulera correctement malgré ces avertissements.
<!-- @os:end -->

## Étapes suivantes
- Essayez [Unsloth Studio](https://unsloth.ai/docs/new/studio), une interface graphique intuitive pour Unsloth
- Entraînez le modèle sur vos propres ensembles de données
- Essayez l'affinage avec différents hyperparamètres
- Déployez avec vLLM ou llama.cpp
- Essayez QLoRA pour une configuration à faible utilisation de mémoire

## Ressources

Voici quelques ressources supplémentaires pour en apprendre davantage sur Unsloth et l'affinage :

* [Documentation Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Guide d'affinage Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)