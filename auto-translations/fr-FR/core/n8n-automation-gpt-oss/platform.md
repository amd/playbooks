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

## Prérequis

### Windows

| Composant | Version | Remarques |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Préinstallé et disponible dans le PATH sur l'AMD Ryzen™ AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |
| **Lemonade Server** | dernière version | S'exécute sur `http://localhost:13305/api/v1` |

### Linux

| Composant | Version | Remarques |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Préinstallé et disponible dans le PATH sur l'AMD Ryzen™ AI Halo Developer Platform ; doit être installé manuellement sur tous les autres appareils |
| **Lemonade Server** | dernière version | S'exécute sur `http://localhost:13305/api/v1` |


## Lemonade LLM

Le serveur Lemonade doit être en cours d'exécution avec le modèle approprié à l'appareil chargé (voir le README pour la commande `lemonade run` correspondant à votre appareil) :

| Appareil | Point de terminaison | Modèle |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |