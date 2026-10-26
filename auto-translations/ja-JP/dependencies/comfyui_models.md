<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI モデル

<!-- @device:halo_box -->
> **注:** モデルがすでに ComfyUI で利用可能な場合は、このセクションをスキップできます。そうでない場合は、以下の手順に従ってダウンロードしてください。
<!-- @device:end -->

以前に事前ダウンロード済みの ComfyUI モデルを削除した場合、または初めてダウンロードする場合は、モデルが見つからないことが検出された際に表示される各モデルの `Download` ボタンを押すだけです。
モデルファイルを正しい場所に手動で配置する必要がある場合があります。

<!-- @device:halo_box -->
<!-- @os:linux -->
> **注:** AMD Ryzen™ AI Halo では、ComfyUI はプリビルドされたコンテナ内で実行されます。手動でダウンロードしたモデルファイルは、コンテナ化された ComfyUI が見つけられるように、`~/.local/share/ComfyUI/models` 配下（対応する `diffusion_models`、`text_encoders`、または `vae` サブフォルダー内）に配置してください。
<!-- @os:end -->
<!-- @device:end -->

<p align="center">
  <img src="/api/dependencies/assets/comfy_download.png" alt="ComfyUI Download Models" width="600"/>