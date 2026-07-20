# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour exécuter ce playbook.

## Prérequis

PyTorch avec prise en charge ROCm est préinstallé sur l'AMD Ryzen™ AI Halo Developer Platform. Pour tous les autres appareils, les utilisateurs doivent installer manuellement PyTorch avec prise en charge ROCm. Veuillez vous référer à la section correspondant à votre système d'exploitation :

### Windows

| Composant     | Version         | Remarques                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ou plus récent    | Préinstallé sur l'AMD Ryzen AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |

### Linux

| Composant     | Version         | Remarques                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ou plus récent    | Préinstallé sur l'AMD Ryzen AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |

## Modèles requis

Les modèles suivants sont testés et optimisés pour votre plateforme :

| Modèle | Paramètres | Taille | Emplacement de téléchargement |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3 Md | ~10 Go | Préinstallé sur l'AMD Ryzen AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |

Les modèles seront automatiquement téléchargés dans le répertoire de cache Hugging Face :
- **Windows** : `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux** : `~/.cache/huggingface/hub/`

Assurez-vous de disposer d'au moins **20 Go d'espace libre** pour le stockage des modèles.

## Exigences réseau

La configuration initiale nécessite un accès Internet pour télécharger les modèles depuis Hugging Face. Une fois le téléchargement effectué, le playbook peut fonctionner hors ligne.

- Les premiers téléchargements de modèles peuvent prendre **5 à 10 minutes** selon la taille du modèle et la vitesse de connexion
- Les modèles sont mis en cache localement et n'ont pas besoin d'être retéléchargés