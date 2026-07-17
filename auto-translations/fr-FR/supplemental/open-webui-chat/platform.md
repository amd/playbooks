<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuration de la plateforme

Ce document décrit la configuration de plateforme attendue pour exécuter ce playbook.

## Applications/Frameworks requis

### Windows/Linux
Lemonade doit être préinstallé depuis [ici](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (application web frontend)
- **Lemonade Server** (serveur de modèles backend)

> Ce playbook exécute **Lemonade** (serveur/application Lemonade) **nativement**. **Open WebUI** s'exécute en tant que **conteneur** sur Linux (via Podman) et en tant que **package Python** sur Windows. Le package PyPI `open-webui` ne prend en charge que Python ≤ 3.12, c'est pourquoi le conteneur Linux évite d'avoir à gérer des versions Python plus anciennes.

## Modèles (dans Lemonade)

Les modèles doivent être téléchargés dans l'**application Lemonade** (via le gestionnaire de modèles intégré) ou via les commandes de gestion de modèles de Lemonade (`lemonade pull <model_name>`). Ce playbook suppose que les modèles recommandés ci-dessous sont téléchargés et apparaissent dans le point de terminaison de la liste des modèles.

Vérifier la disponibilité des modèles :
- Ouvrir : `http://localhost:13305/api/v1/models`
- Les modèles téléchargés seront répertoriés sous `"data"`.

### Modèles recommandés

| Capacité | ID du modèle | Notes |
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

Si ces ports sont déjà utilisés sur votre système, modifiez-les lors du démarrage du ou des serveurs.