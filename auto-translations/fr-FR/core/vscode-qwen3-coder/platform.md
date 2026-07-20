<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour l'exécution de ce playbook.

## Windows

### Installation de LM Studio

LM Studio doit être préinstallé :

| Composant | Version | Emplacement |
|-----------|---------|----------|
| **LM Studio (Modèles + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programme)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Téléchargement du modèle

Les modèles suivants doivent déjà être présents dans le répertoire des modèles de LM Studio (`C:\Users\...\.lmstudio\models`) :

| Type de modèle | Quantification | Taille | Emplacement |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 Go | `models\lmstudio-community` |

---

## Linux

### Installation de LM Studio

Voir lmstudio.md (dans le dossier dependencies) pour plus de détails.

### Téléchargement du modèle

Identique à Windows.