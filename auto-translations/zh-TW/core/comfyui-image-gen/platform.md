<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台設定

本文件說明執行此 playbook 所需的平台設定。

## 所需應用程式/框架
### Windows/Linux

應依照 [ComfyUI 安裝指南](../../dependencies/comfyui.md) 中提供的說明預先安裝 ComfyUI。

## 所需模型

### Windows/Linux

下列模型必須存在於安裝 ComfyUI 的目錄中的 `models` 資料夾內。

| 模型類型 | 檔案名稱 | 大小 | 位置 | 下載 |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [連結](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [連結](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [連結](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [連結](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


若要測試模型是否已正確放置，請[使用 onboarding 網站預覽 ComfyUI playbook](../../README.md#previewing-the-playbooks) 並依照指示操作。若在啟動 Z-Image Turbo 範本時未出現「Models not found」頁面，則表示模型已正確放置。