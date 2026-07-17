<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# RPCを使用した2台のRyzen™ AI Haloのクラスタリング

## 概要

Ryzen™ AI Haloは、すでにローカルで大規模言語モデルを実行する能力を備えています。クラスタリングはこれをさらに発展させ、ローカルネットワーク上で複数のシステムのGPUメモリを組み合わせることで、より強力な推論、優れたコード生成、深い多言語理解を持つさらに大きなモデルへのアクセスを可能にします。これらはすべて、完全にご自身のハードウェア上で実現できます。

このPlaybookでは、llama.cppのRPCエンジンを使用して2台のRyzen AI Haloシステムをクラスタリングし、AMD ROCm™アクセラレーションを使用して358BパラメータモデルであるGLM 4.7を両マシンにまたがって実行する方法を説明します。

## 学習内容

- Ryzen AI HaloシステムでのVRAM割り当てを拡張する方法
- ROCmおよびRPCサポートを含むllama.cppのインストール
- RPCワーカーの設定と2つのノードにまたがる分散推論の起動
- 2台のネットワーク接続されたRyzen AI Haloシステムにまたがる358Bパラメータモデルの実行

## メモリ設定の構成

> **注意**: このステップはマシン1とマシン2の両方で実行してください。

<!-- @os:windows -->
Windowsで、より多くのメモリを必要とする大規模モデルを実行するには、AMD Variable Graphics Memory（iGPU VRAM）割り当てを使用する必要があります。

これは、AMD Software: Adrenalin Editionコントロールパネルを開き、`Performance > Tuning > AMD Variable Graphics Memory`に移動することで設定できます。値を**96 GB**に設定してください。変更を有効にするためにシステムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを使用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順でカーネルのTranslation Table Manager（TTM）ページ設定を変更することで増やすことができます。AMDはBIOSで最小専用VRAMを設定すること（0.5 GB）を推奨しています。

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

* 共有メモリ設定を**120 GB**に再設定します：
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

このPlaybookには、2台のRyzen AI Haloユニットと1台のEthernetスイッチが必要です。各ユニットをスイッチに直接接続したスタートポロジーで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスターを構成するコンピュートノード |
| 10Gbps Ethernetスイッチ | 1 | マルチノードRyzen AI Halo通信を可能にする中央スイッチ（最低2ポート） |
| Ethernetケーブル | 2 | 各HaloユニットをスイッチへI接続する（Cat 7以上推奨） |

> **注意**: 2台のRyzen AI HaloユニットをI接続するには、2つのEthernetスイッチポートが必要です。Haloユニットの1台ではなく別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)（**Desktop Development with C++**ワークロードを含む）
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注意**: このステップはマシン1とマシン2の両方で実行してください。

Cat 7（以上）のケーブルを使用して、各Ryzen AI HaloユニットをEthernetスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの確認

各マシンで、ネットワークインターフェースの名前を確認してメモしておきます（以下では`IFNAME`として参照します）。次のコマンドを実行します：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これにより、インターフェース名が直接出力されます。例：

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブでフル速度で動作していることを確認します：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**: `<IFNAME>`を[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)で取得したインターフェース名に置き換えてください。

速度が`10000Mb/s`と表示されるはずです：

```bash
	Speed: 10000Mb/s
```

> **注意**: 速度が`10000Mb/s`より低い場合、またはリンクが確立されない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。スイッチによっては、オートネゴシエーションを無効にしてリンク速度を手動で設定する必要がある場合があります。スイッチのドキュメントを参照してください。

<!-- @os:end -->

<!-- @os:windows -->
### ネットワークリンク速度の確認

各マシンで、ネットワークインターフェースのリンク速度を確認します：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ethernetインターフェースが`Up`状態で`10 Gbps`で動作しているはずです：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**: 速度が`10 Gbps`より低い場合、またはリンクが確立されない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。スイッチによっては、オートネゴシエーションを無効にしてリンク速度を手動で設定する必要がある場合があります。スイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注意**: このステップはマシン1とマシン2の両方で実行してください。

2つのインストールオプションが利用可能です：

- [オプション1: Lemonade SDK（推奨）](#option-1-lemonade-sdk-recommended) - ビルド済みバイナリ、最速のセットアップ
- [オプション2: 手動ソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御してソースからビルド

### オプション1: Lemonade SDK（推奨）

Lemonade SDKは、AMD ROCm 7アクセラレーションを備えたllama.cppのナイトリービルドを提供しており、gfx1151（Strix Halo / Ryzen AI Max+ 395）などの最新のRadeonアーキテクチャをターゲットにしています。

<!-- @os:windows -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新リリースページに移動し、お使いのプラットフォームとGPUターゲットに合ったアーカイブをダウンロードします：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip`という名前のファイルをダウンロードします（`xxxx`はビルド番号です）。

#### ステップ2: バイナリの展開

ダウンロードしたアーカイブを解凍します：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、Ryzen AI Haloシステム向けにプリコンパイルされた、ROCm対応の`llama-cli.exe`、`llama-server.exe`、`rpc-server.exe`のビルドが含まれています。

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

最新リリースページに移動し、お使いのプラットフォームとGPUターゲットに合ったアーカイブをダウンロードします：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip`という名前のファイルをダウンロードします（`xxxx`はビルド番号です）。

#### ステップ2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、Ryzen AI Haloシステム向けにプリコンパイルされた、ROCm対応の`llama-cli`、`llama-server`、`rpc-server`のビルドが含まれています。

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
各ノードでllama.cppの準備が完了したら、[モデルのダウンロード](#downloading-the-model)に進んでください。

### オプション2: 手動ソースビルド

<!-- @os:windows -->
#### ステップ1: llama.cppのビルド

**x64 Native Tools Command Prompt**（Visual Studio Build Toolsとともにインストール）を開き、リポジトリをクローンします：

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIPをパスに追加し、ROCmおよびRPCサポートを有効にしてビルドします：

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIPソフトウェアスタックを有効にする |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効にする |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU（Radeon 8060s）をターゲットにする |
| `-G Ninja` | Ninjaビルドシステムを使用する |

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

上記のビルドステップでは、現在のセッションのみに`%HIP_PATH%\bin`が設定されます。HIPライブラリを任意のターミナル（x64 Native Tools Command Promptだけでなく）で利用可能にするには、ユーザーの`PATH`に永続的に追加します：

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

各ノードでllama.cppの準備が完了したら、[モデルのダウンロード](#downloading-the-model)に進んでください。
<!-- @os:end -->

<!-- @os:linux -->
#### ステップ1: llama.cppのビルド

リポジトリをクローンします：

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCmおよびRPCサポートを有効にしてビルドします：

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCmソフトウェアスタックを有効にする |
| `-DGGML_RPC=ON` | 分散推論のためのRPCを有効にする |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | AMD GPU上でのFlash Attentionを強化するためのrocWMMAを有効にする |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU（Radeon 8060s）をターゲットにする |

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

各ノードでllama.cppの準備が完了したら、[モデルのダウンロード](#downloading-the-model)に進んでください。
<!-- @os:end -->

## モデルのダウンロード

このPlaybookでは、[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)の`Q4_K_XL`量子化による358Bパラメータモデル[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)を使用します。この量子化では、モデルに約205GBのストレージが必要であり、2台のRyzen AI HaloノードのGPUメモリの合計に収まります。

Hugging Face CLIを使用してGGUFファイルをダウンロードします：
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

> **注意**: モデルのダウンロードはマシン1（コントローラー）で完了する必要があります。RPCワーカーノードにはモデルファイルのローカルコピーは必要ありません。

## クラスター上でのモデルの起動

llama.cppのRPC（Remote Procedure Call）エンジンにより、単一のllama.cppインスタンスがネットワーク経由でリモートワーカーにモデルレイヤーをオフロードできます。1台のマシンが**コントローラー**（マシン1）として機能し、トークン化、スケジューリング、オーケストレーションを処理します。もう1台のマシンは軽量な**RPCサーバー**（マシン2）を実行し、そのGPUメモリとコンピュートをコントローラーに公開します。

ロード時に、llama.cppは両ノードにまたがってモデルをシャーディングします。ロード後は、単一のアクセラレーター上で実行しているかのように推論が進みます。RPCはバックグラウンドでテンソル転送と同期を処理します。

### ステップ1: RPCサーバーの起動（マシン2）

マシン2で、RPCサーバーを起動してGPUリソースをコントローラーに公開します：
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
| `-c` | 大きなテンソルのローカルキャッシュを有効にし、モデルロード中の繰り返しネットワーク転送を回避する |
| `--host` | RPCサーバーをバインドするIPアドレス（すべてのインターフェースには`0.0.0.0`） |

その他のオプションについては、[llama.cpp RPCドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)を参照してください。

### ステップ2: モデルの起動（マシン1）

マシン2でRPCサーバーが実行されている状態で、`llama-cli`または`llama-server`を使用してマシン1から推論を起動します。

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

> **`<RPC_WORKER_IP>`の確認**: マシン2で`hostname -I | awk '{print $1}'`を実行して、ローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**: このコマンドはTerminal（Powershell）で実行してください。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>`の確認**: マシン2でTerminal（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行して、ローカルIPアドレスを確認します。

<!-- @os:end -->

実行すると、`llama-cli`はモデルのロード進捗を表示し、モデルと直接チャットできるインタラクティブなプロンプトに入ります：

![2つのノードにまたがってGLM 4.7を実行するllama-cli](assets/llama-cli-example.png)

#### llama-server

`llama-server`は、統合されたWeb UIとOpenAI互換のHTTP APIを備えた永続的なサーバープロセスを通じて、同じ推論エンジンを公開します。これは、長期実行デプロイメント、マルチユーザーアクセス、および外部ツールとの統合に適したインターフェースです。

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

> **`<RPC_WORKER_IP>`の確認**: マシン2で`hostname -I | awk '{print $1}'`を実行して、ローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**: このコマンドはTerminal（Powershell）で実行してください。

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

> **`<RPC_WORKER_IP>`の確認**: マシン2でTerminal（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行して、ローカルIPアドレスを確認します。
<!-- @os:end -->

起動後、ブラウザで`http://<HOST_IP>:8081`を開いて組み込みのWeb UIにアクセスします。これにより、モデルと対話するためのブラウザベースのチャットインターフェースが提供されます：

![2つのノードにまたがってGLM 4.7を実行するllama-server Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>`の確認**: マシン1で`hostname -I | awk '{print $1}'`を実行して、ローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>`の確認**: マシン1でTerminal（Powershell）にて`ipconfig | findstr /C:"IPv4"`を実行して、ローカルIPアドレスを確認します。
<!-- @os:end -->

#### パラメーターリファレンス

| フラグ | 目的 |
|------|---------|
| `-m` | GGUFモデルファイルへのパス（最初のシャード`00001-of-00005`を使用） |
| `-c` | トークン単位のコンテキストサイズ。値が大きいほどメモリを多く使用する |
| `-fa on` | AMD GPU上でのパフォーマンス向上のためにrocWMMA Flash Attentionを有効にする |
| `-ngl 999` | すべてのモデルレイヤーをGPUにオフロードする |
| `--no-mmap` | メモリマッピングを無効にし、モデルサイズがシステムRAMを超えるがVRAMに収まる場合のロード時間を短縮する |
| `--host` | `llama-server`をバインドするIP（`llama-server`のみ） |
| `--port` | HTTP APIを提供するポート（`llama-server`のみ） |
| `--rpc` | RPCワーカーエンドポイントのカンマ区切りリスト（`IP:port`） |

完全なパラメーターの使用方法については、[llama-cliドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)および[llama-serverドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)を参照してください。

## 次のステップ

- **サードパーティアプリケーションの接続**: `llama-server`はOpenAI互換のAPIを公開しています。OpenAI互換のアプリケーション（Open WebUIなど）を`http://<HOST_IP>:8081`に向け、任意のプレースホルダーAPIキー（例：`none`）を使用してクラスターに接続します
- **他のモデルの探索**: [Hugging Face](https://huggingface.co/models?search=gguf)で量子化されたGGUFを検索し、クラスターの合計GPUメモリに収まるモデルを見つけます
- **4ノードへのスケールアップ**: さらに2台のRyzen AI Haloシステムを追加のRPCワーカーとして追加し、1兆パラメータスケールのモデルにアクセスします。追加のエンドポイントをカンマ区切りリストとして`--rpc`に渡します（例：`--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`）