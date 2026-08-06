<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

## Aperçu général

Un ajustement fin (fine-tuning) efficace est essentiel pour adapter les grands modèles de langage (LLM) à des tâches spécifiques. LLaMA Factory est une plateforme open source et conviviale qui simplifie l'entraînement et l'ajustement fin des grands modèles de langage et des modèles multimodaux. Elle permet aux utilisateurs de personnaliser localement des centaines de modèles pré-entraînés avec un minimum de code.

Ce playbook vous apprend à ajuster finement des LLM à l'aide de LLaMA Factory sur votre matériel AMD local.

<!-- @device:stx,krk -->
> **Remarque :** Les techniques d'ajustement fin de ce playbook nécessitent au moins **32 Go de RAM système**, dont au moins **16 Go doivent être disponibles pour le GPU** (ces 16 Go font partie des 32 Go, et ne s'y ajoutent pas).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Remarque :** Les techniques d'ajustement fin de ce playbook nécessitent au moins **16 Go de mémoire GPU totale** et **32 Go de RAM système**.
> - Sous Windows, la mémoire GPU totale combine la VRAM dédiée de la carte graphique avec la mémoire GPU partagée (empruntée à la RAM système).
> - Ainsi, les cartes disposant de moins de 16 Go de VRAM dédiée peuvent tout de même exécuter ce playbook en utilisant la mémoire GPU partagée pour combler la différence.
<!-- @os:end -->

<!-- @os:linux -->
> **Remarque :** Les techniques d'ajustement fin de ce playbook nécessitent une carte graphique disposant d'au moins **16 Go de mémoire GPU dédiée** et **32 Go de RAM système**.
> - Sous Linux, l'entraînement s'exécute entièrement dans la VRAM dédiée de la carte graphique.
> - Il n'y a pas de repli sur la mémoire GPU partagée (RAM système) lorsque la VRAM est épuisée.
> - Les cartes disposant de moins de 16 Go de VRAM dédiée manqueront de mémoire pendant l'entraînement sous Linux, même si le système dispose de beaucoup de RAM.
<!-- @os:end -->
<!-- @device:end -->

## Ce que vous allez apprendre

- Comment configurer LLaMA Factory avec le logiciel AMD ROCm™
- Comment configurer les paramètres d'ajustement fin des LLM (en utilisant Qwen/Qwen3-4B-Instruct-2507 comme exemple)
- Comment exécuter l'ajustement fin avec LLaMA Factory
- Comment exécuter l'inférence avec le modèle ajusté finement
- Comment exporter le modèle ajusté finement 

## Durée estimée

- Durée : L'exécution de ce playbook prendra environ 60 minutes (selon la taille de votre modèle/jeu de données et la vitesse de votre réseau).
- Consultez le [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) pour plus d'informations.

## Configuration de la mémoire

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Vérification des mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels

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
<!-- @test:id=create-venv timeout=120 -->
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
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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

Téléchargez le code source depuis le [dépôt GitHub officiel de LLaMA Factory](https://github.com/hiyouga/LlamaFactory), et installez ses dépendances.

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

Après avoir installé LLaMA Factory avec succès, passons à l'exécution de l'ajustement fin.

## Utilisation de la CLI LLaMA Factory pour l'ajustement fin 

Cette section couvre la préparation des jeux de données d'ajustement fin, la configuration des paramètres LoRA/QLoRA, et l'exécution de l'ajustement fin LoRA.

### Préparation du jeu de données

LLaMA Factory prend en charge les jeux de données d'ajustement fin au format Alpaca et au format ShareGPT. Tous les jeux de données disponibles sont définis dans le fichier [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Si vous utilisez un jeu de données personnalisé, veillez à ajouter une description du jeu de données dans `dataset_info.json` et à spécifier le nom du jeu de données avant l'entraînement. Les détails sont disponibles dans leur documentation [ici](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Dans ce playbook, nous utiliserons les jeux de données identity et alpaca_en_demo à titre d'exemple, et nous configurerons les informations du jeu de données à l'étape suivante.
### Configuration des paramètres de fine-tuning

LLaMA Factory prend en charge plusieurs schémas de fine-tuning.

| Schémas de fine-tuning | Exemples LLaMA Factory |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fine-tuning LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fine-tuning QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Ces fichiers de configuration d'exemple ont spécifié les paramètres du modèle, les paramètres de la méthode de fine-tuning, les paramètres du jeu de données, les paramètres d'évaluation, et plus encore. Vous pouvez les configurer selon vos propres besoins. Dans ce playbook, nous utiliserons [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Explication des paramètres clés :**
- `model_name_or_path` - Nom du modèle Hugging Face ou chemin du fichier de modèle local.
- `stage` - Étape d'entraînement. Options : rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true pour l'entraînement, false pour l'évaluation
- `finetuning_type` - Méthode de fine-tuning. Options : freeze, lora, full
- `lora_rank` - La dimensionnalité de la matrice de rang faible utilisée dans LoRA, valeurs typiques : 4, 6, 8, 16 (valeurs plus petites = moins de paramètres = fine-tuning plus rapide ; valeurs plus grandes = meilleure adaptation à la tâche mais consommation de ressources plus élevée).
- `lora_target` - Modules cibles pour la méthode LoRA. Par défaut : all.
- `dataset` - Jeu(x) de données à utiliser. Utilisez « , » pour séparer plusieurs jeux de données
- `output_dir` - Chemin de sortie du fine-tuning
- `logging_steps` - Intervalle de journalisation en étapes
- `save_steps` - Intervalle de sauvegarde du point de contrôle du modèle.
- `overwrite_output_dir` - Indique si l'écrasement du répertoire de sortie est autorisé.
- `per_device_train_batch_size` - Taille du lot d'entraînement par appareil.
- `gradient_accumulation_steps` - Nombre d'étapes d'accumulation de gradient.
- `learning_rate` - Taux d'apprentissage
- `num_train_epochs` - Nombre d'époques d'entraînement
- `lr_scheduler_type` - Planification du taux d'apprentissage. Options : linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Ratio de préchauffage du taux d'apprentissage

<!-- @os:linux -->
Nous allons modifier la valeur par défaut de `lora_rank` pour exécuter le fine-tuning sur les GPU AMD Ryzen™ et AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Nous allons mettre à jour la configuration de fine-tuning LoRA par défaut pour une meilleure compatibilité avec les GPU AMD Ryzen™ et AMD Radeon™ :
- Modifier `lora_rank` de `8` à `6` pour réduire l'utilisation de la mémoire pendant le fine-tuning.
- Utiliser `fp16` au lieu de `bf16` pour une compatibilité plus large avec les GPU AMD et une utilisation mémoire réduite.
- Définir `dataloader_num_workers` à `0` sous Windows pour éviter les erreurs `"Can't pickle local object<>"` causées par le chargement de données multiprocessus.

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

### Exécuter le fine-tuning LLaMA Factory 

**llamafactory-cli** est l'outil officiel d'interface en ligne de commande (CLI) pour LLaMA Factory, conçu pour simplifier les workflows LLM de bout en bout (préparation des données → fine-tuning → évaluation → déploiement) sans écrire de code complexe.

Pour l'entraînement/le fine-tuning, **llamafactory-cli train** est la sous-commande principale de la CLI LLaMA Factory. Elle résume les workflows de fine-tuning (prétraitement des données, réglage des hyperparamètres, optimisation matérielle) en une seule commande CLI, prend en charge plusieurs paradigmes de fine-tuning (LoRA/QLoRA/Full Fine-Tuning) et est optimisée pour les GPU à ressources limitées (par exemple, QLoRA sur 16 Go de VRAM).

Vous pouvez exécuter le fine-tuning LLaMA Factory à l'aide de la commande suivante, basée sur le fichier de configuration modifié du fine-tuning Qwen3 LoRA.

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

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Après avoir exécuté le fine-tuning du LLM, toutes les sorties générées sont stockées dans « output_dir », y compris les fichiers de point de contrôle du modèle, les fichiers de configuration et les métriques d'entraînement.

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

### Tester le modèle fine-tuné 

**llamafactory-cli chat** est conçu pour le chat/inférence interactif avec les LLM (modèles de base et modèles fine-tunés avec LoRA). LLaMA Factory fournit la configuration d'exemple pour exécuter l'inférence des modèles fine-tunés dans [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Vous pouvez également modifier cette configuration d'exemple pour changer les paramètres, comme le backend d'inférence.

Utilisez la commande suivante pour tester le modèle Qwen3 fine-tuné :

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Un exemple de chat utilisant le modèle fine-tuné est illustré ci-dessous :

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exporter le modèle fine-tuné

Pour les cas d'utilisation en production, le modèle pré-entraîné et l'adaptateur LoRA doivent être fusionnés et exportés en un seul modèle. Ce modèle fusionné peut être utilisé comme un fichier de modèle Hugging Face normal. LLaMA Factory fournit les configurations d'exemple dans [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Utilisez la commande suivante pour exporter le modèle Qwen3 fine-tuné :

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Le résultat de l'exportation du modèle fine-tuné est illustré ci-dessous.

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

`LLaMA-Factory` prend également en charge le fine-tuning sans code des LLM via une interface web dans le navigateur.

Utilisez la commande suivante pour l'ouvrir :

```bash
llamafactory-cli webui
```
La `LlamaFactory Web UI` offre une interface simplifiée pour gérer les workflows d'apprentissage automatique, notamment l'entraînement, l'évaluation, la prédiction, le chat et l'export de modèles. Voici une brève présentation de chaque onglet :

* **Train** : Cet onglet vous permet de sélectionner un modèle et un jeu de données, de configurer les paramètres d'entraînement et de lancer le processus d'entraînement. Il est essentiel de comprendre les paramètres obligatoires et optionnels pour optimiser la configuration de l'entraînement.
* **Evaluate & Predict** : Après l'entraînement, vous pouvez évaluer les performances du modèle et effectuer des prédictions à l'aide de cet onglet. Il fournit des informations sur la précision et l'efficacité du modèle sur de nouvelles données.
* **Chat** : Une fois l'entraînement terminé, chargez le modèle dans l'onglet Chat pour interagir avec lui et observer les résultats de votre travail. Cette fonctionnalité permet une communication en temps réel avec le modèle entraîné.
* **Export** : Cet onglet facilite l'export des modèles entraînés en vue de leur déploiement ou d'une utilisation ultérieure. Vous pouvez enregistrer vos modèles dans divers formats adaptés à différentes applications.

Pour des instructions détaillées, nous vous encourageons à consulter la documentation officielle sur le [dépôt GitHub de LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) et le [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). De plus, le [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) fournit des informations précieuses sur l'interface et ses fonctionnalités.

## Étapes suivantes
- Essayez différents modèles tels que `gpt-oss` et d'autres modèles de pointe.
- Expérimentez avec différents backends sur le modèle affiné

Pour plus de documentation, veuillez consulter : https://llamafactory.readthedocs.io/en/latest/