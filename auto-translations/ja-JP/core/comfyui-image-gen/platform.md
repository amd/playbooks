<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム設定

このドキュメントでは、このプレイブックを実行するために必要なプラットフォーム設定について説明します。

## 必要なアプリ/フレームワーク
### Windows/Linux

ComfyUI は、[ComfyUI インストールガイド](../../dependencies/comfyui.md)に記載されている手順に従って事前にインストールされている必要があります。

## 必要なモデル

### Windows/Linux

以下のモデルは、ComfyUI がインストールされているディレクトリ内の `models` フォルダに配置されている必要があります。

| モデルタイプ | ファイル名 | サイズ | 場所 | ダウンロード |
|------------|----------|------|----------|----------|
| テキストエンコーダー | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [リンク](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [リンク](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| 拡散モデル | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [リンク](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [リンク](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


モデルが正しく配置されているかどうかを確認するには、[オンボーディングウェブサイトで ComfyUI プレイブックをプレビュー](../../README.md#previewing-the-playbooks)し、手順に従ってください。Z-Image Turbo テンプレートを起動したときに「Models not found」ページが表示されなければ、モデルは正しく配置されています。