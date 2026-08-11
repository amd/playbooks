<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour exécuter ce playbook.

## Conditions préalables

PyTorch avec prise en charge de ROCm est préinstallé sur l'AMD Ryzen™ AI Halo Developer Platform. Pour tous les autres appareils, les utilisateurs doivent installer manuellement PyTorch avec prise en charge de ROCm. Veuillez consulter la section correspondant à votre système d'exploitation :

### Windows

| Composant     | Version         | Remarques                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ou plus récent    | Préinstallé sur l'AMD Ryzen AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |

### Linux

| Composant     | Version         | Remarques                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ou plus récent    | Préinstallé sur l'AMD Ryzen AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |

## Modèles requis

Les modèles suivants sont testés et optimisés pour votre plateforme :

| Modèle | Paramètres | Taille | Emplacement de téléchargement |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40 Go | Préinstallé sur l'AMD Ryzen AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |

Les modèles seront automatiquement téléchargés dans le répertoire de cache Hugging Face :
- **Windows** : `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux** : `~/.cache/huggingface/hub/`

Assurez-vous de disposer d'au moins **50 Go d'espace libre** pour le stockage des modèles.

## Exigences réseau

La configuration initiale nécessite un accès Internet pour télécharger les modèles depuis Hugging Face. Après le téléchargement, le playbook peut fonctionner hors ligne.

- Les premiers téléchargements de modèles peuvent prendre de **5 à 10 minutes**, selon la taille du modèle et la vitesse de connexion
- Les modèles sont mis en cache localement et n'ont pas besoin d'être téléchargés de nouveau