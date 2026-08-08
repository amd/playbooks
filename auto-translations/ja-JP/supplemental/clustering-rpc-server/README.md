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

# RPCを使用した2台のRyzen™ AI Haloのクラスタリング

## 概要

Ryzen™ AI Haloは、すでにローカルで大規模言語モデルを実行できます。クラスタリングを行うことで、複数のシステムのGPUメモリをローカルネットワーク経由で結合し、より優れた推論能力、コード生成能力、そしてより深い多言語理解を備えた、さらに大規模なモデルを、すべて自分自身のハードウェア上で利用できるようになります。

このプレイブックでは、llama.cppのRPCエンジンを使用して2台のRyzen AI Haloシステムをクラスタリングし、AMD ROCm™アクセラレーションを使用して、358BパラメータのモデルであるGLM 4.7を両方のマシンにまたがって実行する方法を説明します。

## このプレイブックで学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmおよびRPCサポートを備えたllama.cppのインストール
- RPCワーカーの設定と、2ノード間での分散推論の起動
- ネットワーク接続された2台のRyzen AI Haloシステムにまたがる358Bパラメータモデルの実行

## メモリ設定の変更

> **注**: この手順はマシン1とマシン2の両方で実行してください。

<!-- @os:windows -->
Windowsで、より高いメモリを必要とする大規模なモデルを実行するには、AMD Variable Graphics Memory（iGPU VRAM）割り当てを使用する必要があります。

これは、AMD Software: Adrenalin Editionコントロールパネルを開き、`Performance > Tuning > AMD Variable Graphics Memory`に移動することで設定できます。値を**96 GB**に設定してください。変更を有効にするには、システムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順に従ってカーネルのTranslation Table Manager（TTM）のページ設定を変更することで増やすことができます。AMDは、BIOSで最小専用VRAMを設定することを推奨しています（0.5 GB）。

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

* 共有メモリ設定を**120 GB**に再設定します。
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

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットをスイッチに直接接続するスター型トポロジで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスターを構成するコンピュートノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo間通信を可能にする中央スイッチ（2ポート以上必要） |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続します（Cat 7以上を推奨） |

> **注**: 2台のRyzen AI Haloユニットを接続するには、イーサネットスイッチのポートが2つ必要です。Haloユニットのいずれかからではなく、別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要になります。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください：
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

> **注**: この手順はマシン1とマシン2の両方で実行してください。

Cat 7（またはそれ以上）のケーブルを使用して、各Ryzen AI Haloユニットをイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、書き留めておきます（以下では`IFNAME`として参照されます）。次を実行します：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これにより、インターフェース名が直接表示されます。例：

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブでフル速度で動作していることを確認します：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>`を、[1. ネットワークインターフェースの確認](#1-ネットワークインターフェースの確認)からの出力インターフェース名に置き換えてください。

`10000Mb/s`の速度が表示されるはずです：

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合や、リンクが確立されない場合は、ケーブルの接続を確認し、スイッチのポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

<!-- @os:windows -->
### ネットワークリンク速度の確認

各マシンで、ネットワークインターフェースのリンク速度を確認します：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

イーサネットインターフェースは`Up`で、`10 Gbps`で動作しているはずです：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注**: 速度が`10 Gbps`より低い場合や、リンクが確立されない場合は、ケーブルの接続を確認し、スイッチのポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注**: この手順はマシン1とマシン2の両方で実行してください。

2つのインストールオプションが利用可能です：

- [オプション1: Lemonade SDK（推奨）](#option-1-lemonade-sdk-recommended) - 事前ビルド済みバイナリ、最速のセットアップ
- [オプション2: 手動によるソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御しながらソースからビルド

### オプション1: Lemonade SDK（推奨）

Lemonade SDKは、AMD ROCm 7アクセラレーションを備えたllama.cppのナイトリービルドを提供しており、gfx1151（Strix Halo / Ryzen AI Max+ 395）などのGPUや、その他の最近のRadeonアーキテクチャを対象としています。

<!-- @os:windows -->
#### ステップ 1: ビルド済みバイナリのダウンロード

最新リリースページに移動し、お使いのプラットフォームと GPU ターゲットに一致するアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip`（`xxxx` はビルド番号）という名前のファイルをダウンロードします。

#### ステップ 2: バイナリの展開

ダウンロードしたアーカイブを解凍します。

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、Ryzen AI Halo システム向けにプリコンパイルされた ROCm 対応の `llama-cli.exe`、`llama-server.exe`、`rpc-server.exe` のビルドが含まれています。

#### ステップ 3: GPU 検出の確認

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
#### ステップ 1: ビルド済みバイナリのダウンロード

最新リリースページに移動し、お使いのプラットフォームと GPU ターゲットに一致するアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip`（`xxxx` はビルド番号）という名前のファイルをダウンロードします。

#### ステップ 2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、Ryzen AI Halo システム向けにプリコンパイルされた ROCm 対応の `llama-cli`、`llama-server`、`rpc-server` のビルドが含まれています。

#### ステップ 3: GPU 検出の確認

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
各ノードで llama.cpp の準備が整ったら、[モデルのダウンロード](#downloading-the-model) に進んでください。

### オプション 2: 手動ソースビルド

<!-- @os:windows -->
#### ステップ 1: llama.cpp のビルド

**x64 Native Tools Command Prompt**（Visual Studio Build Tools と共にインストールされます）を開き、リポジトリをクローンします。

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIP をパスに追加し、ROCm と RPC のサポートを有効にしてビルドします。

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIP ソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のための RPC を有効化 |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU（Radeon 8060s）をターゲット |
| `-G Ninja` | Ninja ビルドシステムを使用 |

#### ステップ 2: GPU 検出の確認

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

#### ステップ 3: HIP をユーザーパスに追加

上記のビルド手順では、現在のセッションでのみ `%HIP_PATH%\bin` を設定しています。（x64 Native Tools Command Prompt に限らず）任意のターミナルで HIP ライブラリを利用できるようにするには、ユーザーの `PATH` に恒久的に追加します。

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

各ノードで llama.cpp の準備が整ったら、[モデルのダウンロード](#downloading-the-model) に進んでください。
<!-- @os:end -->

<!-- @os:linux -->
#### ステップ 1: llama.cpp のビルド

リポジトリをクローンします。

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCm と RPC のサポートを有効にしてビルドします。

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm ソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論のための RPC を有効化 |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | AMD GPU での Flash Attention 強化のために rocWMMA を有効化 |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU（Radeon 8060s）をターゲット |

その他のビルドオプションについては、[llama.cpp ビルドドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) を参照してください。

#### ステップ 2: GPU 検出の確認

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

各ノードで llama.cpp の準備が整ったら、[モデルのダウンロード](#downloading-the-model) に進んでください。
<!-- @os:end -->

## モデルのダウンロード

このプレイブックでは、[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) が提供する `Q4_K_XL` 量子化版の 358B パラメータモデルである [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) を使用します。この量子化では、モデルはおよそ 205GB のストレージを必要とし、2 台の Ryzen AI Halo ノードの合計 GPU メモリに収まります。

Hugging Face CLI を使用して GGUF ファイルをダウンロードします。
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

> **注**: モデルのダウンロードはマシン 1（コントローラー）で完了させる必要があります。RPC ワーカーノードには、モデルファイルのローカルコピーは必要ありません。

## クラスター上でのモデルの起動

llama.cpp の RPC（リモートプロシージャコール）エンジンを使用すると、単一の llama.cpp インスタンスが、ネットワーク経由でモデルレイヤーをリモートワーカーにオフロードできます。1 台のマシンが**コントローラー**（マシン 1）として動作し、トークン化、スケジューリング、オーケストレーションを処理します。もう 1 台のマシン（マシン 2）は、軽量な **RPC サーバー**を実行し、その GPU メモリと計算能力をコントローラーに公開します。

ロード時に、llama.cpp はモデルを両ノードにわたってシャーディングします。ロードが完了すると、推論は単一のアクセラレータ上で実行しているかのように進行します。RPC は、その裏でテンソルの転送と同期を処理します。

### ステップ 1: RPC サーバーの起動（マシン 2）

マシン 2 で RPC サーバーを起動し、その GPU リソースをコントローラーに公開します。
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
| `-p` | RPC サーバーをブロードキャストするポート |
| `-c` | 大きなテンソル用のローカルキャッシュを有効にし、モデルロード時のネットワーク転送の繰り返しを回避 |
| `--host` | RPC サーバーをバインドする IP アドレス（すべてのインターフェースの場合は `0.0.0.0`） |

その他のオプションについては、[llama.cpp RPC ドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md) を参照してください。

### ステップ 2: モデルの起動（マシン 1）

マシン 2 で RPC サーバーが実行された状態で、マシン 1 から `llama-cli` または `llama-server` のいずれかを使用して推論を起動します。

#### llama-cli

`llama-cli` は、モデルと直接対話するためのターミナルベースのインターフェースを提供します。ベンチマーク、デバッグ、低レベルの実験に最適です。

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

> **`<RPC_WORKER_IP>` の確認方法**: マシン 2 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル（PowerShell）で実行してください。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` の確認方法**: マシン 2 でターミナル（PowerShell）で `ipconfig | findstr /C:"IPv4"` を実行し、そのローカル IP アドレスを確認します。

<!-- @os:end -->

実行されると、`llama-cli` はモデルのロード進捗を表示し、モデルと直接対話できるインタラクティブなプロンプトに入ります。

![2 つのノードにまたがって GLM 4.7 を実行する llama-cli](assets/llama-cli-example.png)
#### llama-server

`llama-server` は、統合Web UIとOpenAI互換のHTTP APIを備えた永続的なサーバープロセスを通じて、同じ推論エンジンを公開します。これは、長時間稼働するデプロイ、マルチユーザーアクセス、外部ツールとの連携において好ましいインターフェースです。

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

> **`<RPC_WORKER_IP>` の確認方法**: マシン2で `hostname -I | awk '{print $1}'` を実行し、そのローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはTerminal(Powershell)で実行してください。

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

> **`<RPC_WORKER_IP>` の確認方法**: マシン2でTerminal(Powershell)にて `ipconfig | findstr /C:"IPv4"` を実行し、そのローカルIPアドレスを確認します。
<!-- @os:end -->

起動したら、ブラウザで `http://<HOST_IP>:8081` を開き、組み込みのWeb UIにアクセスします。これにより、モデルと対話するためのブラウザベースのチャットインターフェースが提供されます:

![2ノードでGLM 4.7を実行するllama-server Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` の確認方法**: マシン1で `hostname -I | awk '{print $1}'` を実行し、そのローカルIPアドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` の確認方法**: マシン1でTerminal(Powershell)にて `ipconfig | findstr /C:"IPv4"` を実行し、そのローカルIPアドレスを確認します。
<!-- @os:end -->

#### パラメータリファレンス

| フラグ | 目的 |
|------|---------|
| `-m` | GGUFモデルファイルへのパス(最初のシャード `00001-of-00005` を使用) |
| `-c` | トークン単位のコンテキストサイズ。値が大きいほどメモリ使用量が増加します |
| `-fa on` | AMD GPUでのパフォーマンス向上のためrocWMMA Flash Attentionを有効化します |
| `-ngl 999` | すべてのモデルレイヤーをGPUにオフロードします |
| `--no-mmap` | メモリマッピングを無効化し、モデルサイズがシステムRAMを超えるがVRAMには収まる場合の読み込み時間を短縮します |
| `--host` | `llama-server` をバインドするIP(`llama-server` のみ) |
| `--port` | HTTP APIを提供するポート(`llama-server` のみ) |
| `--rpc` | RPCワーカーエンドポイント(`IP:port`)のカンマ区切りリスト |

完全なパラメータの使用方法については、[llama-cliドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)および[llama-serverドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)を参照してください。

## 次のステップ

- **サードパーティアプリケーションの接続**: `llama-server` はOpenAI互換のAPIを公開します。OpenAI互換の任意のアプリケーション(Open WebUIなど)を `http://<HOST_IP>:8081` に向け、任意のプレースホルダーAPIキー(例: `none`)を使用することで、クラスターに接続できます
- **他のモデルを探索する**: [Hugging Face](https://huggingface.co/models?search=gguf) で量子化されたGGUFを閲覧し、クラスターの合計GPUメモリに収まるモデルを見つけてください
- **4ノードへのスケール**: Ryzen AI Haloシステムをさらに2台追加のRPCワーカーとして追加することで、1兆パラメータ規模のモデルにアクセスできます。`--rpc` にカンマ区切りリストとして追加のエンドポイントを渡してください(例: `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)