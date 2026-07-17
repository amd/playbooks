<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuration de la plateforme — Lemonade Local AI

Ce document décrit les logiciels pré-installés, les chemins des modèles et les prérequis spécifiques à la plateforme supposés par ce playbook.

## Logiciels pré-installés

| Logiciel | Version | Objectif |
|----------|---------|---------|
| Lemonade Server | Dernière version | Serveur LLM local avec API compatible OpenAI |
| Python | 3.10–3.13 | Requis pour l'exemple de client Python OpenAI |

## Stockage des modèles par défaut

Les modèles téléchargés via Lemonade sont stockés selon la spécification Hugging Face Hub :

| Plateforme | Chemin par défaut |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Pour modifier l'emplacement de stockage, définissez la variable d'environnement `HF_HOME`.

## Configuration matérielle requise

| Cible matérielle | Exigences |
|----------------|-------------|
| **CPU** | Tout processeur x86-64 moderne (AMD ou Intel) |
| **GPU (Vulkan)** | Tout GPU avec prise en charge du pilote Vulkan |
| **GPU (ROCm)** | AMD Radeon RX séries 7000/9000 ou Radeon PRO W7000 ; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processeur AMD Ryzen AI 300, Windows 11 |

## Exigences réseau

- Connexion Internet requise pour le téléchargement initial du modèle (1 à 25 Go selon le modèle)
- Aucune connexion Internet requise une fois les modèles téléchargés