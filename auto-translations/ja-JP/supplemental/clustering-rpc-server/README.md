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

# RPCを使用した2つのRyzen™ AI Haloのクラスタリング

## 概要

お使いのRyzen™ AI Haloは、すでにローカルで大規模言語モデルを実行できます。クラスタリングはこれをさらに一歩進め、複数のシステムのGPUメモリをローカルネットワーク経由で結合し、より強力な推論、より優れたコード生成、より深い多言語理解を備えた、さらに大規模なモデルへのアクセスを可能にします。すべてお使いのハードウェア上で完結します。

このプレイブックでは、llama.cppのRPCエンジンを使用して2つのRyzen AI Haloシステムをクラスタリングし、AMD ROCm™アクセラレーションを使用して両方のマシンにまたがる358Bパラメータモデルである GLM 4.7 を実行する方法を学びます。

## 学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmとRPCサポートを備えたllama.cppのインストール
- RPCワーカーの設定と、2つのノードにまたがる分散推論の起動
- 2つのネットワーク接続されたRyzen AI Haloシステムにまたがる358Bパラメータモデルの実行

## メモリ構成の設定

> **注**: この手順はマシン1とマシン2の両方で完了させてください。

<!-- @device:halo_box -->
<!-- @os:windows -->
> **128 GB前後またはそれ以上のモデルを実行する場合:** Windowsを実行しているAMD Ryzen™ AI Max 400シリーズ(Gorgon Halo)システムでは、128 GBのメモリに近い、またはそれを超えるモデルを実行するには、エラーなしで実行するための追加設定が必要です。モデルをロードする前に、[AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines)に従ってください。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
Windowsでは、より高いメモリを必要とする大規模モデルを実行するために、AMD Variable Graphics Memory(iGPU VRAM)割り当てを使用する必要があります。

これを行うには、AMD Software: Adrenalin Editionコントロールパネルを開き、`Performance > Tuning > AMD Variable Graphics Memory`に移動します。値を**96 GB**に設定します。変更を有効にするには、システムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順に従ってカーネルのTranslation Table Manager(TTM)ページ設定を変更することで増やすことができます。AMDは、BIOSで最小専用VRAM(0.5 GB)を設定することを推奨します。

* pipxユーティリティをインストールし、pipxでインストールされたwheelのパスをシステムの検索パスに追加します。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPIからamd-debug-tools wheelをインストールします。
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttmツールを実行して、共有メモリの現在の設定をクエリします。
  ```bash
  amd-ttm
  ```

* 共有メモリの設定を**120 GB**に再構成します:
  ```bash
  amd-ttm --set 120
  ```

* 変更を有効にするには、システムを再起動してください。


<!-- @os:end -->
<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->
## 前提条件

### ハードウェア

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットがスイッチに直接接続されたスター型トポロジーで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスターを構成するコンピュートノード |
| 10Gbpsイーサネットスイッチ | 1 | マルチノードのRyzen AI Halo通信を可能にする中央スイッチ(最低2ポート) |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続します(Cat 7以上を推奨) |

> **注**: 2つのRyzen AI Haloユニットを接続するには、イーサネットスイッチの2つのポートが必要です。Haloユニットのいずれかではなく別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++**ワークロードを含む[Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: この手順はマシン1とマシン2の両方で完了させてください。

Cat 7(以上)ケーブルを使用して、各Ryzen AI Haloユニットをイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの特定

各マシンで、ネットワークインターフェースの名前を確認し、メモしておきます(以下では`IFNAME`と呼びます)。次を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これによりインターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブでフル速度で動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>`を[1. ネットワークインターフェースの特定](#1-determine-network-interfaces)の出力インターフェース名に置き換えてください

速度が`10000Mb/s`になっているはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

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

> **注**: 速度が`10 Gbps`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注**: この手順はマシン1とマシン2の両方で完了させてください。

2つのインストールオプションが利用可能です:

- [オプション1: Lemonade SDK(推奨)](#option-1-lemonade-sdk-recommended) - ビルド済みバイナリ、最速のセットアップ
- [オプション2: 手動ソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御したソースからのビルド
### オプション1: Lemonade SDK (推奨)

Lemonade SDKは、AMD ROCm 7アクセラレーションを備えたllama.cppのナイトリービルドを提供しており、gfx1151 (Strix Halo / Ryzen AI Max+ 395) やその他の最近のRadeonアーキテクチャなどのGPUを対象としています。

<!-- @os:windows -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新のリリースページに移動し、お使いのプラットフォームとGPUターゲットに一致するアーカイブをダウンロードしてください。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip` という名前のファイルをダウンロードします (`xxxx` はビルド番号です)。

#### ステップ2: バイナリの展開

ダウンロードしたアーカイブを解凍します。

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、ROCm対応の `llama-cli.exe`、`llama-server.exe`、`rpc-server.exe` のビルドが含まれており、お使いのRyzen AI Haloシステム向けに事前コンパイルされています。

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

最新のリリースページに移動し、お使いのプラットフォームとGPUターゲットに一致するアーカイブをダウンロードしてください。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` という名前のファイルをダウンロードします (`xxxx` はビルド番号です)。

#### ステップ2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、ROCm対応の `llama-cli`、`llama-server`、`rpc-server` のビルドが含まれており、お使いのRyzen AI Haloシステム向けに事前コンパイルされています。

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
各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進みます。

### オプション2: 手動ソースビルド

<!-- @os:windows -->
#### ステップ1: llama.cppのビルド

**x64 Native Tools Command Prompt** (Visual Studio Build Toolsと共にインストールされます) を開き、リポジトリをクローンします。

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
| `-DGGML_HIP=ON` | ROCm/HIPソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化 |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU (Radeon 8060s) をターゲット |
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

上記のビルドステップでは、現在のセッションに限り `%HIP_PATH%\bin` を設定しました。HIPライブラリを (x64 Native Tools Command Promptだけでなく) どのターミナルでも使用できるようにするには、ユーザーの `PATH` に永続的に追加します。

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

ROCmとRPCサポートを有効にしてビルドします。

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCmソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効化 |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU (Radeon 8060s) をターゲット |

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

各ノードでllama.cppの準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進みます。
<!-- @os:end -->

## モデルのダウンロード

このプレイブックでは、[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)が提供する `Q4_K_XL` 量子化の358Bパラメータモデルである[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)を使用します。この量子化では、モデルに約205GBのストレージが必要となり、2台のRyzen AI Haloノードを合わせたGPUメモリに収まります。

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

> **注**: モデルのダウンロードは、マシン1 (コントローラー) 上で完了させる必要があります。RPCワーカーノードには、モデルファイルのローカルコピーは必要ありません。

## クラスターでのモデルの起動

llama.cpp RPC (Remote Procedure Call) エンジンにより、単一のllama.cppインスタンスがネットワーク経由でモデルレイヤーをリモートワーカーにオフロードできます。1台のマシンが**コントローラー** (マシン1) として動作し、トークン化、スケジューリング、オーケストレーションを処理します。もう1台のマシンは、軽量な**RPCサーバー** (マシン2) を実行し、そのGPUメモリと計算能力をコントローラーに公開します。

ロード時に、llama.cppはモデルを両方のノードに分割します。ロードが完了すると、単一のアクセラレーター上で実行しているかのように推論が進行します。RPCは、テンソルの転送と同期を裏側で処理します。

### ステップ1: RPCサーバーの起動 (マシン2)

マシン2で、RPCサーバーを起動し、そのGPUリソースをコントローラーに公開します。
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
| `-c` | 大きなテンソル用のローカルキャッシュを有効にし、モデルロード中の繰り返しのネットワーク転送を回避する |
| `--host` | RPCサーバーをバインドするIPアドレス (すべてのインターフェースの場合は `0.0.0.0`) |

その他のオプションについては、[llama.cpp RPCドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)を参照してください。

### ステップ2: モデルの起動 (マシン1)

マシン2でRPCサーバーが実行されている状態で、`llama-cli` または `llama-server` のいずれかを使用して、マシン1から推論を起動します。
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

> **`<RPC_WORKER_IP>`の確認方法**: マシン2で`hostname -I | awk '{print $1}'`を実行し、ローカルIPアドレスを確認します。
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

> **`<RPC_WORKER_IP>`の確認方法**: マシン2でターミナル（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行し、ローカルIPアドレスを確認します。

<!-- @os:end -->

実行すると、`llama-cli`はモデルの読み込み状況を表示し、モデルと直接チャットできる対話型プロンプトに入ります。

![llama-cli running GLM 4.7 across two nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server`は、統合されたウェブUIとOpenAI互換のHTTP APIを備えた永続的なサーバープロセスを通じて、同じ推論エンジンを公開します。これは、長時間稼働するデプロイメント、マルチユーザーアクセス、外部ツールとの統合に適したインターフェースです。

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

> **`<RPC_WORKER_IP>`の確認方法**: マシン2で`hostname -I | awk '{print $1}'`を実行し、ローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル（Powershell）で実行してください。

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

> **`<RPC_WORKER_IP>`の確認方法**: マシン2でターミナル（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行し、ローカルIPアドレスを確認します。
<!-- @os:end -->

起動後、ブラウザで`http://<HOST_IP>:8081`を開くと、組み込みのウェブUIにアクセスできます。これにより、モデルと対話するためのブラウザベースのチャットインターフェースが提供されます。

![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`の確認方法**: マシン1で`hostname -I | awk '{print $1}'`を実行し、ローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`の確認方法**: マシン1でターミナル（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行し、ローカルIPアドレスを確認します。
<!-- @os:end -->

#### パラメータリファレンス

| フラグ | 目的 |
|------|---------|
| `-m` | GGUFモデルファイルへのパス（最初のシャード`00001-of-00005`を使用） |
| `-c` | トークン単位のコンテキストサイズ。値が大きいほどメモリ使用量が増加します |
| `-fa on` | AMD GPUでのパフォーマンス向上のためrocWMMA Flash Attentionを有効化します |
| `-ngl 999` | すべてのモデルレイヤーをGPUにオフロードします |
| `-lm none` | モデルの読み込みモードを`none`に設定し、モデルサイズがシステムRAMを超えるがVRAMには収まる場合に読み込み時間を短縮するため、メモリマッピングを無効化します |
| `--host` | `llama-server`をバインドするIP（`llama-server`のみ） |
| `--port` | HTTP APIを提供するポート（`llama-server`のみ） |
| `--rpc` | RPCワーカーのエンドポイント（`IP:port`）のカンマ区切りリスト |

パラメータの詳細な使用方法については、[llama-cliドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)および[llama-serverドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)を参照してください。

## 次のステップ

- **サードパーティアプリケーションの接続**: `llama-server`はOpenAI互換のAPIを公開します。OpenAI互換の任意のアプリケーション（Open WebUIなど）を`http://<HOST_IP>:8081`に向け、任意のプレースホルダーAPIキー（例：`none`）を使用することで、クラスターに接続できます
- **他のモデルの探索**: [Hugging Face](https://huggingface.co/models?search=gguf)で量子化されたGGUFを閲覧し、クラスターの合計GPUメモリに収まるモデルを見つけてください
- **4ノードへのスケール**: Ryzen AI Haloシステムをさらに2台追加のRPCワーカーとして導入することで、1兆パラメータ規模のモデルにアクセスできます。`--rpc`にカンマ区切りのリストとして追加のエンドポイントを渡してください（例：`--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`）