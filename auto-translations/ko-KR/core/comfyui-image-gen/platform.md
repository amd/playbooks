<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위해 예상되는 플랫폼 구성을 설명합니다.

## 필수 앱/프레임워크
### Windows/Linux

ComfyUI는 [ComfyUI 설치 가이드](../../dependencies/comfyui.md)에 제공된 안내에 따라 사전 설치되어 있어야 합니다.

## 필수 모델

### Windows/Linux

다음 모델들은 ComfyUI가 설치된 디렉터리 내의 `models` 폴더에 존재해야 합니다.

| Model Type | Filename | Size | Location | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


모델이 올바르게 배치되었는지 테스트하려면 [온보딩 웹사이트를 사용하여 ComfyUI 플레이북을 미리 보기](../../README.md#previewing-the-playbooks)하고 안내를 따르세요. Z-Image Turbo 템플릿을 실행할 때 "Models not found" 페이지가 표시되지 않으면 모델이 올바르게 배치된 것입니다.