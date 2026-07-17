<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## 必要應用程式/框架
### Windows/Linux

ComfyUI 應依照 [ComfyUI 安裝指南](../../dependencies/comfyui.md) 中提供的說明預先安裝。

## 必要模型

### Windows/Linux

以下模型必須存放於 ComfyUI 安裝目錄內的 `models` 資料夾中。

| 模型類型 | 檔案名稱 | 大小 | 位置 | 下載 |
|------------|----------|------|----------|----------|
| 文字編碼器 | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [連結](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [連結](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| 擴散模型 | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [連結](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [連結](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


若要測試模型是否正確放置，請[透過導覽網站預覽 ComfyUI playbook](../../README.md#previewing-the-playbooks) 並依照指示操作。若在啟動 Z-Image Turbo 範本時未出現「找不到模型」頁面，則表示模型已正確放置。