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

## Vue d'ensemble

Ce tutoriel fournit des exemples étape par étape pour affiner un grand modèle de langage (LLM) avec PyTorch et ROCm. Il couvre plusieurs techniques, du fine-tuning standard aux stratégies de fine-tuning à paramètres efficaces (PEFT) économes en mémoire, afin que vous puissiez facilement adapter des modèles à vos besoins.

**Modèle utilisé** : google/gemma-3-4b-it  *(voir [Activer l'authentification HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) si le modèle est restreint)*  
**Matériel** : GPU AMD Radeon™ avec prise en charge ROCm  
**Framework** : PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Remarque :** 
> - Le fine-tuning complet nécessite au moins **64 Go de RAM système**, dont au moins **32 Go doivent être disponibles pour le GPU** (les 32 Go font partie des 64 Go, et ne s'y ajoutent pas).
> - Vous pouvez également essayer d'autres architectures de modèles, notamment **GPT-OSS-20B**, en substituant le modèle dans les scripts d'entraînement fournis.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Remarque :** Le fine-tuning LoRA et QLoRA nécessite au moins **32 Go de RAM système**, dont au moins **16 Go doivent être disponibles pour le GPU** (les 16 Go font partie des 32 Go, et ne s'y ajoutent pas).
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque :** Le fine-tuning LoRA nécessite au moins **32 Go de RAM système**, dont au moins **16 Go doivent être disponibles pour le GPU** (les 16 Go font partie des 32 Go, et ne s'y ajoutent pas).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Remarque :** Le fine-tuning LoRA et QLoRA nécessite une carte graphique disposant d'au moins **16 Go de mémoire GPU dédiée** et de **32 Go de RAM système**.
> - Sous Linux, l'entraînement s'exécute entièrement dans la VRAM dédiée de la carte graphique.
> - Il ne bascule pas vers la mémoire GPU partagée (RAM système) lorsque la VRAM est saturée.
> - Les cartes disposant de moins de 16 Go de VRAM dédiée manqueront de mémoire pendant l'entraînement sous Linux, même si le système dispose de beaucoup de RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque :** Le fine-tuning LoRA nécessite au moins **16 Go de mémoire GPU totale** et **32 Go de RAM système**.
> - Sous Windows, la mémoire GPU totale combine la VRAM dédiée de la carte graphique avec la mémoire GPU partagée (empruntée à la RAM système).
> - Par conséquent, les cartes disposant de moins de 16 Go de VRAM dédiée peuvent tout de même exécuter ce playbook en utilisant la mémoire GPU partagée pour combler la différence.
<!-- @os:end -->
<!-- @device:end -->

## Ce que vous allez apprendre

- Comment affiner un LLM en utilisant LoRA, QLoRA et le fine-tuning complet avec PyTorch et ROCm
- Comment enregistrer et déployer votre modèle affiné
- Comment surveiller l'entraînement et déboguer les problèmes courants

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

#### Créer un environnement virtuel

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Installation des dépendances de base
<!-- @require:pytorch -->

#### Dépendances supplémentaires

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows :** Seuls les packages principaux sont testés et pris en charge ici. **bitsandbytes n'est pas bien pris en charge sous Windows**, donc l'installation Windows l'omet ; utilisez LoRA ou le fine-tuning complet sous Windows (QLoRA nécessite bitsandbytes et est destiné à Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Activer l'authentification HF (modèles restreints, personnalisés ou non préinstallés)

Dans cet exemple, nous utilisons **google/gemma-3-4b-it**, qui est un modèle **restreint**. Vous devez accepter les conditions du modèle sur Hugging Face, puis vous authentifier afin que les scripts d'entraînement puissent le télécharger.

1. **Accepter la licence :** Ouvrez [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), connectez-vous (ou créez un compte), et acceptez la licence/les conditions sur la page du modèle (par exemple, « Agree and access repository »).
2. **Installer et se connecter :** Installez le CLI Hugging Face, puis exécutez la connexion standard :

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Comprendre les techniques

### Qu'est-ce que LoRA ?

**LoRA (Low-Rank Adaptation)** conserve le modèle de base gelé et entraîne uniquement de petites matrices « adaptatrices » qui sont ajoutées à certaines couches. 

- **L'idée clé** : au lieu de mettre à jour une immense matrice de poids comportant des millions de paramètres, nous apprenons une mise à jour de faible rang (deux petites matrices dont le produit compte beaucoup moins de paramètres). Cela permet une réduction importante des paramètres entraînables et de la VRAM, tout en conservant l'essentiel de la qualité d'un fine-tuning complet.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Qu'est-ce que QLoRA ?

**QLoRA** combine la **quantification 4 bits** avec **LoRA**. Le modèle de base est chargé en 4 bits (importantes économies de mémoire), et seuls les adaptateurs LoRA sont entraînés avec une précision plus élevée. Vous bénéficiez ainsi de l'efficacité paramétrique de LoRA, ainsi que d'une VRAM bien plus réduite, au prix d'un léger compromis de qualité par rapport à un LoRA en pleine précision. Notez que la quantification 4 bits peut provoquer des instabilités numériques (pics de perte ou NaN), c'est pourquoi les utilisateurs peuvent souvent préférer **LoRA** si suffisamment de VRAM est disponible.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Remarque** : Pour les modèles de base MXFP4 tels que `openai/gpt-oss-20b`, nous recommandons d'utiliser **LoRA** (`train_lora.py`) plutôt que QLoRA. Le chemin 4 bits `bitsandbytes` du script QLoRA déquantifie généralement les poids MXFP4 en BF16, de sorte que l'exécution se comporte comme un LoRA standard. Le MXFP4 natif nécessite `bitsandbytes` compilé depuis les sources ainsi qu'une pile Transformers/Triton/kernels correspondante. Consultez la [documentation MXFP4 de Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Choisissez votre méthode

| Méthode | Mémoire | Vitesse | Qualité | Idéal pour |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux uniquement) | 12-16 Go | La plus rapide | 90-95 % | Utilisation mémoire réduite |
| **LoRA** | 24-32 Go | Rapide | 95-98 % | Approche équilibrée |
| **Full** | 80 Go+ | La plus lente | 100 % | Qualité maximale |

### 3. Lancer l'entraînement

**Jeu de données et ce que le modèle apprend**  
Les scripts transforment le jeu de données en exemples de conversation. Par exemple, le script QLoRA utilise **Abirate/english_quotes** : chaque exemple devient une paire utilisateur-assistant comme :

- **Utilisateur :** « Donne-moi une citation sur : &lt;tag&gt; »
- **Assistant :** « &lt;citation&gt; – &lt;auteur&gt; »

Le fine-tuning apprend au modèle à répondre aux invites demandant des citations sur un sujet et à les renvoyer au format `<texte de la citation> - <auteur>`. Les scripts LoRA et de fine-tuning complet utilisent **databricks/databricks-dolly-15k** (paires instruction/réponse générales), donc la tâche exacte varie selon le script ; l'idée reste la même : adapter le modèle à votre jeu de données et format choisis.

Voici un résumé des méthodes d'entraînement disponibles. Chaque méthode renvoie vers son script et fournit une brève description pour vous aider à choisir la bonne approche.

| Script                           | Méthode            | Description                                                                                                         | VRAM typique | Recommandé pour                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Entraîne de petites matrices d'adaptation tout en gelant le modèle de base. 3 à 5 fois plus rapide ; environ 95-98 % de la qualité complète.                         | 24-32 Go      | Utilisateurs avancés ; adaptateurs multiples ; VRAM plus importante    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux uniquement)*             | **QLoRA**       | Quantification 4 bits + adaptateurs LoRA. Utilisation mémoire la plus faible, la plus rapide, léger compromis sur la qualité. Nécessite `bitsandbytes` (Linux uniquement).                            | 12-16 Go      | La plupart des utilisateurs ; expérimentations rapides ; VRAM limitée      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Fine-tuning complet** | Met à jour tous les paramètres du modèle. Qualité maximale ; utilisation mémoire et calcul la plus élevée.                                    | 40 Go+      | Qualité maximale ; recherche ; VRAM importante           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Remarque :** Le fine-tuning complet (`train_full_finetuning.py`) peut nécessiter plus de 64 Go de RAM système et peut ne pas être réalisable sur cet appareil. Envisagez plutôt d'utiliser LoRA ou QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque :** Le fine-tuning complet (`train_full_finetuning.py`) peut nécessiter plus de 64 Go de RAM système et peut ne pas être réalisable sur cet appareil. Envisagez plutôt d'utiliser LoRA.
<!-- @os:end -->
<!-- @device:end -->

Sélectionnez simplement votre `Training method` préférée, téléchargez le script correspondant et exécutez-le à l'aide de la commande, en gardant votre environnement virtuel activé : 

```python
python3 train_<method_name>.py.
```

## Utiliser votre modèle affiné

### Après un fine-tuning complet

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Après un entraînement LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Fusionner l'adaptateur LoRA dans le modèle de base

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Remarque :**  
- Assurez-vous que le nom du répertoire du modèle (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) correspond à votre dossier de sortie réel issu de l'entraînement.  
- Si vous avez utilisé LoRA au lieu de QLoRA, remplacez simplement le chemin en conséquence.  
- Certains modèles Gemma nécessitent de spécifier `trust_remote_code=True` dans `from_pretrained` ; ajoutez-le si vous voyez un avertissement à ce sujet.

Pour des paramètres personnalisés supplémentaires (jetons de remplissage, appareil, etc.), consultez le script que vous avez utilisé pour l'entraînement.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Guide de personnalisation

### Utiliser votre propre jeu de données

Tous les scripts utilisent le même format de jeu de données. Remplacez la section de chargement :

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Format du jeu de données pour un fichier JSON/JSONL local :**

Lorsque vous utilisez cette méthode, veuillez vous assurer que vos fichiers JSON sont correctement structurés afin d'éviter les erreurs d'analyse. 

Les directives suivantes doivent être respectées :
* **Formatage du fichier :** les fichiers JSON doivent être formatés dans un environnement de développement intégré (IDE) afin de garantir une structure et une syntaxe correctes.
* **Clés requises :** le fichier JSON personnalisé doit contenir les clés `instruction` et `response`. Ces clés sont essentielles au bon fonctionnement de la méthode.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Format du jeu de données pour un jeu de données Hugging Face Hub**

Lorsque vous utilisez des jeux de données provenant de Hugging Face, veuillez vous assurer que vos jeux de données sont correctement structurés afin de faciliter une intégration sans accroc. 

Les directives suivantes doivent être suivies :
* **Paire instruction-réponse :** privilégiez les jeux de données comportant une paire `instruction-response`. Cette structure est essentielle au bon fonctionnement prévu.
* **Modification de clé personnalisée :** si votre jeu de données ne respecte pas la structure `instruction-response`, vous avez la possibilité de modifier la fonction `format_instruction()`. Cela vous permet de prendre en compte des clés spécifiques selon vos besoins.

Exemple d'ajustement : dans les cas où la sortie du jeu de données doit être ajustée, vous pouvez modifier la section de réponse dans la fonction format_instruction() pour répondre à vos besoins.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Format du jeu de données pour un fichier CSV**

Pour utiliser le script avec un format de fichier CSV, vous devez vous assurer que le fichier CSV contient des colonnes nommées `instruction` et `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Ajuster les paramètres d'entraînement

Modifiez le script d'entraînement et changez les variables selon vos objectifs : **taux d'apprentissage** (`LR`), **époques** (`EPOCHS`), **taille de lot** (`BATCH_SIZE`), **accumulation de gradient** (`GRAD_ACCUM_STEPS`), et pour LoRA/QLoRA le **rang** (`LORA_R`). Pour des exécutions plus rapides, utilisez moins d'époques et un taux d'apprentissage (LR) plus élevé ; pour une meilleure qualité, utilisez plus d'époques et un LR plus faible. Réduisez la taille de lot ou la longueur de séquence si vous rencontrez des erreurs de mémoire insuffisante.
### Astuces d'optimisation de la mémoire

Si vous rencontrez des erreurs de mémoire insuffisante :

**1. Réduire la taille du batch :**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Réduire la longueur de séquence :**
```python
max_seq_length=256  # Instead of 512
```

**3. Utiliser une quantification plus agressive :**
```
Full → LoRA → QLoRA
```

**4. Activer le gradient checkpointing (fine-tuning complet uniquement) :**
```python
model.gradient_checkpointing_enable()
```

---

## Surveillance et débogage

### Surveiller la mémoire GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Facultatif) Suivre les expériences avec Weights & Biases

Pour enregistrer les runs et les métriques dans [Weights & Biases](https://wandb.ai) :

```bash
pip install wandb
wandb login
```

Dans le script d'entraînement, définissez `report_to="wandb"` et éventuellement `run_name="your-experiment-name"` dans la configuration du trainer. Si vous préférez ne pas utiliser Wandb, laissez `report_to` à sa valeur par défaut ou définissez-le sur `"none"`.

### Problèmes courants

#### Mémoire insuffisante (OOM)

**Solution :** Réduisez la taille du batch et/ou utilisez QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### La perte ne diminue pas

**Solution :** Ajustez le taux d'apprentissage
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Entraînement lent

**Solution :** Augmentez la taille du batch si la mémoire le permet
```python
BATCH_SIZE = 8
```
## Étapes suivantes

Une fois votre fine-tuning terminé avec succès, envisagez les étapes suivantes pour tirer le meilleur parti de votre modèle :

1. **Évaluez** minutieusement sur des données de test isolées afin de mesurer la généralisation et d'éviter le surapprentissage.
2. **Expérimentez** en essayant différentes valeurs d'hyperparamètres pour obtenir de meilleurs compromis en matière de précision, de vitesse et de mémoire.
3. **Suivez** toutes vos expériences (et les métriques associées) avec Weights & Biases pour une recherche reproductible.
4. **Essayez** l'entraînement sur vos propres jeux de données personnalisés pour adapter le modèle spécifiquement à votre cas d'usage.
5. **Déployez** votre modèle affiné pour une inférence rapide à l'aide de backends efficaces tels que vLLM sur du matériel compatible.
6. **Explorez** des techniques avancées telles que l'ingénierie de prompts, la précision mixte et des longueurs de séquence plus importantes.
7. **Entraînez** plusieurs adaptateurs LoRA pour différentes tâches ou domaines et échangez-les selon les besoins.

---