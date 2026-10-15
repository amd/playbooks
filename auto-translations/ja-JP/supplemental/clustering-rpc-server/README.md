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

Ryzen™ AI Haloは、既にローカルで大規模言語モデルを実行できる能力を備えています。クラスタリングでは、これをさらに一歩進め、複数のシステムのGPUメモリをローカルネットワーク経由で結合することで、より優れた推論能力、コード生成能力、そしてより深い多言語理解力を持つ、さらに大規模なモデルへのアクセスを可能にします。すべては、お手持ちのハードウェアだけで実現できます。

このプレイブックでは、llama.cppのRPCエンジンを使用して2台のRyzen AI Haloシステムをクラスタリングし、AMD ROCm™アクセラレーションを活用して358BパラメータのモデルであるGLM 4.7を両マシン上で実行する方法を解説します。

## 学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmおよびRPCサポート付きのllama.cppのインストール
- RPCワーカーの設定と2ノード間での分散推論の起動
- 2台のネットワーク接続されたRyzen AI Haloシステムにまたがる358Bパラメータのモデルの実行

## メモリ構成の設定

> **注**: この手順はマシン1とマシン2の両方で完了してください。

<!-- @os:windows -->
Windowsでは、より多くのメモリを必要とする大規模モデルを実行するために、AMD Variable Graphics Memory（iGPU VRAM）の割り当てを使用する必要があります。

これは、AMD Software: Adrenalin Editionコントロールパネルを開き、`Performance > Tuning > AMD Variable Graphics Memory` に移動することで設定できます。値を**96 GB**に設定してください。変更を反映させるには、システムを再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順に従ってカーネルのTranslation Table Manager（TTM）のページ設定を変更することで増やすことができます。AMDでは、BIOSで最小専用VRAMを設定することを推奨しています（0.5 GB）。

* pipxユーティリティをインストールし、pipxでインストールされたwheelのパスをシステムの検索パスに追加します。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPIからamd-debug-tools wheelをインストールします。
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttmツールを実行して、共有メモリの現在の設定を照会します。
  ```bash
  amd-ttm
  ```

* 共有メモリ設定を**120 GB**に再構成します。
  ```bash
  amd-ttm --set 120
  ```

* 変更を反映させるには、システムを再起動してください。


<!-- @os:end -->
<!-- @device:halo_box -->
## ソフトウェアの更新確認

<!-- @require:software-update -->
<!-- @device:end -->
## 前提条件

### ハードウェア

このプレイブックでは、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要であり、各ユニットをスイッチに直接接続するスター型トポロジで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスタを構成する計算ノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo間の通信を可能にする中央スイッチ（少なくとも2ポート） |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続します（Cat 7以上を推奨） |

> **注**: 2台のRyzen AI Haloユニットを接続するには、イーサネットスイッチの2ポートが必要です。Haloユニットの一方ではなく別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
以下をインストールしてください:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++**ワークロード付きの[Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: この手順はマシン1とマシン2の両方で完了してください。

各Ryzen AI HaloユニットをCat 7（以上）のケーブルを使用してイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。
<!-- @os:linux -->
### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、書き留めておきます（以下では`IFNAME`として参照します）。以下を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これによりインターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブで、フルスピードで動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>` は[1. ネットワークインターフェースの確認](#1-ネットワークインターフェースの確認)の出力インターフェース名に置き換えてください

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にしてリンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

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

> **注**: 速度が`10 Gbps`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にしてリンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

<!-- @os:end -->

## llama.cppのインストール

> **注**: この手順はマシン1とマシン2の両方で完了してください。

2つのインストールオプションが利用可能です:

- [オプション1: Lemonade SDK（推奨）](#option-1-lemonade-sdk-recommended) - ビルド済みバイナリで最速のセットアップ
- [オプション2: 手動ソースビルド](#option-2-manual-source-build) - ビルドフラグを完全に制御しながらソースからビルド

### オプション1: Lemonade SDK（推奨）

Lemonade SDKは、gfx1151（Strix Halo / Ryzen AI Max+ 395）などのGPUや他の最新のRadeonアーキテクチャを対象とした、AMD ROCm 7アクセラレーション付きのllama.cppのナイトリービルドを提供します。

<!-- @os:windows -->
#### ステップ1: ビルド済みバイナリのダウンロード

最新のリリースページに移動し、お使いのプラットフォームと GPU ターゲットに合ったアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip`(`xxxx` はビルド番号)という名前のファイルをダウンロードします。

#### ステップ2: バイナリの展開

ダウンロードしたアーカイブを解凍します。

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

このディレクトリには、Ryzen AI Halo システム向けにあらかじめコンパイルされた、ROCm 対応の `llama-cli.exe`、`llama-server.exe`、`rpc-server.exe` のビルドが含まれています。

#### ステップ3: GPU 検出の確認

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

最新のリリースページに移動し、お使いのプラットフォームと GPU ターゲットに合ったアーカイブをダウンロードします。

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip`(`xxxx` はビルド番号)という名前のファイルをダウンロードします。

#### ステップ2: バイナリの展開と準備

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

このディレクトリには、Ryzen AI Halo システム向けにあらかじめコンパイルされた、ROCm 対応の `llama-cli`、`llama-server`、`rpc-server` のビルドが含まれています。

#### ステップ3: GPU 検出の確認

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
各ノードで llama.cpp の準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進んでください。

### オプション2: 手動でのソースビルド

<!-- @os:windows -->
#### ステップ1: llama.cpp のビルド

**x64 Native Tools Command Prompt**(Visual Studio Build Tools に付属)を開き、リポジトリをクローンします。

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
| `-DGGML_RPC=ON` | 分散推論向けの RPC を有効化 |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU(Radeon 8060s)をターゲット化 |
| `-G Ninja` | Ninja ビルドシステムを使用 |

#### ステップ2: GPU 検出の確認

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

#### ステップ3: HIP をユーザーパスに追加

上記のビルド手順では、現在のセッションのみ `%HIP_PATH%\bin` を設定しました。（x64 Native Tools Command Prompt だけでなく)任意のターミナルで HIP ライブラリを利用できるようにするには、ユーザーの `PATH` に永続的に追加します。

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

各ノードで llama.cpp の準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進んでください。
<!-- @os:end -->

<!-- @os:linux -->
#### ステップ1: llama.cpp のビルド

リポジトリをクローンします。

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCm と RPC のサポートを有効にしてビルドします。

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| ビルドフラグ | 目的 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm ソフトウェアスタックを有効化 |
| `-DGGML_RPC=ON` | 分散推論向けの RPC を有効化 |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU(Radeon 8060s)をターゲット化 |

その他のビルドオプションについては、[llama.cpp のビルドドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)を参照してください。

#### ステップ2: GPU 検出の確認

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

各ノードで llama.cpp の準備が整ったら、[モデルのダウンロード](#downloading-the-model)に進んでください。
<!-- @os:end -->

## モデルのダウンロード

このプレイブックでは、[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) が提供する `Q4_K_XL` 量子化版の 358B パラメータモデルである [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) を使用します。この量子化レベルでは、モデルは約 205GB のストレージを必要とし、2 台の Ryzen AI Halo ノードの合計 GPU メモリに収まります。

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

> **注**: モデルのダウンロードは、マシン1(コントローラー)上で完了させる必要があります。RPC ワーカーノードには、モデルファイルのローカルコピーは不要です。

## クラスターでのモデルの起動

llama.cpp の RPC(Remote Procedure Call)エンジンを使用すると、単一の llama.cpp インスタンスが、ネットワーク経由でモデルレイヤーをリモートワーカーにオフロードできます。1台のマシンが**コントローラー**(マシン1)として動作し、トークン化、スケジューリング、オーケストレーションを処理します。もう1台のマシンは軽量な **RPC サーバー**(マシン2)を実行し、その GPU メモリと演算能力をコントローラーに公開します。

読み込み時、llama.cpp はモデルを両方のノードにシャーディングします。読み込みが完了すると、推論は単一のアクセラレータ上で実行されているかのように進行します。RPC はテンソル転送と同期を裏側で処理します。

### ステップ1: RPC サーバーの起動(マシン2)

マシン2で、GPU リソースをコントローラーに公開するために RPC サーバーを起動します。
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
| `-c` | 大きなテンソル用のローカルキャッシュを有効化し、モデルの読み込み中にネットワーク転送が繰り返されるのを回避 |
| `--host` | RPC サーバーをバインドする IP アドレス(すべてのインターフェースの場合は `0.0.0.0`) |

その他のオプションについては、[llama.cpp RPC ドキュメント](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)を参照してください。

### ステップ2: モデルの起動(マシン1)

マシン2で RPC サーバーが実行されている状態で、マシン1から `llama-cli` または `llama-server` を使用して推論を起動します。

#### llama-cli

`llama-cli` は、モデルと直接対話するためのターミナルベースのインターフェースを提供します。ベンチマーク、デバッグ、低レベルな実験に最適です。

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

> **`<RPC_WORKER_IP>` の確認方法**: マシン2で `hostname -I | awk '{print $1}'` を実行して、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル(Powershell)で実行してください。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` の確認方法**: マシン2でターミナル(Powershell)にて `ipconfig | findstr /C:"IPv4"` を実行して、そのローカル IP アドレスを確認します。

<!-- @os:end -->

実行が開始されると、`llama-cli` はモデルの読み込み進捗を表示し、モデルと直接チャットできる対話型プロンプトに入ります。

![2ノードにまたがって GLM 4.7 を実行している llama-cli](assets/llama-cli-example.png)
#### llama-server

`llama-server` は同じ推論エンジンを、統合された Web UI と OpenAI 互換の HTTP API を備えた永続的なサーバープロセスとして公開します。これは、長時間稼働するデプロイメント、マルチユーザーアクセス、外部ツールとの統合に適したインターフェースです。

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

> **`<RPC_WORKER_IP>` の確認方法**: Machine 2 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: このコマンドはターミナル (Powershell) で実行してください。

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

> **`<RPC_WORKER_IP>` の確認方法**: Machine 2 でターミナル (Powershell) にて `ipconfig | findstr /C:"IPv4"` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

起動後、ブラウザで `http://<HOST_IP>:8081` を開くと、組み込みの Web UI にアクセスできます。これにより、モデルとやり取りするためのブラウザベースのチャットインターフェースが提供されます。

![2 つのノードにまたがって GLM 4.7 を実行している llama-server Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` の確認方法**: Machine 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` の確認方法**: Machine 1 でターミナル (Powershell) にて `ipconfig | findstr /C:"IPv4"` を実行し、そのローカル IP アドレスを確認します。
<!-- @os:end -->

#### パラメーターリファレンス

| フラグ | 用途 |
|------|---------|
| `-m` | GGUF モデルファイルへのパス (最初のシャード `00001-of-00005` を使用) |
| `-c` | トークン単位のコンテキストサイズ。値が大きいほどメモリ使用量が増加します |
| `-fa on` | AMD GPU 上でのパフォーマンスを向上させる rocWMMA Flash Attention を有効化します |
| `-ngl 999` | すべてのモデルレイヤーを GPU にオフロードします |
| `-lm none` | モデルのロードモードを `none` に設定し、メモリマッピングを無効化することで、モデルサイズがシステム RAM を超えるが VRAM には収まる場合のロード時間を短縮します |
| `--host` | `llama-server` をバインドする IP (`llama-server` 専用) |
| `--port` | HTTP API を提供するポート (`llama-server` 専用) |
| `--rpc` | RPC ワーカーエンドポイントのカンマ区切りリスト (`IP:port`) |

パラメーターの詳細な使用方法については、[llama-cli documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) および [llama-server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) を参照してください。

## 次のステップ

- **サードパーティアプリケーションとの接続**: `llama-server` は OpenAI 互換の API を公開します。任意の OpenAI 互換アプリケーション (Open WebUI など) を、任意のプレースホルダー API キー (例: `none`) とともに `http://<HOST_IP>:8081` に接続することで、クラスターに接続できます
- **他のモデルの探索**: [Hugging Face](https://huggingface.co/models?search=gguf) で量子化された GGUF を閲覧し、クラスターの合計 GPU メモリに収まるモデルを探してください
- **4 ノードへのスケール**: さらに 2 台の Ryzen AI Halo システムを追加の RPC ワーカーとして追加することで、1 兆パラメーター規模のモデルにアクセスできます。追加のエンドポイントは、カンマ区切りのリストとして `--rpc` に渡します (例: `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)