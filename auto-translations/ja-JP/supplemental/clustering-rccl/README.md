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

# RCCLを用いた2台のRyzen™ AI Haloのクラスタリング

## 概要

Ryzen™ AI Haloは、すでにローカルで大規模言語モデルを実行できる能力を備えています。クラスタリングは、これをさらに一歩進め、複数のシステムのGPUメモリをローカルネットワーク経由で結合することで、より強力な推論能力、優れたコード生成能力、より深い多言語理解を備えた、さらに大規模なモデルへのアクセスを、完全に自分のハードウェア上で実現します。

このプレイブックでは、RCCL(ROCm Communication Collectives Library)を使用して、2台のRyzen AI Haloシステムをvllmとクラスタリングし、ROCmアクセラレーションによって両方のマシンにまたがる397Bパラメータモデル、Qwen3.5-397Bを実行する方法を説明します。

## 学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmサポート付きでのvLLMの起動
- 2台のRyzen AI Haloシステムにまたがるマルチノードテンソル並列推論のためのRCCLの構成
- 2台のネットワーク接続されたRyzen AI Haloシステムにまたがる397Bパラメータモデルの実行

## 前提条件

### ハードウェア

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、それぞれのユニットをスイッチに直接接続したスター型トポロジで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスタを構成するコンピュートノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo通信を可能にする中央スイッチ(少なくとも2ポート) |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続する(Cat 7以上を推奨) |

> **注記**: 2台のRyzen AI Haloユニットを接続するには、2つのイーサネットスイッチポートが必要です。Haloユニットのいずれかからではなく、別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注記**: この手順はマシン1とマシン2の両方で実施してください。

各Ryzen AI HaloユニットをCat 7(以上)ケーブルを使用してイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。

### 1. ネットワークインターフェースの特定

各マシンで、そのネットワークインターフェースの名前を調べてメモしておいてください(以降の手順では`IFNAME`として参照されます)。以下を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これによりインターフェース名が直接出力されます。例:

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブで最大速度で動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注記**: `<IFNAME>`は[1. ネットワークインターフェースの特定](#1-ネットワークインターフェースの特定)の出力インターフェース名に置き換えてください

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注記**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はスイッチのドキュメントを参照してください。

## VRAM割り当ての拡張

> **注記**: この手順はマシン1とマシン2の両方で実施してください。

### 大規模モデル実行のためのメモリ構成

Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

以下の手順に従ってカーネルのTranslation Table Manager(TTM)ページ設定を変更することで、この量を増やすことができます。AMDでは、BIOSで最小専用VRAMを設定する(0.5 GB)ことを推奨しています。

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

* 共有メモリ設定を**120 GB**に再構成します:
  ```bash
  amd-ttm --set 120
  ```

* 変更を反映させるためにシステムを再起動します。

## vLLMコンテナの初期化

> **注記**: この手順はマシン1とマシン2の両方で実施してください。

Ryzen AI Haloには、事前構築済みのコンテナイメージ内にパッケージ化されたvLLMが同梱されており、これは無料でオープンソースのコンテナツールであるPodmanを使用して実行します。

### 1. モデルダウンロードディレクトリの作成

このプレイブックでQwen3.5-397Bモデルを提供する際、vLLMは自動的にモデルの重みをシステムにダウンロードします。これらの重みがコンテナ内からアクセスできるようにするため、まずコンテナがマウントできるモデルディレクトリを作成します:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLMコンテナの起動

以下のコマンドはコンテナを起動し、対話型シェルに入ります。先ほど作成したモデルディレクトリをマウントし、`IFNAME`を`NCCL_SOCKET_IFNAME`と`GLOO_SOCKET_IFNAME`に渡すことで、RCCL(vLLMがクラスタ全体でGPUを調整するために使用するライブラリ)にどのインターフェースを使用するかを伝えます。

以下でコンテナを起動します:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注記**: `<IFNAME>`は[1. ネットワークインターフェースの特定](#1-ネットワークインターフェースの特定)の出力インターフェース名に置き換えてください

## クラスタ上でのモデルの実行

vLLMはRayを使用してクラスタをオーケストレーションし、RCCLを使用してノード間のGPU間通信を処理します。一方のマシンが**ヘッドノード**(マシン1)として動作し、推論を調整します。もう一方は**ワーカーノード**(マシン2)として参加し、そのGPUメモリと計算能力を提供します。

> **注記**: RayはvLLMのオプションの依存関係であり、事前構成済みのPodmanコンテナ内からのみ利用可能です。

起動時、vLLMはテンソル並列を使用してモデルを両方のノードに分割します。読み込みが完了すると、推論は単一のアクセラレータ上で実行しているかのように進行します。

#### Rayでのメモリ不足エラーの防止

デフォルトでは、Rayは各ノードのホストメモリを監視し、メモリ使用率が95%を超えると最大のプロセスを強制終了します。Ryzen™ AI Haloでは、GPUとホストが1つのメモリプールを共有しているため、モデルの読み込みが`ray.exceptions.OutOfMemoryError`を引き起こし、ワーカープロセスが強制終了される場合があります。

これを防ぐため、クラスタの起動および参加の前に、各マシンで`RAY_memory_monitor_refresh_ms=0`をエクスポートします。
### ステップ 1: Ray ヘッドノードを起動する(マシン 1)

マシン 1 で、クラスターを初期化するために Ray ヘッドノードを起動します。

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` の確認方法**: マシン 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。

### ステップ 2: クラスターに参加する(マシン 2)

マシン 2 で、ヘッドノードに接続してクラスターを構成します。

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` の確認方法**: マシン 2 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。

### ステップ 3: モデルを配信する(マシン 1)

マシン 1 で、vLLM サーバーを起動します。これによりモデルが自動的にダウンロードされ、両方のノードにまたがってモデルの配信が開始されます。

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
| `--max-model-len` | トークン単位での最大コンテキスト長 |
| `--gpu-memory-utilization` | 割り当てる GPU メモリの割合(0.0~1.0) |
| `--dtype` | モデルの重みに使用するデータ型 |
| `--tensor-parallel-size` | モデルを分割する GPU の数(クラスター内の GPU の合計数に設定します) |
| `--distributed-executor-backend` | マルチノード実行用のバックエンド(クラスターデプロイの場合は `ray`) |
| `--enforce-eager` | 互換性のため CUDA グラフのコンパイルを無効化します |
| `--language-model-only` | 補助的なモデルコンポーネント(視覚エンコーダーなど)の読み込みをスキップします |
| `--reasoning-parser` | モデルに対して構造化された推論出力の解析を有効化します |

パラメータの完全な使用方法については、[vLLM ドキュメント](https://docs.vllm.ai/en/latest/configuration/engine_args/)を参照してください。

## モデルへのアクセス

vLLM は OpenAI 互換の API を公開しているため、互換性のある任意のクライアントやインターフェースをクラスターに接続できます。人気の高い選択肢の 1 つが、ブラウザベースのチャットインターフェースを提供する[Open WebUI](https://github.com/open-webui/open-webui)です。

Open WebUI を vLLM エンドポイントに接続するには:

1. **Settings** > **Admin Panel** > **Connections** を開きます
2. **Manage OpenAI API Connections** にある **+** をクリックします
3. **Connection Type** を **External** に設定します
4. **URL** を `http://<MACHINE_1_IP>:7000/v1` に設定します
5. **Auth** で、ドロップダウンから **None** を選択します
6. エンドポイントからすべてのモデルを自動的に検出させるため、**Model IDs** は空欄のままにしておきます

> **`<MACHINE_1_IP>` の確認方法**: マシン 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。マシン 1 自体から Open WebUI にアクセスする場合は、`http://localhost:7000/v1` を使用できます。

![vLLM エンドポイント用の Open WebUI 接続設定](assets/openwebui-connection.png)

接続が完了したら、Open WebUI のモデルドロップダウンからモデルを選択し、チャットを開始します。これで、モデルは 2 台の Ryzen AI Halo ノードにまたがって実行されています。

![Open WebUI で Qwen3.5-397B とチャットする様子](assets/openwebui-chat.png)

## 次のステップ

- **他のモデルを探索する**: クラスターの合計 GPU メモリに収まる新しいモデルを [Hugging Face](https://huggingface.co/models?&sort=trending) で探してみましょう
- **4 ノードにスケールする**: さらに Ryzen AI Halo システムを 2 台追加し、追加の Ray ワーカーとして加えることで、より多くの GPU にモデルを分割できます。これには、各ノードに 1 ポートずつ、最低 4 ポートを備えたイーサネットスイッチが必要です。追加する各ワーカーで [ステップ 2: クラスターに参加する](#step-2-join-the-cluster-machine-2)の手順に従い、それに応じて `--tensor-parallel-size` を増やしてください
- **他の並列化戦略を試す**: vLLM は、mixture-of-experts モデル向けの[エキスパートパラレル](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)と、より高いスループットを実現する[データパラレル](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)をサポートしています。`--enable-expert-parallel` や `--data-parallel-size` を試して、ワークロードに最適な構成を見つけてください