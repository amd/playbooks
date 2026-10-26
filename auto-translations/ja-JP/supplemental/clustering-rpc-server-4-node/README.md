<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# RPCを使用した4台のRyzen™ AI Haloのクラスタリング

## 概要

お使いのRyzen™ AI Haloは、すでにローカルで大規模言語モデルを実行する能力を備えています。クラスタリングはこれをさらに一歩進め、複数のシステムのGPUメモリをローカルネットワーク経由で結合することで、より強力な推論能力、優れたコード生成能力、そしてより深い多言語理解能力を持つ、さらに大規模なモデルへのアクセスを可能にします。これらはすべて、完全にご自身のハードウェア上で実現されます。

このプレイブックでは、llama.cppのRPCエンジンを使用して4台のRyzen AI Haloシステムをクラスタリングし、大規模なmixture-of-expertsモデルであるKimi K2.6を、AMD ROCm™アクセラレーションを活用しながら4台すべてのマシンにわたって実行する方法を解説します。

## 学習内容

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmおよびRPCサポートを備えたllama.cppのインストール
- RPCワーカーの構成と4ノードにわたる分散推論の起動
- 4台のネットワーク接続されたRyzen AI Haloシステムにわたる1Tパラメータモデルの実行

## メモリ構成の設定

> **注**: このステップは4台すべてのマシン（Machine 1からMachine 4まで）で完了させてください。

<!-- @device:halo_box -->
<!-- @os:windows -->
> **128 GB前後またはそれ以上のモデルを実行する場合:** Windowsを実行しているAMD Ryzen™ AI Max 400シリーズ（Gorgon Halo）システムでは、128 GBのメモリに近い、またはそれを超えるモデルを実行する場合、エラーなく実行するために追加の構成が必要です。モデルを読み込む前に、[AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines)に従ってください。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windowsでは、より高いメモリを必要とする大規模なモデルを実行するために、AMD Variable Graphics Memory（iGPU VRAM）の割り当てを使用する必要があります。

これは、AMD Software: Adrenalin Editionコントロールパネルを開き、`Performance > Tuning > AMD Variable Graphics Memory`に移動することで設定できます。値を**96 GB**に設定してください。変更を有効にするためにシステムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順でカーネルのTranslation Table Manager（TTM）ページ設定を変更することで増やすことができます。AMDは、BIOSで最小専用VRAMを設定することを推奨します（0.5 GB）。

* pipxユーティリティをインストールし、pipxでインストールされたwheelのパスをシステムの検索パスに追加します。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPIからamd-debug-toolsのwheelをインストールします。
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttmツールを実行して、共有メモリの現在の設定を確認します。
  ```bash
  amd-ttm
  ```

* 共有メモリ設定を**120 GB**に再構成します。
  ```bash
  amd-ttm --set 120
  ```

* 変更を有効にするためにシステムを再起動します。


<!-- @os:end -->
<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->
## 前提条件

### ハードウェア

このプレイブックには、4台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットがスイッチに直接接続されたスター型トポロジーで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | クラスターを構成する計算ノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo間の通信を可能にする中央スイッチ（最低4ポート） |
| イーサネットケーブル | 4 | 各Haloユニットをスイッチに接続（Cat 7以上を推奨） |

> **注**: 4台のRyzen AI Haloユニットを接続するには、4つのイーサネットスイッチポートが必要です。Haloユニットの1台ではなく別のクライアントマシンからモデルにアクセスする場合は、5つ目のポートが必要です。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)（**Desktop Development with C++**ワークロードを含む）
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: このステップは4台すべてのマシン（Machine 1からMachine 4まで）で完了させてください。

Cat 7（以上）のケーブルを使用して、各Ryzen AI Haloユニットをイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの特定

各マシンで、そのネットワークインターフェースの名前を特定し、書き留めておいてください（以降は`IFNAME`として参照されます）。以下を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これによりインターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認し、リンクがアクティブでフルスピードで動作していることを確認します。

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>`を[1. ネットワークインターフェースの特定](#1-ネットワークインターフェースの特定)の出力インターフェース名に置き換えてください

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にしてリンク速度を手動で設定する必要があります。お使いのスイッチのドキュメントを参照してください。

<!-- @os:end -->

<!-- @os:windows -->
### ネットワークリンク速度の確認

各マシンで、ネットワークインターフェースのリンク速度を確認します:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

イーサネットインターフェースは`Up`状態で、`10 Gbps`で動作しているはずです:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注**: 速度が`10 Gbps`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にしてリンク速度を手動で設定する必要があります。お使いのスイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注**: このステップは4台すべてのマシン（Machine 1からMachine 4まで）で完了させてください。

2つのインストールオプションが利用可能です:

- [オプション1: Lemonade SDK（推奨）](#option-1-lemonade-sdk-recommended) - ビルド済みバイナリ、最速のセットアップ
- [オプション2: 手動ソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御したソースからのビルド
### オプション1: Lemonade SDK（推奨）

Lemonade SDKは、AMD ROCm 7アクセラレーションを備えたllama.cppのナイトリービルドを提供しており、gfx1151（Strix Halo / Ryzen AI Max+ 395）やその他の最新のRadeonアーキテクチャをターゲットとしています。

<!-- @os:windows -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新のリリースページに移動し、お使いのプラットフォームとGPUターゲットに合ったアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip`という名前のファイルをダウンロードします（`xxxx`はビルド番号です）。

#### ステップ2: バイナリの展開

ダウンロードしたアーカイブを解凍します。

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、Ryzen AI Haloシステム向けに事前コンパイルされたROCm対応のビルドである`llama-cli.exe`、`llama-server.exe`、`ggml-rpc-server.exe`が含まれています。

#### ステップ3: GPU検出の確認

```bash
.\llama-cli.exe --list-devices
```

期待される出力:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新のリリースページに移動し、お使いのプラットフォームとGPUターゲットに合ったアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip`という名前のファイルをダウンロードします（`xxxx`はビルド番号です）。

#### ステップ2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、Ryzen AI Haloシステム向けに事前コンパイルされたROCm対応のビルドである`llama-cli`、`llama-server`、`rpc-server`が含まれています。

#### ステップ3: GPU検出の確認

```bash
./llama-cli --list-devices
```

期待される出力:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進んでください。

### オプション2: 手動でのソースビルド

<!-- @os:windows -->
#### ステップ1: llama.cppのビルド

**x64 Native Tools Command Prompt**（Visual Studio Build Toolsと共にインストールされます）を開き、リポジトリをクローンします。

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIPをパスに追加し、ROCmおよびRPCサポートを有効にしてビルドします。

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIPソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化 |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU（Radeon 8060s）をターゲットに指定 |
| `-G Ninja` | Ninjaビルドシステムを使用 |

#### ステップ2: GPU検出の確認

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

期待される出力:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### ステップ3: HIPをユーザーパスに追加

上記のビルドステップでは、`%HIP_PATH%\bin`は現在のセッションのみに設定されています。HIPライブラリを（x64 Native Tools Command Promptだけでなく）任意のターミナルで利用できるようにするには、ユーザーの`PATH`に恒久的に追加します。

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進んでください。
<!-- @os:end -->

<!-- @os:linux -->
#### ステップ1: llama.cppのビルド

リポジトリをクローンします。

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCmおよびRPCサポートを有効にしてビルドします。

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCmソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化 |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU（Radeon 8060s）をターゲットに指定 |

その他のビルドオプションについては、[llama.cppビルドドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)を参照してください。

#### ステップ2: GPU検出の確認

```bash
cd rocm/bin
./llama-cli --list-devices
```

期待される出力:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進んでください。
<!-- @os:end -->

## モデルのダウンロード

このプレイブックでは、[Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL)の`UD-Q2_K_XL`量子化による[Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6)を使用します。この量子化は、4台のRyzen AI Haloノードの合計GPUメモリ内に収まります。

Hugging Face CLIを使用してGGUFファイルをダウンロードします。
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **注記**: モデルのダウンロードは、マシン1（コントローラー）上で完了させる必要があります。RPCワーカーノード（マシン2、3、4）は、モデルファイルのローカルコピーを必要としません。

## クラスター上でのモデルの起動

llama.cppのRPC（Remote Procedure Call）エンジンは、単一のllama.cppインスタンスがネットワーク経由でモデルレイヤーをリモートワーカーにオフロードできるようにします。1台のマシンが**コントローラー**（マシン1）として動作し、トークナイゼーション、スケジューリング、オーケストレーションを処理します。他の3台のマシン（マシン2、3、4）はそれぞれ軽量な**RPCサーバー**を実行し、自身のGPUメモリと計算能力をコントローラーに公開します。

ロード時に、llama.cppはモデルを4つのノード全体に分割（シャーディング）します。ロードが完了すると、推論はまるで単一のアクセラレーター上で実行されているかのように進行します。RPCはテンソルの転送と同期を裏側で処理します。

### ステップ1: RPCサーバーの起動（マシン2、3、4）

マシン2、3、4のそれぞれで、自身のGPUリソースをコントローラーに公開するためにRPCサーバーを起動します。
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| フラグ | 目的 |
|------|---------|
| `-p` | RPCサーバーをブロードキャストするポート |
| `-c` | 大きなテンソル用のローカルキャッシュを有効化し、モデルロード中のネットワーク転送の繰り返しを回避 |
| `--host` | RPCサーバーをバインドするIPアドレス（すべてのインターフェースには`0.0.0.0`） |

その他のオプションについては、[llama.cpp RPCドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)を参照してください。

### ステップ2: モデルの起動（マシン1）

マシン2、3、4でRPCサーバーが稼働している状態で、`llama-cli`または`llama-server`のいずれかを使用してマシン1から推論を起動します。
#### llama-cli

`llama-cli` は、モデルと直接対話するためのターミナルベースのインターフェースを提供します。ベンチマーク、デバッグ、低レベルの実験に最適です。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>` の確認方法**: マシン 2、3、4 のそれぞれで `hostname -I | awk '{print $1}'` を実行し、ローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル（Powershell）で実行してください。

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>` の確認方法**: マシン 2、3、4 のそれぞれでターミナル（Powershell）にて `ipconfig | findstr /C:"IPv4"` を実行し、ローカル IP アドレスを確認します。

<!-- @os:end -->

実行すると、`llama-cli` はモデルの読み込み状況を表示し、モデルと直接チャットできるインタラクティブなプロンプトに入ります。

![4 つのノードで Kimi K2.6 を実行する llama-cli](assets/llama-cli-example.png)

#### llama-server

`llama-server` は、統合された Web UI と OpenAI 互換の HTTP API を備えた永続的なサーバープロセスを通じて、同じ推論エンジンを公開します。これは、長時間稼働するデプロイメント、複数ユーザーによるアクセス、外部ツールとの連携に適したインターフェースです。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>` の確認方法**: マシン 2、3、4 のそれぞれで `hostname -I | awk '{print $1}'` を実行し、ローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル（Powershell）で実行してください。

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>` の確認方法**: マシン 2、3、4 のそれぞれでターミナル（Powershell）にて `ipconfig | findstr /C:"IPv4"` を実行し、ローカル IP アドレスを確認します。
<!-- @os:end -->

起動後、ブラウザで `http://<HOST_IP>:8081` を開くと、組み込みの Web UI にアクセスできます。これにより、モデルと対話するためのブラウザベースのチャットインターフェースが提供されます。

![4 つのノードで Kimi K2.6 を実行する llama-server の Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` の確認方法**: マシン 1 で `hostname -I | awk '{print $1}'` を実行し、ローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` の確認方法**: マシン 1 でターミナル（Powershell）にて `ipconfig | findstr /C:"IPv4"` を実行し、ローカル IP アドレスを確認します。
<!-- @os:end -->

#### パラメータリファレンス

| フラグ | 目的 |
|------|---------|
| `-m` | GGUF モデルファイルへのパス（最初のシャード `00001-of-00008` を使用） |
| `-c` | トークン単位のコンテキストサイズ。値を大きくするとメモリ使用量が増加します |
| `-fa on` | AMD GPU でのパフォーマンス向上のため、rocWMMA Flash Attention を有効化します |
| `-ngl 999` | すべてのモデルレイヤーを GPU にオフロードします |
| `-lm none` | モデルの読み込みモードを `none` に設定し、メモリマッピングを無効化します。これにより、モデルサイズがシステム RAM を超えても VRAM に収まる場合に読み込み時間を短縮できます |
| `-b` | トークン単位の論理バッチサイズ。4096 に設定すると、各ノードでスループットとメモリ使用量のバランスが取れます |
| `-ub` | プロンプト処理用の物理（マイクロ）バッチサイズ。`-b` と一致させることで、不要なチャンク分割のオーバーヘッドを回避できます |
| `--host` | `llama-server` をバインドする IP（`llama-server` のみ） |
| `--port` | HTTP API を提供するポート（`llama-server` のみ） |
| `--rpc` | RPC ワーカーエンドポイント（`IP:port`）のカンマ区切りリスト |

完全なパラメータの使用方法については、[llama-cli のドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) および [llama-server のドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) を参照してください。

## 次のステップ

- **サードパーティアプリケーションとの接続**: `llama-server` は OpenAI 互換の API を公開します。OpenAI 互換の任意のアプリケーション（Open WebUI など）を、任意のプレースホルダー API キー（例: `none`）とともに `http://<HOST_IP>:8081` に向けることで、クラスターに接続できます
- **他のモデルの探索**: [Hugging Face](https://huggingface.co/models?search=gguf) で量子化された GGUF を参照し、クラスターの合計 GPU メモリに収まるモデルを見つけてください
- **4 ノードを超えるスケール**: 追加の Ryzen AI Halo システムを RPC ワーカーとして追加することで、1 兆パラメータ規模を超えるモデルにアクセスできます。追加のエンドポイントをカンマ区切りリストとして `--rpc` に渡します（例: `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`）