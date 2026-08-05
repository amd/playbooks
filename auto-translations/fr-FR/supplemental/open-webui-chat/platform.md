<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit la configuration de plateforme attendue pour exécuter ce playbook.

## Applications/frameworks requis

### Windows/Linux
Lemonade doit être préinstallé à partir d'[ici](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (application web frontend)
- **Lemonade Server** (serveur de modèles backend)

> Ce playbook exécute **Lemonade** (serveur/application Lemonade) **nativement**. **Open WebUI** s'exécute en tant que **conteneur** sur Linux (via Podman) et en tant que **package Python** sur Windows. Le package PyPI `open-webui` ne prend en charge que Python ≤ 3.12, c'est pourquoi le conteneur Linux permet d'éviter d'avoir à gérer des versions plus anciennes de Python.  

## Modèles (dans Lemonade)

Les modèles doivent être téléchargés au sein de l'**application Lemonade** (à l'aide du gestionnaire de modèles intégré) ou via les commandes de gestion des modèles de Lemonade (`lemonade pull <model_name>`). Ce playbook suppose que les modèles recommandés ci-dessous sont téléchargés et apparaissent dans le point de terminaison de la liste des modèles.

Vérifier la disponibilité des modèles :
- Ouvrir : `http://localhost:13305/api/v1/models`
- Les modèles téléchargés seront listés sous `"data"`.

### Modèles recommandés

| Capacité | ID du modèle | Remarques |
|---|----|-----|
| LLM (Entrée texte → Sortie texte) | `Qwen3-4B-Hybrid` (ou similaire) | Tout modèle LLM Lemonade pour le chat, la complétion de texte, le codage ou le raisonnement |
| VLM (Image → Texte) | `Qwen3.5-4B-GGUF` (ou tout modèle de la catégorie **Vision**) | Tout modèle multimodal/capable de vision pouvant prendre des images en entrée |
| Génération d'images (Texte → Image) | `SDXL-Turbo` (ou tout modèle de la catégorie **Image**) | Tout modèle Stable Diffusion générant des images à partir d'une invite textuelle |
| Audio (Parole → Texte) | `Whisper-Large-v3` (ou tout modèle de la catégorie **Audio**) | Tout modèle ASR convertissant l'audio en texte |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Ports utilisés

- **Lemonade Server :** `http://localhost:13305`
- **Open WebUI :** `http://localhost:8080`

Si ces ports sont déjà utilisés sur votre système, modifiez-les au démarrage du ou des serveurs.