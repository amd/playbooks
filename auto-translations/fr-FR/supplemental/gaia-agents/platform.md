<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour exécuter ce playbook.

## Applications/frameworks requis

### Windows/Linux

GAIA doit être préinstallé en suivant les instructions fournies dans le [Guide d'installation de GAIA](../../dependencies/gaia.md).

Lemonade Server doit être préinstallé en suivant les instructions fournies dans le [Guide d'installation de Lemonade](../../dependencies/lemonade.md).

## Modèles requis

### Windows/Linux

Le Hardware Advisor Agent utilise **Qwen3-Coder-30B** pour le raisonnement de l'agent. Ce modèle est téléchargé automatiquement lors de `gaia init`. Aucun téléchargement manuel de modèle n'est requis.