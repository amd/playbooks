<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme — Lemonade Local AI

Ce document décrit les logiciels préinstallés, les chemins d'accès aux modèles et les prérequis spécifiques à la plateforme supposés par ce playbook.

## Logiciels préinstallés

| Logiciel | Version | Objectif |
|----------|---------|----------|
| Lemonade Server | Dernière version | Serveur LLM local avec API compatible OpenAI |
| Python | 3.10–3.13 | Requis pour l'exemple du client Python OpenAI |

## Emplacement de stockage des modèles par défaut

Les modèles téléchargés via Lemonade sont stockés selon la spécification Hugging Face Hub :

| Plateforme | Chemin par défaut |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Pour modifier l'emplacement de stockage, définissez la variable d'environnement `HF_HOME`.

## Configuration matérielle requise

| Cible matérielle | Configuration requise |
|----------------|-------------|
| **CPU** | Tout processeur x86-64 moderne (AMD ou Intel) |
| **GPU (Vulkan)** | Tout GPU prenant en charge le pilote Vulkan |
| **GPU (ROCm)** | AMD Radeon RX série 7000/9000 ou Radeon PRO série W7000 ; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processeur AMD Ryzen AI série 300, Windows 11 |

## Exigences réseau

- Connexion Internet requise pour le téléchargement initial du modèle (1 à 25 Go selon le modèle)
- Aucune connexion Internet requise une fois les modèles téléchargés