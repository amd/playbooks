<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Aplicativos/Frameworks Necessários
### Windows/Linux

O ComfyUI deve ser pré-instalado usando as instruções fornecidas no [Guia de Instalação do ComfyUI](../../dependencies/comfyui.md).

## Modelos Necessários

### Windows/Linux

Os seguintes modelos devem estar presentes no diretório onde o ComfyUI está instalado, dentro da pasta `models`.

| Tipo de Modelo | Nome do Arquivo | Tamanho | Localização | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Para testar se os modelos foram colocados corretamente, [visualize o playbook do ComfyUI usando o site de onboarding](../../README.md#previewing-the-playbooks) e siga as instruções. Os modelos estão colocados corretamente se nenhuma página "Models not found" aparecer ao iniciar o template Z-Image Turbo.