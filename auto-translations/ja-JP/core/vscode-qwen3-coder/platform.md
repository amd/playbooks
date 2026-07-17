<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム設定

このドキュメントでは、このプレイブックを実行するための想定プラットフォーム設定について説明します。

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

| モデルタイプ | 量子化 | サイズ | 場所 |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio インストール

詳細については、lmstudio.md（dependencies フォルダー内）を参照してください。

### モデルのダウンロード

Windows と同様です。