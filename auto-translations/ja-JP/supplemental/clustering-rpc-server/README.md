<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックにはGitHubがレンダリングできない特殊なタグが使用されています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

# RPCによる2台のRyzen™ AI Haloのクラスタリング

## 概要

Ryzen™ AI Haloは、既にローカルで大規模言語モデルを実行できる能力を備えています。クラスタリングは、複数のシステムのGPUメモリをローカルネットワーク経由で結合することで、これをさらに一歩進め、より強力な推論能力、優れたコード生成、より深い多言語理解を備えたさらに大規模なモデルへのアクセスを、完全に自身のハードウェア上で実現します。

このプレイブックでは、llama.cppのRPCエンジンを使用して2台のRyzen AI Haloシステムをクラスタリングし、AMD ROCm™アクセラレーションを用いて358Bパラメータのモデルであるgemini GLM 4.7を両方のマシンにまたがって実行する方法を学びます。

## 学習内容

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmおよびRPCサポート付きのllama.cppのインストール
- RPCワーカーの設定と2ノード間での分散推論の起動
- ネットワーク接続された2台のRyzen AI Haloシステムにまたがる358Bパラメータモデルの実行

## メモリ構成の設定

> **注**: この手順は、マシン1とマシン2の両方で実施してください。

<!-- @os:windows -->
Windowsでは、より多くのメモリを必要とする大規模なモデルを実行するために、AMD Variable Graphics Memory（iGPU VRAM）割り当てを使用する必要があります。

これは、AMD Software: Adrenalin Editionコントロールパネルを開き、`パフォーマンス > チューニング > AMD Variable Graphics Memory`に移動することで設定できます。値を**96 GB**に設定してください。変更を有効にするには、システムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順に従ってカーネルのTranslation Table Manager（TTM）ページ設定を変更することで増やすことができます。AMDでは、BIOSで最小専有VRAM（0.5 GB）を設定することを推奨しています。

* pipxユーティリティをインストールし、pipxでインストールされたホイールのパスをシステム検索パスに追加します。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPIからamd-debug-toolsホイールをインストールします。
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttmツールを実行して、共有メモリの現在の設定を確認します。
  ```bash
  amd-ttm
  ```

* 共有メモリ設定を**120 GB**に再構成します:
  ```bash
  amd-ttm --set 120
  ```

* 変更を有効にするには、システムを再起動してください。


<!-- @os:end -->
<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->
## 前提条件

### ハードウェア

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットをスイッチに直接接続するスター型トポロジーで接続します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスターを構成するコンピュートノード |
| 10GbpsイーサネットSwitch | 1 | 複数ノードのRyzen AI Halo通信を可能にする中央スイッチ（少なくとも2ポート） |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続します（Cat 7以上を推奨） |

> **注**: 2台のRyzen AI Haloユニットを接続するには、イーサネットスイッチのポートが2つ必要です。Haloユニットの一方ではなく、別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++**ワークロード付きの[Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理ハードウェアセットアップ

> **注**: この手順は、マシン1とマシン2の両方で実施してください。

Cat 7（以上）のケーブルを使用して、各Ryzen AI Haloユニットをイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、書き留めておきます（以下では`IFNAME`として参照されます）。次を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これにより、次のようにインターフェース名が直接表示されます:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブでフル速度で動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>`を[1. ネットワークインターフェースの確認](#1-ネットワークインターフェースの確認)の出力インターフェース名に置き換えてください

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`未満の場合、またはリンクが確立しない場合は、ケーブルの接続を確認し、スイッチのポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

<!-- @os:windows -->
### ネットワークリンク速度の確認

各マシンで、ネットワークインターフェースのリンク速度を確認します:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

イーサネットインターフェースは`Up`状態で、`10 Gbps`で動作している必要があります:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注**: 速度が`10 Gbps`未満の場合、またはリンクが確立しない場合は、ケーブルの接続を確認し、スイッチのポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注**: この手順は、マシン1とマシン2の両方で実施してください。

2つのインストールオプションが利用可能です:

- [オプション1: Lemonade SDK（推奨）](#option-1-lemonade-sdk-recommended) - ビルド済みバイナリで最速のセットアップ
- [オプション2: 手動でのソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御できるソースからのビルド

### オプション1: Lemonade SDK（推奨）

Lemonade SDKは、gfx1151（Strix Halo / Ryzen AI Max+ 395）などのGPUや、その他の最新のRadeonアーキテクチャをターゲットとした、AMD ROCm 7アクセラレーション付きのllama.cppのナイトリービルドを提供します。

<!-- @os:windows -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新のリリースページに移動し、お使いのプラットフォームとGPUターゲットに合ったアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip`（`xxxx`はビルド番号）という名前のファイルをダウンロードします。

#### ステップ2: バイナリの展開

ダウンロードしたアーカイブを解凍します。

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、Ryzen AI Halo システム向けにビルドされたROCm対応の`llama-cli.exe`、`llama-server.exe`、`rpc-server.exe`が含まれています。

#### ステップ3: GPU検出の確認

```bash
.\llama-cli.exe --list-devices
```

期待される出力：

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

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip`（`xxxx`はビルド番号）という名前のファイルをダウンロードします。

#### ステップ2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、Ryzen AI Halo システム向けにビルドされたROCm対応の`llama-cli`、`llama-server`、`rpc-server`が含まれています。

#### ステップ3: GPU検出の確認

```bash
./llama-cli --list-devices
```

期待される出力：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進みます。

### オプション2: 手動でのソースビルド

<!-- @os:windows -->
#### ステップ1: llama.cppのビルド

**x64 Native Tools Command Prompt**（Visual Studio Build Toolsとともにインストールされます）を開き、リポジトリをクローンします。

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIPをパスに追加し、ROCmとRPCのサポートを有効にしてビルドします。

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIPソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化 |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU（Radeon 8060s）をターゲット |
| `-G Ninja` | Ninjaビルドシステムを使用 |

#### ステップ2: GPU検出の確認

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

期待される出力：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### ステップ3: HIPをユーザーパスに追加

上記のビルド手順では、`%HIP_PATH%\bin`は現在のセッションのみに設定されました。HIPライブラリを（x64 Native Tools Command Promptだけでなく）どのターミナルでも利用できるようにするには、ユーザーの`PATH`に恒久的に追加します。

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進みます。
<!-- @os:end -->

<!-- @os:linux -->
#### ステップ1: llama.cppのビルド

リポジトリをクローンします。

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCmとRPCのサポートを有効にしてビルドします。

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCmソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化 |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | AMD GPU向けの強化されたFlash AttentionのためにrocWMMAを有効化 |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU（Radeon 8060s）をターゲット |

その他のビルドオプションについては、[llama.cppビルドドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)を参照してください。

#### ステップ2: GPU検出の確認

```bash
cd rocm/bin
./llama-cli --list-devices
```

期待される出力：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進みます。
<!-- @os:end -->

## モデルのダウンロード

このプレイブックでは、[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)による`Q4_K_XL`量子化版の358Bパラメータモデル、[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)を使用します。この量子化では、モデルは約205GBのストレージを必要とし、2台のRyzen AI Haloノードの合計GPUメモリに収まります。

Hugging Face CLIを使用してGGUFファイルをダウンロードします。
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **注**: モデルのダウンロードはマシン1（コントローラー）で完了させる必要があります。RPCワーカーノードには、モデルファイルのローカルコピーは不要です。

## クラスタでのモデルの起動

llama.cppのRPC（リモートプロシージャコール）エンジンにより、単一のllama.cppインスタンスがネットワーク経由でモデル層をリモートワーカーにオフロードできます。1台のマシンが**コントローラー**（マシン1）として動作し、トークン化、スケジューリング、オーケストレーションを処理します。もう1台のマシンは軽量な**RPCサーバー**（マシン2）を実行し、そのGPUメモリと計算能力をコントローラーに公開します。

ロード時に、llama.cppはモデルを両ノードにシャーディングします。ロードが完了すると、単一のアクセラレータ上で実行しているかのように推論が進行します。RPCは、テンソルの転送と同期を裏側で処理します。

### ステップ1: RPCサーバーの起動（マシン2）

マシン2で、GPUリソースをコントローラーに公開するためにRPCサーバーを起動します。
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| フラグ | 目的 |
|------|---------|
| `-p` | RPCサーバーをブロードキャストするポート |
| `-c` | 大きなテンソル用のローカルキャッシュを有効にし、モデルのロード中に発生するネットワーク転送の繰り返しを回避 |
| `--host` | RPCサーバーをバインドするIPアドレス（すべてのインターフェースの場合は`0.0.0.0`） |

その他のオプションについては、[llama.cpp RPCドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)を参照してください。

### ステップ2: モデルの起動（マシン1）

マシン2でRPCサーバーが動作している状態で、マシン1から`llama-cli`または`llama-server`のいずれかを使用して推論を起動します。

#### llama-cli

`llama-cli`は、モデルと直接対話するためのターミナルベースのインターフェースを提供します。ベンチマーク、デバッグ、低レベルの実験に最適です。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`の確認方法**: マシン2で`hostname -I | awk '{print $1}'`を実行し、そのローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル（Powershell）で実行してください。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`の確認方法**: マシン2でターミナル（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行し、そのローカルIPアドレスを確認します。

<!-- @os:end -->

起動すると、`llama-cli`はモデルのロード進捗を表示し、モデルと直接チャットできるインタラクティブなプロンプトに入ります。

![2つのノードでGLM 4.7を実行するllama-cli](assets/llama-cli-example.png)
#### llama-server

`llama-server` は、統合されたウェブ UI と OpenAI 互換の HTTP API を備えた永続的なサーバープロセスを通じて、同じ推論エンジンを公開します。これは、長時間稼働するデプロイメント、マルチユーザーアクセス、および外部ツールとの統合に適したインターフェースです。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` の確認方法**: マシン 2 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル (Powershell) で実行してください。

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` の確認方法**: マシン 2 でターミナル (Powershell) を開き、`ipconfig | findstr /C:"IPv4"` を実行して、そのローカル IP アドレスを確認します。
<!-- @os:end -->

起動後、ブラウザで `http://<HOST_IP>:8081` を開くと、組み込みのウェブ UI にアクセスできます。これにより、モデルとやり取りするためのブラウザベースのチャットインターフェースが提供されます。

![2 つのノードにまたがって GLM 4.7 を実行している llama-server ウェブ UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` の確認方法**: マシン 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` の確認方法**: マシン 1 でターミナル (Powershell) を開き、`ipconfig | findstr /C:"IPv4"` を実行して、そのローカル IP アドレスを確認します。
<!-- @os:end -->

#### パラメータリファレンス

| フラグ | 目的 |
|------|---------|
| `-m` | GGUF モデルファイルへのパス (最初のシャード `00001-of-00005` を使用) |
| `-c` | トークン単位のコンテキストサイズ。値を大きくするとメモリ使用量が増加します |
| `-fa on` | AMD GPU 上でのパフォーマンス向上のため、rocWMMA Flash Attention を有効にします |
| `-ngl 999` | すべてのモデルレイヤーを GPU にオフロードします |
| `--no-mmap` | メモリマッピングを無効にし、モデルサイズがシステム RAM を超えるが VRAM には収まる場合に読み込み時間を短縮します |
| `--host` | `llama-server` をバインドする IP (`llama-server` のみ) |
| `--port` | HTTP API を提供するポート (`llama-server` のみ) |
| `--rpc` | RPC ワーカーエンドポイント (`IP:port`) のカンマ区切りリスト |

パラメータの詳細な使用方法については、[llama-cli ドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) および [llama-server ドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) を参照してください。

## 次のステップ

- **サードパーティアプリケーションとの接続**: `llama-server` は OpenAI 互換の API を公開しています。OpenAI 互換のアプリケーション (Open WebUI など) を、任意のプレースホルダー API キー (例: `none`) とともに `http://<HOST_IP>:8081` に向けることで、クラスターに接続できます
- **他のモデルを探索する**: [Hugging Face](https://huggingface.co/models?search=gguf) で量子化された GGUF を閲覧し、クラスターの合計 GPU メモリに収まるモデルを見つけてください
- **4 ノードへのスケール**: 追加の RPC ワーカーとして、さらに 2 台の Ryzen AI Halo システムを追加すると、1 兆パラメータ規模のモデルにアクセスできます。追加のエンドポイントは、カンマ区切りのリストとして `--rpc` に渡してください (例: `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)