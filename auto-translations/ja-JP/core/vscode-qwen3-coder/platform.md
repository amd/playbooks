<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# プラットフォーム構成

このドキュメントでは、本プレイブックを実行するために想定されるプラットフォーム構成について説明します。

## Windows

### LM Studio のインストール

LM Studio は事前にインストールされている必要があります。

| コンポーネント | バージョン | 場所 |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### モデルのダウンロード

以下のモデルが、LM Studio のモデルディレクトリ(`C:\Users\...\.lmstudio\models`)にすでに存在している必要があります。

| モデルタイプ | 量子化 | サイズ | 場所 |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio のインストール

詳細については、lmstudio.md(dependencies フォルダ内)を参照してください。

### モデルのダウンロード

Windows と同様です。