<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme — IA locale Lemonade

Ce document décrit les logiciels préinstallés, les chemins des modèles et les conditions préalables propres à la plateforme présumées par ce guide.

## Logiciels préinstallés

| Logiciel | Version | Objectif |
|----------|---------|----------|
| Lemonade Server | Dernière version | Serveur LLM local doté d'une API compatible OpenAI |
| Python | 3.10–3.13 | Requis pour l'exemple du client Python OpenAI |

## Emplacement de stockage par défaut des modèles

Les modèles téléchargés au moyen de Lemonade sont stockés selon la spécification Hugging Face Hub :

| Plateforme | Chemin par défaut |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Pour modifier l'emplacement de stockage, définissez la variable d'environnement `HF_HOME`.

## Exigences matérielles

| Cible matérielle | Exigences |
|----------------|-------------|
| **CPU** | Tout processeur x86-64 moderne (AMD ou Intel) |
| **GPU (Vulkan)** | Tout GPU prenant en charge le pilote Vulkan |
| **GPU (ROCm)** | AMD Radeon série RX 7000/9000 ou série Radeon PRO W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processeur AMD Ryzen AI série 300, Windows 11 |

## Exigences réseau

- Connexion Internet requise pour le téléchargement initial du modèle (1 à 25 Go selon le modèle)
- Aucune connexion Internet requise une fois les modèles téléchargés