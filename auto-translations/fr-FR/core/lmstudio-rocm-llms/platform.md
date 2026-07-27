<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement à partir de l'anglais et n'a pas été relue par un humain. Elle peut contenir des erreurs, et certaines étapes, commandes, téléchargements ou disponibilités de produits peuvent différer selon votre langue ou région. Si quelque chose semble incorrect, veuillez considérer le playbook original en anglais comme la source de référence.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour exécuter ce playbook.

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

| Appareil | Type de modèle | Quantification | Taille (Go) | Emplacement |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Installation de LM Studio

Voir [lmstudio.md](../../dependencies/lmstudio.md) pour plus de détails.

### Téléchargement du modèle

Identique à Windows.