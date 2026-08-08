<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

## Aperçu

Le réglage fin efficace est essentiel pour adapter les grands modèles de langage (LLM) à des tâches spécifiques. LLaMA Factory est une plateforme conviviale et à code source ouvert qui simplifie l'entraînement et le réglage fin des grands modèles de langage et des modèles multimodaux. Elle permet aux utilisateurs de personnaliser localement des centaines de modèles préentraînés avec un minimum de codage.

Ce guide vous apprend à effectuer un réglage fin de LLM à l'aide de LLaMA Factory sur votre matériel AMD local.

<!-- @device:stx,krk -->
> **Remarque :** Les techniques de réglage fin présentées dans ce guide nécessitent au moins **32 Go de mémoire vive système**, dont au moins **16 Go doivent être disponibles pour le GPU** (les 16 Go font partie des 32 Go, et ne s'y ajoutent pas).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Remarque :** Les techniques de réglage fin présentées dans ce guide nécessitent au moins **16 Go de mémoire GPU totale** et **32 Go de mémoire vive système**.
> - Sous Windows, la mémoire GPU totale combine la mémoire VRAM dédiée de la carte graphique et la mémoire GPU partagée (empruntée à la mémoire vive système).
> - Ainsi, les cartes disposant de moins de 16 Go de VRAM dédiée peuvent tout de même exécuter ce guide en utilisant la mémoire GPU partagée pour combler la différence.
<!-- @os:end -->

<!-- @os:linux -->
> **Remarque :** Les techniques de réglage fin présentées dans ce guide nécessitent une carte graphique dotée d'au moins **16 Go de mémoire GPU dédiée** et de **32 Go de mémoire vive système**.
> - Sous Linux, l'entraînement s'exécute entièrement dans la VRAM dédiée de la carte graphique.
> - Il ne bascule pas vers la mémoire GPU partagée (mémoire vive système) lorsque la VRAM est épuisée.
> - Les cartes disposant de moins de 16 Go de VRAM dédiée manqueront de mémoire pendant l'entraînement sous Linux, même si le système dispose de beaucoup de mémoire vive.
<!-- @os:end -->
<!-- @device:end -->

## Ce que vous apprendrez

- Comment configurer LLaMA Factory avec le logiciel AMD ROCm™
- Comment configurer les paramètres de réglage fin des LLM (en utilisant Qwen/Qwen3-4B-Instruct-2507 comme exemple)
- Comment exécuter le réglage fin avec LLaMA Factory
- Comment effectuer l'inférence avec le modèle affiné
- Comment exporter le modèle affiné

## Durée estimée

- Durée : L'exécution de ce guide prendra environ 60 minutes (selon la taille de votre modèle/jeu de données et la vitesse de votre réseau).
- Consultez la page [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) pour plus d'information.

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des logiciels préalables

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Créer un environnement virtuel

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous puis reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### Installation des dépendances de base

<!-- @require:pytorch,driver -->
 
### Installation des dépendances supplémentaires

> **Remarque** : Assurez-vous que la version de Python est 3.11, 3.12 ou 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### Installer LLaMA Factory

LLaMA Factory dépend de PyTorch. Vous devriez déjà l'avoir installé conformément aux exigences ci-dessus.

Téléchargez le code source à partir du [dépôt GitHub officiel de LLaMA Factory](https://github.com/hiyouga/LlamaFactory), et installez ses dépendances.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

Vérifiez si `llamafactory-cli` est exécutable.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Exemple de sortie :

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Maintenant que LLaMA Factory est installé avec succès, procédons au réglage fin.

## Utilisation de l'interface CLI de LLaMA Factory pour le réglage fin

Cette section explique comment préparer les jeux de données pour le réglage fin, configurer les paramètres LoRA/QLoRA, et exécuter un réglage fin LoRA.

### Préparation du jeu de données

LLaMA Factory prend en charge les jeux de données de réglage fin aux formats Alpaca et ShareGPT. Tous les jeux de données disponibles sont définis dans le fichier [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Si vous utilisez un jeu de données personnalisé, assurez-vous d'ajouter une description du jeu de données dans `dataset_info.json` et de spécifier son nom avant l'entraînement. Vous trouverez plus de détails dans leur documentation [ici](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Dans ce guide, nous utiliserons les jeux de données identity et alpaca_en_demo à titre d'exemple, et configurerons l'information relative aux jeux de données à l'étape suivante.
### Configuration des paramètres de réglage fin

LLaMA Factory prend en charge plusieurs schémas de réglage fin.

| Schémas de réglage fin | Exemples LLaMA Factory |
|-----------|------|
| Paramètres complets    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Réglage fin LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Réglage fin QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

Ces fichiers de configuration d'exemple ont défini les paramètres du modèle, les paramètres de méthode de réglage fin, les paramètres de jeu de données, les paramètres d'évaluation, et plus encore. Vous pouvez les configurer selon vos propres besoins. Dans ce guide, nous utiliserons [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Explication des paramètres clés :**
- `model_name_or_path` - Nom du modèle Hugging Face ou chemin d'accès local au fichier du modèle.
- `stage` - Étape d'entraînement. Options : rm (modélisation de récompense), pt (préentraînement), sft (réglage fin supervisé), PPO, DPO, KTO, ORPO.
- `do_train` - true pour l'entraînement, false pour l'évaluation
- `finetuning_type` - Méthode de réglage fin. Options : freeze, lora, full
- `lora_rank` - La dimensionnalité de la matrice de rang faible utilisée dans LoRA, valeurs typiques : 4, 6, 8, 16 (valeurs plus petites = moins de paramètres = réglage fin plus rapide; valeurs plus grandes = meilleure adaptation à la tâche mais utilisation de ressources plus élevée).
- `lora_target` - Modules cibles pour la méthode LoRA. Par défaut : all.
- `dataset` - Jeu(x) de données à utiliser. Utilisez « , » pour séparer plusieurs jeux de données
- `output_dir` - Chemin de sortie du réglage fin
- `logging_steps` - Intervalle de journalisation en étapes
- `save_steps` - Intervalle d'enregistrement des points de contrôle du modèle.
- `overwrite_output_dir` - Indique s'il faut autoriser l'écrasement du répertoire de sortie.
- `per_device_train_batch_size` - Taille du lot d'entraînement par appareil.
- `gradient_accumulation_steps` - Nombre d'étapes d'accumulation du gradient.
- `learning_rate` - Taux d'apprentissage
- `num_train_epochs` - Nombre d'époques d'entraînement
- `lr_scheduler_type` - Programme du taux d'apprentissage. Options : linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Ratio de préchauffage du taux d'apprentissage

<!-- @os:linux -->
Nous allons modifier la valeur par défaut de `lora_rank` afin d'exécuter le réglage fin sur les GPU AMD Ryzen™ et AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Nous allons mettre à jour la configuration de réglage fin LoRA par défaut pour une meilleure compatibilité avec les GPU AMD Ryzen™ et AMD Radeon™ :
- Réglez `lora_rank` de `8` à `6` pour réduire l'utilisation de la mémoire pendant le réglage fin.
- Utilisez `fp16` plutôt que `bf16` pour une compatibilité plus étendue avec les GPU AMD et une utilisation de mémoire moindre.
- Réglez `dataloader_num_workers` à `0` sous Windows afin d'éviter les erreurs de type « Can't pickle local object<> » causées par le chargement de données multiprocessus.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### Exécuter le réglage fin LLaMA Factory 

**llamafactory-cli** est l'outil officiel d'interface en ligne de commande (CLI) de LLaMA Factory, conçu pour simplifier les flux de travail de bout en bout des LLM (préparation des données → réglage fin → évaluation → déploiement) sans avoir à écrire de code complexe.

Pour l'entraînement/le réglage fin, **llamafactory-cli train** est la sous-commande principale de l'interface CLI de LLaMA Factory. Elle regroupe les flux de travail de réglage fin (prétraitement des données, ajustement des hyperparamètres, optimisation matérielle) en une seule commande CLI, prend en charge plusieurs paradigmes de réglage fin (LoRA/QLoRA/réglage fin complet) et est optimisée pour les GPU à ressources limitées (p. ex. QLoRA sur 16 Go de VRAM).

Vous pouvez exécuter le réglage fin LLaMA Factory à l'aide de la commande suivante, qui repose sur le fichier de configuration modifié du réglage fin Qwen3 LoRA.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

# Single-process dataset preprocessing to avoid Windows multiprocessing errors.
if (Select-String -Path $filePath -Pattern '^preprocessing_num_workers:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^preprocessing_num_workers:.*', 'preprocessing_num_workers: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "preprocessing_num_workers: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Après l'exécution du réglage fin du LLM, toutes les sorties générées sont stockées dans « output_dir », y compris les fichiers de points de contrôle du modèle, les fichiers de configuration et les métriques d'entraînement.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### Tester le modèle affiné 

**llamafactory-cli chat** est conçu pour le clavardage/l'inférence interactive avec les LLM (tant les modèles de base que les modèles affinés par LoRA). LLaMA Factory fournit la configuration d'exemple pour exécuter l'inférence des modèles affinés dans [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Vous pouvez également modifier cette configuration d'exemple pour changer les réglages, comme le moteur d'inférence.

Utilisez la commande suivante pour tester le modèle Qwen3 affiné :

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Un exemple de clavardage utilisant le modèle affiné est présenté ci-dessous :

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exporter le modèle affiné

Pour les cas d'utilisation en production, le modèle préentraîné et l'adaptateur LoRA doivent être fusionnés et exportés en un seul modèle. Ce modèle fusionné peut être utilisé comme un fichier de modèle Hugging Face normal. LLaMA Factory fournit les configurations d'exemple dans [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Utilisez la commande suivante pour exporter le modèle Qwen3 affiné :

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Le résultat de l'exportation du modèle affiné est présenté ci-dessous.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end -->
## Utilisation de l'interface graphique LLaMA Factory

`LLaMA-Factory` prend également en charge le réglage fin sans code des LLM grâce à une interface Web dans le navigateur.

Utilisez la commande suivante pour l'ouvrir :

```bash
llamafactory-cli webui
```
Le `LlamaFactory Web UI` offre une interface simplifiée pour gérer les flux de travail d'apprentissage automatique, y compris l'entraînement, l'évaluation, la prédiction, le clavardage et l'exportation de modèles. Voici une brève présentation de chaque onglet :

* **Train** : Cet onglet vous permet de sélectionner un modèle et un ensemble de données, de configurer les paramètres d'entraînement et de lancer le processus d'entraînement. Il est essentiel de comprendre les paramètres obligatoires et facultatifs afin d'optimiser la configuration de l'entraînement.
* **Evaluate & Predict** : Une fois l'entraînement terminé, vous pouvez évaluer la performance du modèle et effectuer des prédictions à l'aide de cet onglet. Il fournit un aperçu de la précision et de l'efficacité du modèle sur de nouvelles données.
* **Chat** : Une fois l'entraînement terminé, chargez le modèle dans l'onglet Chat pour interagir avec lui et observer les résultats de votre travail. Cette fonctionnalité permet une communication en temps réel avec le modèle entraîné.
* **Export** : Cet onglet facilite l'exportation des modèles entraînés en vue de leur déploiement ou d'une utilisation ultérieure. Vous pouvez enregistrer vos modèles dans divers formats adaptés à différentes applications.

Pour des directives détaillées, nous vous encourageons à consulter la documentation officielle sur le [dépôt GitHub de LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) et le [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). De plus, le [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) fournit des renseignements précieux sur l'interface et ses fonctionnalités.

## Prochaines étapes
- Essayez différents modèles, tels que `gpt-oss` et d'autres modèles à la fine pointe de la technologie.
- Expérimentez avec différents moteurs d'exécution sur le modèle ayant fait l'objet d'un réglage fin

Pour plus de documentation, veuillez visiter : https://llamafactory.readthedocs.io/en/latest/