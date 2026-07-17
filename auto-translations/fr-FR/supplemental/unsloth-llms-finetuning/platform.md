# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour exécuter ce playbook.

## Prérequis

PyTorch avec support ROCm est préinstallé sur la AMD Ryzen™ AI Halo Developer Platform. Pour tous les autres appareils, les utilisateurs doivent installer manuellement PyTorch avec support ROCm. Veuillez consulter la section correspondant à votre système d'exploitation :

### Windows

| Composant     | Version         | Remarques                             |
|---------------|-----------------|---------------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Préinstallé sur la AMD Ryzen AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |


### Linux

| Composant     | Version         | Remarques                             |
|---------------|-----------------|---------------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Préinstallé sur la AMD Ryzen AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |


## Modèles requis

Les modèles suivants sont testés et optimisés pour votre plateforme :

| Modèle | Paramètres | Taille | Emplacement de téléchargement |
|--------|------------|--------|-------------------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16 Go | Télécharger depuis HF

Les modèles seront automatiquement téléchargés dans le répertoire de cache Hugging Face : `~/.cache/huggingface/hub/`

Assurez-vous de disposer d'au moins **20 Go d'espace libre** pour le stockage des modèles.

## Exigences réseau

La configuration initiale nécessite un accès à Internet pour télécharger les modèles depuis Hugging Face. Une fois téléchargé, le playbook peut fonctionner hors ligne.

- Les premiers téléchargements de modèles peuvent prendre **5 à 10 minutes** selon la taille du modèle et la vitesse de connexion
- Les modèles sont mis en cache localement et n'ont pas besoin d'être téléchargés à nouveau