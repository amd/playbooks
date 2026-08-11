<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour l'exécution de ce playbook.

## Prérequis

PyTorch avec la prise en charge de ROCm est préinstallé sur la plateforme AMD Ryzen™ AI Halo Developer Platform. Pour tous les autres appareils, les utilisateurs doivent installer manuellement PyTorch avec la prise en charge de ROCm. Veuillez consulter la section pertinente pour votre système d'exploitation :

### Windows

| Composant     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ou plus récent    | Préinstallé sur la plateforme AMD Ryzen AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |

### Linux

| Composant     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ou plus récent    | Préinstallé sur la plateforme AMD Ryzen AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |

## Modèles requis

Les modèles suivants sont testés et optimisés pour votre plateforme :

| Modèle | Paramètres | Taille | Emplacement de téléchargement |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3 G | ~10 Go | Préinstallé sur la plateforme AMD Ryzen AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |

Les modèles seront téléchargés automatiquement dans le répertoire de cache de Hugging Face :
- **Windows** : `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux** : `~/.cache/huggingface/hub/`

Assurez-vous de disposer d'au moins **20 Go d'espace libre** pour le stockage des modèles.

## Exigences réseau

La configuration initiale nécessite un accès Internet pour télécharger les modèles depuis Hugging Face. Une fois le téléchargement terminé, le playbook peut fonctionner hors ligne.

- Les premiers téléchargements de modèles peuvent prendre de **5 à 10 minutes**, selon la taille du modèle et la vitesse de la connexion
- Les modèles sont mis en cache localement et n'ont pas besoin d'être téléchargés de nouveau