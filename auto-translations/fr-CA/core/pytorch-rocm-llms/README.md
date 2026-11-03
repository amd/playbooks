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


Vous souhaitez exécuter des modèles de langage IA puissants sur votre propre matériel? Ce guide vous montre comment faire.
Ce tutoriel utilise PyTorch, propulsé par le logiciel AMD ROCm™, pour exécuter des modèles capables de résumer des documents, de répondre à des questions, de générer du texte, et plus encore, le tout en local.

## Ce que vous apprendrez

- Exécuter des LLM comme gpt-oss-20b et qwen3.5-4B en local à l'aide de PyTorch et de ROCm
- Créer un outil de synthèse de documents à l'aide de LLM

<!-- @device:halo_box,halo,stx,krk -->
## Configuration de la mémoire

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles
> **Remarque** : Si VS Code n'est pas installé, vous pouvez l'installer avec le Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

### Créer un environnement virtuel

<!-- @os:linux -->
<!-- @device:halo_box -->
Sur Linux, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv avec ROCm+Pytorch déjà installé.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

Sur Linux, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
Sur Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv avec ROCm+Pytorch déjà installé.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Sur Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Astuce** : Les utilisateurs de Windows pourraient devoir modifier leur politique d'exécution PowerShell (p. ex.
> en la définissant à RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes Powershell.

<!-- @os:end -->

### Installation des dépendances de base
<!-- @require:driver,pytorch -->

### Installation des dépendances supplémentaires

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Remarque :** Si le modèle ne se charge pas ou manque de mémoire, essayez d'installer le paquet `kernels` pour charger le modèle avec une quantification optimisée.
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Démarrage rapide avec des scripts d'exemple

Ce guide pratique comprend des scripts prêts à l'emploi. Cliquez dessus pour les prévisualiser et les télécharger dans le même répertoire que l'environnement que vous avez créé.

| Script | Description | Utilisation |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Génération de texte de base par LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Résumeur de documents avec prise en charge Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Les deux scripts prennent en charge :
- La sélection du modèle via l'indicateur `--model`
- Le formatage du modèle de discussion pour une invite appropriée du modèle, particulièrement utile pour la synthèse de documents

## Charger et exécuter votre premier LLM

Le script inclus [run_llm.py](assets/run_llm.py) montre comment générer du texte avec des LLM à l'aide de PyTorch et d'AMD ROCm.

> **Remarque :** Lorsque vous chargez un modèle, Hugging Face Transformers vérifie d'abord son cache local (`~/.cache/huggingface/hub` sous Linux, `C:\Users\<user>\.cache\huggingface\hub` sous Windows). Si le modèle n'est pas mis en cache, il est téléchargé automatiquement depuis huggingface.co. La première exécution peut prendre quelques minutes selon la taille du modèle et la vitesse du réseau.

L'extrait ci-dessous montre comment utiliser le modèle et personnaliser les questions posées.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Essayez le script téléchargé :

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Créer un résumeur de documents

Maintenant que vous avez généré une sortie de LLM en local, vous pouvez continuer en créant un résumeur de documents pratique. Dans cette section, vous utiliserez le script [summarizer.py](assets/summarizer.py) pour fournir un fichier .txt et générer automatiquement un résumé concis, le tout exécuté en local sur votre GPU.

Le script est conçu pour fonctionner immédiatement. Ouvrez le script dans un éditeur pour explorer le code, personnaliser les invites et ajuster des paramètres comme la longueur et la température.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Exemples d'utilisation

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## En savoir plus sur les paramètres de génération

| Paramètre | Ce qu'il contrôle | Valeurs typiques |
|-----------|------------------|----------------|
| `max_new_tokens` | La longueur maximale de la sortie du LLM | Utilisez de 50 à 500 jetons pour les résumés. (1 jeton équivaut à environ 0,75 mot anglais) |
| `temperature` | Créativité. Des valeurs faibles rendent la sortie ciblée, tandis que des valeurs élevées apportent plus d'imprévisibilité | - **0,1–0,3** : Ciblé, déterministe (bon pour les résumés) <br> **0,5–0,7** : Équilibré (usage général) <br> **0,8–1,0** : Créatif, varié (remue-méninges) |
| `top_p` | Échantillonnage par noyau - Des valeurs faibles limitent le modèle à des sorties plus restreintes | **0,1-0,5** : Strict, prévisible <br> **0,9-0,95** : (standard, naturel, conversationnel) |


## Applications concrètes

- **Analyse d'articles de recherche** : Extraire les conclusions clés de publications complexes pour un examen rapide
- **Agrégation de nouvelles** : Résumer des articles de presse en brefs bilans quotidiens ou faits saillants
- **Notes de réunion** : Condenser des transcriptions en éléments d'action et en résumés concis
- **Révision de documents juridiques** : Extraire rapidement les clauses ou obligations pertinentes de longs textes juridiques
- **Documentation de code** : Générer des aperçus de dépôts concis et des explications de fonctions
## Prochaines étapes

- **Réglage fin (fine-tuning)** : Adaptez les modèles à votre domaine ou jargon spécifique pour une meilleure précision (voir les guides de réglage fin)
- **Systèmes RAG** : Combinez les LLM avec la récupération de documents pour des réponses et des recherches tenant compte du contexte
- **Exploration de modèles** : Expérimentez avec de nouveaux modèles comme Llama 3, Phi-3 ou Qwen pour de meilleurs résultats
- **Déploiement en production** : Utilisez des outils comme vLLM pour la diffusion évolutive de LLM au sein des organisations

Votre système vous donne le pouvoir d'exécuter des modèles de langage sophistiqués localement. Expérimentez avec différents modèles, invites et paramètres pour découvrir ce qui fonctionne le mieux pour vos applications.