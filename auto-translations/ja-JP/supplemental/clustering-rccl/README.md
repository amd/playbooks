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

# RCCLを使用した2台のRyzen™ AI Haloのクラスタリング

## 概要

Ryzen™ AI Haloは、すでにローカルで大規模言語モデルを実行できる性能を備えています。クラスタリングを行うことで、これをさらに一歩進め、ローカルネットワーク経由で複数システムのGPUメモリを結合し、より強力な推論能力、優れたコード生成、より深い多言語理解を持つ、さらに大規模なモデルへのアクセスを、完全に自分自身のハードウェアだけで実現できます。

このプレイブックでは、RCCL(ROCm Communication Collectives Library)を使用してvLLM上で2台のRyzen AI Haloシステムをクラスタリングし、397BパラメータのモデルであるQwen3.5-397Bを、ROCmアクセラレーションを利用して両マシン上で実行する方法を解説します。

## このプレイブックで学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCm対応のvLLMの起動方法
- 2台のRyzen AI Haloシステム間でのマルチノードテンソル並列推論のためのRCCL設定
- 397Bパラメータのモデルを、ネットワーク接続された2台のRyzen AI Haloシステム上で実行する方法

## 前提条件

### ハードウェア

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要です。各ユニットはスイッチに直接配線され、スター型トポロジで接続されます。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスタを構成する計算ノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo間通信を可能にする中心スイッチ(ポートは最低2つ) |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続(Cat 7以上を推奨) |

> **注**: 2台のRyzen AI Haloユニットを接続するには、イーサネットスイッチのポートが2つ必要です。Haloユニットの1台からではなく、別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要になります。

### ソフトウェア
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: この手順は、マシン1とマシン2の両方で実施してください。

各Ryzen AI Haloユニットを、Cat 7(以上)のケーブルを使ってイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用する10Gbpsリンクが確立されます。

### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、控えておきます(以降の手順では`IFNAME`として参照します)。次を実行します。

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これにより、インターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認し、リンクがアクティブでフル速度で動作していることを確認します。

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: `<IFNAME>`は、[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)で得られた出力インターフェース名に置き換えてください。

`10000Mb/s`の速度が表示されるはずです。

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立されない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はお使いのスイッチのドキュメントを参照してください。

## VRAM割り当ての拡張

> **注**: この手順は、マシン1とマシン2の両方で実施してください。

### 大規模モデル実行のためのメモリ設定

Linux上では、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトではシステムメモリの半分に設定されています。

以下の手順に従ってカーネルのTranslation Table Manager(TTM)ページ設定を変更することで、この容量を増やすことができます。AMDでは、BIOSで専用VRAMの最小値(0.5 GB)を設定することを推奨しています。

* pipxユーティリティをインストールし、pipxでインストールされたwheelのパスをシステムの検索パスに追加します。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPIからamd-debug-tools wheelをインストールします。
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttmツールを実行し、共有メモリの現在の設定を確認します。
  ```bash
  amd-ttm
  ```

* 共有メモリ設定を**120 GB**に再設定します。
  ```bash
  amd-ttm --set 120
  ```

* 変更を反映させるため、システムを再起動します。

## vLLMコンテナの初期化

> **注**: この手順は、マシン1とマシン2の両方で実施してください。

お使いのRyzen AI Haloには、あらかじめビルドされたコンテナイメージ内にパッケージ化されたvLLMが同梱されています。これは、無料でオープンソースのコンテナツールであるPodmanを使って実行します。

### 1. モデルダウンロードディレクトリの作成

このプレイブックでQwen3.5-397Bモデルを提供すると、vLLMは自動的にモデルの重みをシステムにダウンロードします。これらの重みをコンテナ内からアクセスできるようにするため、まずコンテナがマウントできるモデルディレクトリを作成します。

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLMコンテナの起動

以下のコマンドは、コンテナを起動し、対話型シェルに入ります。先ほど作成したモデルディレクトリをマウントし、`IFNAME`を`NCCL_SOCKET_IFNAME`および`GLOO_SOCKET_IFNAME`に渡すことで、RCCL(vLLMがクラスタ全体でGPUを調整するために使用するライブラリ)がどのインターフェースを使用するかを指定します。

次のコマンドでコンテナを起動します。

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注**: `<IFNAME>`は、[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)で得られた出力インターフェース名に置き換えてください。

## クラスタ上でのモデルの実行

vLLMはRayを使ってクラスタをオーケストレーションし、RCCLを使ってノード間のGPU間通信を処理します。1台のマシンが**ヘッドノード**(マシン1)として動作し、推論を調整します。もう1台は**ワーカーノード**(マシン2)として参加し、そのGPUメモリと計算能力を提供します。

> **注**: RayはvLLMのオプションの依存関係であり、あらかじめ設定済みのPodmanコンテナ内からのみ利用可能です。

起動時、vLLMはテンソル並列を使用して両方のノードにモデルをシャーディングします。読み込みが完了すると、推論は単一のアクセラレータ上で実行されているかのように進行します。

#### RayによるOOMエラーの防止

デフォルトでは、Rayは各ノードのホストメモリを監視し、メモリ使用率が95%を超えると最も大きなプロセスを強制終了します。お使いのRyzen™ AI Haloでは、GPUとホストが1つのメモリプールを共有しているため、モデルの読み込みが`ray.exceptions.OutOfMemoryError`を引き起こし、ワーカープロセスを強制終了させてしまうことがあります。

これを防ぐため、クラスタの起動および参加を行う前に、各マシンで`RAY_memory_monitor_refresh_ms=0`をエクスポートします。
### ステップ1: Ray ヘッドノードを起動する(マシン1)

マシン1で、クラスターを初期化するために Ray ヘッドノードを起動します。

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` の確認方法**: マシン1で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認してください。

### ステップ2: クラスターに参加する(マシン2)

マシン2で、ヘッドノードに接続してクラスターを形成します。

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` の確認方法**: マシン2で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認してください。

### ステップ3: モデルを配信する(マシン1)

マシン1で、vLLM サーバーを起動します。これによりモデルが自動的にダウンロードされ、両方のノードにまたがって配信が開始されます。

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### パラメータリファレンス

| フラグ | 用途 |
|------|---------|
| `--port` | HTTP API を配信するポート |
| `--host` | サーバーをバインドする IP アドレス(すべてのインターフェースの場合は `0.0.0.0`) |
| `--max-model-len` | 最大コンテキスト長(トークン数) |
| `--gpu-memory-utilization` | 割り当てる GPU メモリの割合(0.0〜1.0) |
| `--dtype` | モデルの重みのデータ型 |
| `--tensor-parallel-size` | モデルを分割する GPU の数(クラスター内の GPU 総数を設定) |
| `--distributed-executor-backend` | マルチノード実行のバックエンド(クラスターデプロイの場合は `ray`) |
| `--enforce-eager` | 互換性のために CUDA グラフのコンパイルを無効化 |
| `--language-model-only` | 補助的なモデルコンポーネント(視覚エンコーダーなど)の読み込みをスキップ |
| `--reasoning-parser` | モデルの構造化推論出力パーシングを有効化 |

パラメータの完全な使用方法については、[vLLM ドキュメント](https://docs.vllm.ai/en/latest/configuration/engine_args/)を参照してください。

## モデルへのアクセス

vLLM は OpenAI 互換の API を公開しているため、対応する任意のクライアントやインターフェースをクラスターに接続できます。よく使われる選択肢の1つが [Open WebUI](https://github.com/open-webui/open-webui) で、ブラウザベースのチャットインターフェースを提供します。

Open WebUI を vLLM エンドポイントに接続するには:

1. **設定** > **管理者パネル** > **接続** を開きます
2. **OpenAI API 接続の管理** で **+** をクリックします
3. **接続タイプ** を **外部** に設定します
4. **URL** を `http://<MACHINE_1_IP>:7000/v1` に設定します
5. **認証** で、ドロップダウンから **なし** を選択します
6. **モデル ID** は空欄のままにして、エンドポイントからすべてのモデルを自動検出させます

> **`<MACHINE_1_IP>` の確認方法**: マシン1で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認してください。マシン1自体から Open WebUI にアクセスする場合は、`http://localhost:7000/v1` を使用できます。

![vLLM エンドポイント用の Open WebUI 接続設定](assets/openwebui-connection.png)

接続が完了したら、Open WebUI のモデルドロップダウンからモデルを選択し、チャットを開始します。これでモデルは、両方の Ryzen AI Halo ノードにまたがって実行されるようになりました。

![Open WebUI で Qwen3.5-397B とチャットする様子](assets/openwebui-chat.png)

## 次のステップ

- **他のモデルを試す**: クラスターの合計 GPU メモリに収まる新しいモデルを [Hugging Face](https://huggingface.co/models?&sort=trending) で探してみましょう
- **4ノードへのスケール**: さらに2台の Ryzen AI Halo システムを追加の Ray ワーカーとして加え、より多くの GPU にわたってモデルを分割します。これには、各ノードにつき1ポートずつ、最低4ポートを備えたイーサネットスイッチが必要です。追加する各ワーカーで [ステップ2: クラスターに参加する](#step-2-join-the-cluster-machine-2) の手順に従い、それに応じて `--tensor-parallel-size` を増やしてください
- **他の並列化戦略を試す**: vLLM は、mixture-of-experts モデル向けの[エキスパート並列](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)や、より高いスループットのための[データ並列](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)をサポートしています。`--enable-expert-parallel` や `--data-parallel-size` を試して、ワークロードに最適な構成を見つけてください