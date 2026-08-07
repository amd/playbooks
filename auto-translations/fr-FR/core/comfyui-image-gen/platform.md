<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit les configurations de plateforme attendues pour l'exécution de ce playbook.

## Applications/Frameworks requis
### Windows/Linux

ComfyUI doit être préinstallé en suivant les instructions fournies dans [Guide d'installation de ComfyUI](../../dependencies/comfyui.md).

## Modèles requis

### Windows/Linux

Les modèles suivants doivent être présents dans le répertoire où ComfyUI est installé, à l'intérieur du dossier `models`.

| Type de modèle | Nom de fichier | Taille | Emplacement | Téléchargement |
|------------|----------|------|----------|----------|
| Encodeur de texte | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Lien](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Lien](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Modèle de diffusion | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Lien](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Lien](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Pour vérifier que les modèles sont correctement placés, [prévisualisez le playbook ComfyUI à l'aide du site web d'onboarding](../../README.md#previewing-the-playbooks) et suivez les instructions. Les modèles sont correctement placés si aucune page « Models not found » ne s'affiche lors du lancement du modèle Z-Image Turbo.