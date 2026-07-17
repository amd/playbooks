<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

このドキュメントでは、このプレイブックを実行するための想定されるプラットフォーム構成について説明します。

## Windows

### LM Studio インストール

LM Studio は事前にインストールされている必要があります：

| コンポーネント | バージョン | 場所 |
|-----------|---------|----------|
| **LM Studio (モデル + その他)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (プログラム)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (キャッシュ)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### モデルのダウンロード

以下のモデルは、LM Studio のモデルディレクトリ（`C:\Users\...\.lmstudio\models`）にあらかじめ存在している必要があります：

| デバイス | モデルタイプ | 量子化 | サイズ (GB) | 場所 |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio インストール

詳細については [lmstudio.md](../../dependencies/lmstudio.md) を参照してください。

### モデルのダウンロード

Windows と同様です。