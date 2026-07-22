<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている可能性があり、一部の手順、コマンド、ダウンロード、または製品の提供状況がお住まいの言語や地域と異なる場合があります。おかしな点がございましたら、英語版のプレイブックを正としてご参照ください。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->

> [!IMPORTANT]
> このプレイブックでは、GitHub がレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) にアクセスしてください。
<!-- @github-only:end -->

# RCCL を使用した 2 台の Ryzen™ AI Halo のクラスタリング

## 概要

Ryzen™ AI Halo は、すでにローカルで大規模言語モデルを実行できる能力を備えています。クラスタリングは、これをさらに進化させ、複数のシステムの GPU メモリをローカルネットワーク経由で結合することで、より強力な推論能力、より優れたコード生成、より深い多言語理解を備えた、さらに大規模なモデルへのアクセスを可能にします。しかもこれらはすべて、お手元のハードウェア上で完結します。

このプレイブックでは、RCCL(ROCm Communication Collectives Library)を使用して vLLM とともに 2 台の Ryzen AI Halo システムをクラスタリングし、397B パラメータのモデルである Qwen3.5-397B を、ROCm アクセラレーションを利用しながら両方のマシンにまたがって実行する方法を学びます。

## 学習内容

- Ryzen AI Halo システムにおける VRAM 割り当ての拡張方法
- ROCm サポートを使用した vLLM の起動方法
- 2 台の Ryzen AI Halo システム間でのマルチノードテンソル並列推論のための RCCL の構成方法
- ネットワーク接続された 2 台の Ryzen AI Halo システムにまたがる 397B パラメータモデルの実行方法

## 前提条件

### ハードウェア

このプレイブックには、2 台の Ryzen AI Halo ユニットと 1 台のイーサネットスイッチが必要です。各ユニットはスイッチに直接接続され、スター型トポロジで構成されます。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスタを構成するコンピュートノード |
| 10Gbps イーサネットスイッチ | 1 | 複数ノードの Ryzen AI Halo 間通信を可能にする中央スイッチ(最低 2 ポート必要) |
| イーサネットケーブル | 2 | 各 Halo ユニットをスイッチに接続します(Cat 7 以上を推奨) |

> **注記**: 2 台の Ryzen AI Halo ユニットを接続するには、イーサネットスイッチのポートが 2 つ必要です。Halo ユニットのいずれかからではなく、別のクライアントマシンからモデルにアクセスする場合は、3 つ目のポートが必要になります。

### ソフトウェア
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注記**: この手順は、マシン 1 とマシン 2 の両方で実施してください。

Cat 7(以上)ケーブルを使用して、各 Ryzen AI Halo ユニットをイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される 10Gbps リンクが確立されます。

### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、書き留めておきます(以降の手順ではこれを `IFNAME` として参照します)。次を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これにより、インターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認し、リンクがアクティブでフル速度で動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注記**: `<IFNAME>` は、[1. ネットワークインターフェースの確認](#1-ネットワークインターフェースの確認) で得られた出力インターフェース名に置き換えてください。

速度が `10000Mb/s` と表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注記**: 速度が `10000Mb/s` より低い場合、またはリンクが確立しない場合は、ケーブルの接続を確認し、スイッチのポートが 10Gbps に設定されていることを確認してください。一部のスイッチでは、オートネゴシエーションを無効化し、リンク速度を手動で設定する必要があります。詳細はお使いのスイッチのドキュメントを参照してください。

## VRAM 割り当ての拡張

> **注記**: この手順は、マシン 1 とマシン 2 の両方で実施してください。

### 大規模モデル実行のためのメモリ構成

Linux 上では、ROCm は共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順に従ってカーネルの Translation Table Manager(TTM)のページ設定を変更することで増やすことができます。AMD は、BIOS で専用 VRAM の最小値(0.5 GB)を設定することを推奨します。

* pipx ユーティリティをインストールし、pipx でインストールされた wheel のパスをシステムのサーチパスに追加します。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI から amd-debug-tools の wheel をインストールします。
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttm ツールを実行して、共有メモリの現在の設定を確認します。
  ```bash
  amd-ttm
  ```

* 共有メモリの設定を **120 GB** に再構成します:
  ```bash
  amd-ttm --set 120
  ```

* 変更を反映させるためにシステムを再起動します。

## vLLM コンテナの初期化

> **注記**: この手順は、マシン 1 とマシン 2 の両方で実施してください。

お使いの Ryzen AI Halo には、事前ビルド済みのコンテナイメージ内にパッケージ化された vLLM が同梱されています。これは、無料のオープンソースコンテナツールである Podman を使用して実行します。

### 1. モデルダウンロードディレクトリの作成

このプレイブックで Qwen3.5-397B モデルを提供する際、vLLM はモデルの重みをシステムに自動的にダウンロードします。これらの重みがコンテナ内からアクセス可能であることを確実にするため、まずコンテナがマウントできる models ディレクトリを作成します:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM コンテナの起動

以下のコマンドは、コンテナを起動し、インタラクティブシェルに入ります。先ほど作成した models ディレクトリをマウントし、`IFNAME` を `NCCL_SOCKET_IFNAME` と `GLOO_SOCKET_IFNAME` に渡すことで、RCCL(vLLM がクラスタ全体で GPU を調整するために使用するライブラリ)にどのインターフェースを使用するかを伝えます。

以下でコンテナを起動します:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注記**: `<IFNAME>` は、[1. ネットワークインターフェースの確認](#1-ネットワークインターフェースの確認) で得られた出力インターフェース名に置き換えてください。

## クラスタでのモデルの実行

vLLM は、クラスタのオーケストレーションに Ray を、ノード間の GPU 対 GPU 通信の処理に RCCL を使用します。1 台のマシンが**ヘッドノード**(マシン 1)として機能し、推論を調整します。もう 1 台は**ワーカーノード**(マシン 2)として参加し、その GPU メモリと計算能力を提供します。

> **注記**: Ray は vLLM のオプションの依存関係であり、事前構成済みの Podman コンテナ内からのみ利用可能です。

起動時に、vLLM はテンソル並列を使用してモデルを両方のノードにまたがってシャーディングします。読み込みが完了すると、推論は単一のアクセラレータ上で実行しているかのように進行します。

### ステップ 1: Ray ヘッドノードの起動(マシン 1)

マシン 1 で、クラスタを初期化するために Ray ヘッドノードを起動します:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` の確認方法**: マシン 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。
### ステップ2: クラスターに参加する(マシン2)

マシン2で、ヘッドノードに接続してクラスターを形成します:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` の確認方法**: マシン2で `hostname -I | awk '{print $1}'` を実行すると、そのローカルIPアドレスを確認できます。

### ステップ3: モデルを提供する(マシン1)

マシン1で、vLLMサーバーを起動します。これにより、モデルが自動的にダウンロードされ、両方のノードにわたって提供が開始されます:

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

| フラグ | 目的 |
|------|---------|
| `--port` | HTTP APIを提供するポート |
| `--host` | サーバーをバインドするIPアドレス(すべてのインターフェースの場合は `0.0.0.0`) |
| `--max-model-len` | トークン単位の最大コンテキスト長 |
| `--gpu-memory-utilization` | 割り当てるGPUメモリの割合(0.0~1.0) |
| `--dtype` | モデルの重みのデータ型 |
| `--tensor-parallel-size` | モデルを分割するGPUの数(クラスター内の合計GPU数に設定) |
| `--distributed-executor-backend` | マルチノード実行用のバックエンド(クラスターデプロイメントの場合は `ray`) |
| `--enforce-eager` | 互換性のためにCUDAグラフのコンパイルを無効化 |
| `--language-model-only` | 補助モデルコンポーネント(例: ビジョンエンコーダー)の読み込みをスキップ |
| `--reasoning-parser` | モデルの構造化された推論出力パーシングを有効化 |

パラメータの完全な使用方法については、[vLLMドキュメント](https://docs.vllm.ai/en/latest/configuration/engine_args/)を参照してください。

## モデルへのアクセス

vLLMはOpenAI互換のAPIを公開しているため、互換性のあるクライアントやインターフェースをクラスターに接続できます。人気のあるオプションの1つが[Open WebUI](https://github.com/open-webui/open-webui)で、ブラウザベースのチャットインターフェースを提供します。

Open WebUIをvLLMエンドポイントに接続するには:

1. **Settings** > **Admin Panel** > **Connections** を開きます
2. **Manage OpenAI API Connections** の **+** をクリックします
3. **Connection Type** を **External** に設定します
4. **URL** を `http://<MACHINE_1_IP>:7000/v1` に設定します
5. **Auth** のドロップダウンから **None** を選択します
6. **Model IDs** は空欄のままにして、エンドポイントからすべてのモデルを自動検出します

> **`<MACHINE_1_IP>` の確認方法**: マシン1で `hostname -I | awk '{print $1}'` を実行すると、そのローカルIPアドレスを確認できます。マシン1自体からOpen WebUIにアクセスする場合は、`http://localhost:7000/v1` を使用できます。

![vLLMエンドポイント用のOpen WebUI接続設定](assets/openwebui-connection.png)

接続が完了したら、Open WebUIのモデルドロップダウンからモデルを選択し、チャットを開始します。これで、モデルは2台のRyzen AI Haloノードにわたって実行されています:

![Open WebUIでQwen3.5-397Bとチャットする](assets/openwebui-chat.png)

## 次のステップ

- **他のモデルを試す**: クラスターの合計GPUメモリに収まる新しいモデルを[Hugging Face](https://huggingface.co/models?&sort=trending)で見つけましょう
- **4ノードにスケールする**: さらに2台のRyzen AI Haloシステムを追加のRayワーカーとして加え、さらに多くのGPUにモデルを分割します。これには、各ノードに1つずつ、少なくとも4ポートのイーサネットスイッチが必要です。追加する各ワーカーで[ステップ2: クラスターに参加する](#step-2-join-the-cluster-machine-2)に従い、`--tensor-parallel-size` を適宜増やしてください
- **他の並列化戦略を試す**: vLLMは、混合エキスパートモデル向けの[エキスパート並列](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)や、スループット向上のための[データ並列](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)をサポートしています。`--enable-expert-parallel` や `--data-parallel-size` を試して、ワークロードに最適な構成を見つけてください