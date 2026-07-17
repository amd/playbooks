<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム構成

このドキュメントでは、このプレイブックを実行するために必要なプラットフォーム構成について説明します。

## 必要なアプリ / フレームワーク

| コンポーネント       | 想定される構成                               | 備考                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | `venv` サポートを含む Python         | `kernel-env` の作成と有効化に使用                                     |
| ROCm Python SDK | ROCm 7.13 パッケージファミリー             | プレイブックの依存関係フローを通じてインストール                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`、HIP ランタイム、JIT コンパイル、および `CUDAExtension` に必要 |
| GPU ドライバー      | ROCm/HIP サポートを含む AMD GPU ドライバー | PyTorch が AMD GPU を検出する前に必要                               |

> 注意: AMD Ryzen™ AI Halo Developer Platform で実行している場合、AMD ROCm™ ソフトウェアと PyTorch はプリインストールされています。

## Linux の前提条件

以下のシステムパッケージが必要です:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` は `kernel-env` の作成に必要です。
* `build-essential`、`gcc`、および `g++` は C++ 拡張機能のウォークスルーに必要です。
* `amd-smi` は Linux の GPU 可視性/使用率チェックに使用されます。

C++ 拡張機能の例は、PyTorch の `CUDAExtension` パスを使用して `.cu` ファイルからネイティブ `.so` モジュールをビルドします。

## Windows の前提条件

Windows ランナーには以下が必要です:

* `python` を通じて利用可能な Python
* 最新版のインストール: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* **C++ によるデスクトップ開発**ワークロードを含む [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) または[それ以降のバージョン](https://visualstudio.microsoft.com/vs/community/)

Visual Studio C++ 環境は以下を提供する必要があります:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK のインクルードパスおよびライブラリパス

C++ 拡張機能の例は、PyTorch の `CUDAExtension` パスを使用して `.cu` ファイルからネイティブ `.pyd` モジュールをビルドします。