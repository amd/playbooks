<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit la configuration de plateforme attendue pour exécuter ce playbook.

## Applications/cadriciels requis

### Windows/Linux
Lemonade devrait être préinstallé à partir d'[ici](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (application Web frontale)
- **Lemonade Server** (serveur de modèles dorsal)

> Ce playbook exécute **Lemonade** (serveur/application Lemonade) **nativement**. **Open WebUI** s'exécute en tant que **conteneur** sur Linux (via Podman) et en tant que **paquet Python** sur Windows. Le paquet PyPI `open-webui` ne prend en charge que Python ≤ 3.12, de sorte que le conteneur Linux évite d'avoir à gérer des versions plus anciennes de Python.  

## Modèles (dans Lemonade)

Les modèles doivent être téléchargés dans l'**application Lemonade** (à l'aide du gestionnaire de modèles intégré) ou par l'intermédiaire des commandes de gestion de modèles de Lemonade (`lemonade pull <model_name>`). Ce playbook suppose que les modèles recommandés ci-dessous sont téléchargés et figurent dans le point de terminaison de la liste des modèles.

Vérifier la disponibilité des modèles :
- Ouvrir : `http://localhost:13305/api/v1/models`
- Les modèles téléchargés seront répertoriés sous `"data"`.

### Modèles recommandés

| Capacité | ID du modèle | Remarques |
|---|----|-----|
| LLM (entrée texte → sortie texte) | `Qwen3-4B-Hybrid` (ou similaire) | Tout modèle LLM Lemonade pour le clavardage, la complétion de texte, le codage ou le raisonnement |
| VLM (image → texte) | `Qwen3.5-4B-GGUF` (ou tout modèle de la catégorie **Vision**) | Tout modèle multimodal/à capacité visuelle pouvant prendre des images en entrée |
| Génération d'images (texte → image) | `SDXL-Turbo` (ou tout modèle de la catégorie **Image**) | Tout modèle Stable Diffusion qui génère des images à partir d'une invite textuelle |
| Audio (parole → texte) | `Whisper-Large-v3` (ou tout modèle de la catégorie **Audio**) | Tout modèle de RAP (reconnaissance automatique de la parole) qui convertit l'audio en texte |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Ports utilisés

- **Lemonade Server :** `http://localhost:13305`
- **Open WebUI :** `http://localhost:8080`

Si ces ports sont déjà utilisés sur votre système, modifiez-les au démarrage du ou des serveurs.