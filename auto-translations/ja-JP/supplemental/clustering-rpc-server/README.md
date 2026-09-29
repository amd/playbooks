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

# RPCによる2台のRyzen™ AI Haloのクラスタリング

## 概要

お使いのRyzen™ AI Haloは、すでにローカルで大規模言語モデルを実行できる性能を備えています。クラスタリングを行うことで、複数のシステムのGPUメモリをローカルネットワーク経由で結合し、より強力な推論能力、優れたコード生成能力、そしてより深い多言語理解力を持つ、さらに大規模なモデルへのアクセスを、すべて自分の手元にあるハードウェア上で実現できます。

このプレイブックでは、llama.cppのRPCエンジンを使用して2台のRyzen AI Haloシステムをクラスタリングし、AMD ROCm™アクセラレーションにより両方のマシンにまたがって358Bパラメータのモデルである GLM 4.7 を実行する方法を解説します。

## 学べること

- Ryzen AI Haloシステム上でのVRAM割り当ての拡張方法
- ROCmおよびRPCサポートを備えたllama.cppのインストール
- RPCワーカーの構成と、2台のノード間での分散推論の起動
- 2台のネットワーク接続されたRyzen AI Haloシステム全体での358Bパラメータモデルの実行

## メモリ構成の設定

> **注**: この手順はマシン1とマシン2の両方で実施してください。

<!-- @os:windows -->
Windowsでは、より多くのメモリを必要とする大規模モデルを実行するために、AMD Variable Graphics Memory(iGPU VRAM)割り当てを使用する必要があります。

これは、AMD Software: Adrenalin Edition コントロールパネルを開き、`Performance > Tuning > AMD Variable Graphics Memory` に移動することで設定できます。値を **96 GB** に設定してください。変更を反映させるには、システムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この容量は、以下の手順でカーネルのTranslation Table Manager(TTM)ページ設定を変更することで増やすことができます。AMDでは、BIOSで最小専用VRAM(0.5 GB)を設定することを推奨しています。

* pipxユーティリティをインストールし、pipxでインストールされたホイールのパスをシステムの検索パスに追加します。

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

* 共有メモリ設定を **120 GB** に再構成します:
  ```bash
  amd-ttm --set 120
  ```

* 変更を反映させるには、システムを再起動してください。


<!-- @os:end -->
<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->
## 前提条件

### ハードウェア

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットをスイッチに直接配線したスター型トポロジーで接続します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスタを構成する演算ノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo間の通信を可能にする中央スイッチ(少なくとも2ポート) |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続する(Cat 7以上を推奨) |

> **注**: 2台のRyzen AI Haloユニットを接続するには、イーサネットスイッチの2ポートが必要です。Haloユニットの一方ではなく別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++** ワークロードを含む [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: この手順はマシン1とマシン2の両方で実施してください。

各Ryzen AI HaloユニットをCat 7(以上)ケーブルを使用してイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、書き留めておきます(以下では`IFNAME`と表記します)。次を実行してください:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これによりインターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認し、リンクがアクティブでフル速度で動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>` は [1. ネットワークインターフェースの確認](#1-determine-network-interfaces) で確認したインターフェース名に置き換えてください。

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブルの接続を確認し、スイッチのポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

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

> **注**: 速度が`10 Gbps`より低い場合、またはリンクが確立しない場合は、ケーブルの接続を確認し、スイッチのポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注**: この手順はマシン1とマシン2の両方で実施してください。

2つのインストールオプションが利用できます:

- [オプション1: Lemonade SDK(推奨)](#option-1-lemonade-sdk-recommended) - ビルド済みバイナリによる最速のセットアップ
- [オプション2: 手動でのソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御できるソースからのビルド

### オプション1: Lemonade SDK(推奨)

Lemonade SDKは、gfx1151(Strix Halo / Ryzen AI Max+ 395)やその他の最新Radeonアーキテクチャなどのgfx1151(Strix Halo / Ryzen AI Max+ 395)を含むGPUを対象に、AMD ROCm 7アクセラレーションを備えたllama.cppのナイトリービルドを提供します。

<!-- @os:windows -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新のリリースページにアクセスし、お使いのプラットフォームとGPUターゲットに一致するアーカイブをダウンロードしてください。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip`（`xxxx`はビルド番号）という名前のファイルをダウンロードしてください。

#### ステップ2: バイナリの展開

ダウンロードしたアーカイブを解凍します。

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、お使いのRyzen AI HaloシステムでROCmが有効化された`llama-cli.exe`、`llama-server.exe`、`rpc-server.exe`のビルド済みバイナリが含まれています。

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

最新のリリースページにアクセスし、お使いのプラットフォームとGPUターゲットに一致するアーカイブをダウンロードしてください。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip`（`xxxx`はビルド番号）という名前のファイルをダウンロードしてください。

#### ステップ2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、お使いのRyzen AI HaloシステムでROCmが有効化された`llama-cli`、`llama-server`、`rpc-server`のビルド済みバイナリが含まれています。

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

（Visual Studio Build Toolsに付属する）**x64 Native Tools Command Prompt**を開き、リポジトリをクローンします。

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIPをパスに追加し、ROCmとRPCサポートを有効にしてビルドします。

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIPソフトウェアスタックを有効化する |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化する |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU（Radeon 8060s）をターゲットにする |
| `-G Ninja` | Ninjaビルドシステムを使用する |

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

#### ステップ3: HIPをユーザーパスに追加する

上記のビルド手順では、現在のセッションのみに対して`%HIP_PATH%\bin`を設定しました。HIPライブラリを（x64 Native Tools Command Promptだけでなく）任意のターミナルで利用できるようにするには、これをユーザーの`PATH`に恒久的に追加してください。

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

ROCmとRPCサポートを有効にしてビルドします。

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCmソフトウェアスタックを有効化する |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化する |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU（Radeon 8060s）をターゲットにする |

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

このプレイブックでは、[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)による`Q4_K_XL`量子化版の3580億パラメータモデルである[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)を使用します。この量子化レベルでは、モデルは約205GBのストレージを必要とし、2台のRyzen AI Haloノードの合計GPUメモリに収まります。

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

> **注**: モデルのダウンロードはMachine 1（コントローラー）で完了させる必要があります。RPCワーカーノードは、モデルファイルのローカルコピーを必要としません。

## クラスター上でのモデルの起動

llama.cpp RPC（Remote Procedure Call）エンジンを使用すると、単一のllama.cppインスタンスがモデルレイヤーをネットワーク経由でリモートワーカーにオフロードできます。1台のマシンが**コントローラー**（Machine 1）として動作し、トークン化、スケジューリング、オーケストレーションを担当します。もう1台のマシンは軽量な**RPCサーバー**（Machine 2）を実行し、そのGPUメモリと計算能力をコントローラーに公開します。

読み込み時、llama.cppはモデルを両方のノードにシャーディングします。読み込みが完了すると、あたかも単一のアクセラレータ上で実行されているかのように推論が進みます。RPCはテンソルの転送と同期を裏側で処理します。

### ステップ1: RPCサーバーの起動（Machine 2）

Machine 2上で、RPCサーバーを起動してGPUリソースをコントローラーに公開します。
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
| `-c` | 大きなテンソル用のローカルキャッシュを有効化し、モデル読み込み時の繰り返しのネットワーク転送を回避する |
| `--host` | RPCサーバーをバインドするIPアドレス（すべてのインターフェースの場合は`0.0.0.0`） |

その他のオプションについては、[llama.cpp RPCドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)を参照してください。

### ステップ2: モデルの起動（Machine 1）

Machine 2でRPCサーバーが実行されている状態で、Machine 1から`llama-cli`または`llama-server`を使用して推論を起動します。

#### llama-cli

`llama-cli`は、モデルと直接対話するためのターミナルベースのインターフェースを提供します。ベンチマーク、デバッグ、低レベルの実験に最適です。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`の確認方法**: Machine 2上で`hostname -I | awk '{print $1}'`を実行し、そのローカルIPアドレスを確認してください。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル（Powershell）で実行してください。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`の確認方法**: Machine 2上でターミナル（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行し、そのローカルIPアドレスを確認してください。

<!-- @os:end -->

実行が開始されると、`llama-cli`はモデルの読み込み進捗を表示し、モデルと直接チャットできるインタラクティブなプロンプトに入ります。

![2ノードにわたってGLM 4.7を実行しているllama-cli](assets/llama-cli-example.png)
#### llama-server

`llama-server` は同じ推論エンジンを、統合された Web UI と OpenAI 互換の HTTP API を備えた永続的なサーバープロセスとして公開します。これは、長時間稼働するデプロイメント、マルチユーザーアクセス、および外部ツールとの連携に適したインターフェースです。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` の確認方法**: Machine 2 上で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル(Powershell)で実行してください。

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` の確認方法**: Machine 2 上で、ターミナル(Powershell)で `ipconfig | findstr /C:"IPv4"` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

起動後、ブラウザで `http://<HOST_IP>:8081` を開くと、組み込みの Web UI にアクセスできます。これにより、モデルとやり取りするためのブラウザベースのチャットインターフェースが提供されます。

![2 つのノードで GLM 4.7 を実行する llama-server の Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` の確認方法**: Machine 1 上で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` の確認方法**: Machine 1 上で、ターミナル(Powershell)で `ipconfig | findstr /C:"IPv4"` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

#### パラメーターリファレンス

| フラグ | 目的 |
|------|---------|
| `-m` | GGUF モデルファイルへのパス(最初のシャード `00001-of-00005` を使用) |
| `-c` | トークン単位のコンテキストサイズ。値を大きくするとメモリ使用量が増加します |
| `-fa on` | AMD GPU でのパフォーマンス向上のため rocWMMA Flash Attention を有効化します |
| `-ngl 999` | すべてのモデルレイヤーを GPU にオフロードします |
| `-lm none` | モデルのロードモードを `none` に設定し、メモリマッピングを無効化して、モデルサイズがシステム RAM を超えるが VRAM には収まる場合のロード時間を短縮します |
| `--host` | `llama-server` をバインドする IP(`llama-server` のみ) |
| `--port` | HTTP API を提供するポート(`llama-server` のみ) |
| `--rpc` | RPC ワーカーエンドポイント(`IP:port`)のカンマ区切りリスト |

パラメーターの完全な使用方法については、[llama-cli のドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)および [llama-server のドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)を参照してください。

## 次のステップ

- **サードパーティアプリケーションとの接続**: `llama-server` は OpenAI 互換の API を公開します。任意の OpenAI 互換アプリケーション(Open WebUI など)を、任意のプレースホルダー API キー(例: `none`)とともに `http://<HOST_IP>:8081` に接続することで、クラスターに接続できます
- **他のモデルの探索**: [Hugging Face](https://huggingface.co/models?search=gguf) で量子化された GGUF を閲覧し、クラスターの合計 GPU メモリに収まるモデルを見つけてください
- **4 ノードへのスケール**: さらに 2 台の Ryzen AI Halo システムを追加の RPC ワーカーとして追加することで、1 兆パラメータ規模のモデルにアクセスできます。追加のエンドポイントは `--rpc` にカンマ区切りリストとして渡します(例: `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)