<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# プラットフォーム構成

このドキュメントでは、このプレイブックを実行するために想定されるプラットフォーム構成について説明します。

## 必要なアプリ / フレームワーク

| コンポーネント       | 想定される構成               | 注記                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | `venv` をサポートする Python         | `kernel-env` の作成とアクティベートに使用                                     |
| ROCm Python SDK | ROCm 7.13 パッケージファミリー             | プレイブックの依存関係フローを通じてインストール                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`、HIP ランタイム、JIT コンパイル、`CUDAExtension` に必須 |
| GPU ドライバー      | ROCm/HIP をサポートする AMD GPU ドライバー | PyTorch が AMD GPU を検出する前に必須                                               |

> 注: AMD Ryzen™ AI Halo Developer Platform で実行している場合、AMD ROCm™ ソフトウェアと PyTorch はプリインストールされています。

## Linux の前提条件

以下のシステムパッケージが必要です:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `kernel-env` を作成するために `python3-venv` が必要です。
* C++ 拡張のウォークスルーには `build-essential`、`gcc`、`g++` が必要です。
* `amd-smi` は Linux の GPU の可視性/使用率の確認に使用されます。

C++ 拡張の例では、PyTorch の `CUDAExtension` パスを使用して `.cu` ファイルからネイティブの `.so` モジュールをビルドします。

## Windows の前提条件

Windows ランナーには以下が必要です:

* `python` から利用可能な Python
* 最新版をインストール: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* **Desktop development with C++** ワークロードを含む [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) または [それ以降](https://visualstudio.microsoft.com/vs/community/)

Visual Studio C++ 環境は以下を提供する必要があります:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK のインクルードおよびライブラリのパス

C++ 拡張の例では、PyTorch の `CUDAExtension` パスを使用して `.cu` ファイルからネイティブの `.pyd` モジュールをビルドします。