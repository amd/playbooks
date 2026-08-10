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

### Windows

| Composant | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Préinstallé et accessible dans le PATH sur la plateforme AMD Ryzen™ AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |
| **Lemonade Server** | dernière version | En cours d'exécution à `http://localhost:13305/api/v1` |

### Linux

| Composant | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Préinstallé et accessible dans le PATH sur la plateforme AMD Ryzen™ AI Halo Developer Platform; doit être installé manuellement sur tous les autres appareils |
| **Lemonade Server** | dernière version | En cours d'exécution à `http://localhost:13305/api/v1` |


## LLM Lemonade

Le serveur Lemonade doit être en cours d'exécution avec le modèle approprié à l'appareil chargé (voir le README pour la commande `lemonade run` propre à votre appareil) :

| Appareil | Point de terminaison | Modèle |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |