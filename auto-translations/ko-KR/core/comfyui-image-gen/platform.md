<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위한 예상 플랫폼 구성을 설명합니다.

## 필수 앱/프레임워크
### Windows/Linux

ComfyUI는 [ComfyUI 설치 가이드](../../dependencies/comfyui.md)에 제공된 지침에 따라 사전 설치되어 있어야 합니다.

## 필수 모델

### Windows/Linux

다음 모델들은 ComfyUI가 설치된 디렉터리 내 `models` 폴더에 있어야 합니다.

| 모델 유형 | 파일명 | 크기 | 위치 | 다운로드 |
|------------|----------|------|----------|----------|
| 텍스트 인코더 | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [링크](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [링크](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| 디퓨전 모델 | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [링크](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [링크](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


모델이 올바르게 배치되었는지 테스트하려면 [온보딩 웹사이트에서 ComfyUI 플레이북을 미리 보고](../../README.md#previewing-the-playbooks) 지침을 따르십시오. Z-Image Turbo 템플릿을 실행할 때 "모델을 찾을 수 없음" 페이지가 표시되지 않으면 모델이 올바르게 배치된 것입니다.