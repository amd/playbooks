<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour l'exécution de ce guide pratique.

## Applications/cadriciels requis

### Windows/Linux

GAIA doit être préinstallé en suivant les instructions fournies dans le [Guide d'installation de GAIA](../../dependencies/gaia.md).

Lemonade Server doit être préinstallé en suivant les instructions fournies dans le [Guide d'installation de Lemonade](../../dependencies/lemonade.md).

## Modèles requis

### Windows/Linux

L'agent Hardware Advisor utilise **Qwen3-Coder-30B** pour le raisonnement de l'agent. Ce modèle est téléchargé automatiquement pendant `gaia init`. Aucun téléchargement manuel de modèle n'est requis.