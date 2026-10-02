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

# RCCLを使用した4台のRyzen™ AI Haloのクラスタリング

## 概要

お使いのRyzen™ AI Haloは、すでにローカルで大規模言語モデルを実行する能力を備えています。クラスタリングはこれをさらに一歩進め、ローカルネットワーク上で複数のシステムのGPUメモリを結合することで、より強力な推論、より優れたコード生成、より深い多言語理解を備えたさらに大規模なモデルへのアクセスを、すべて自分自身のハードウェア上で完結させて実現します。

このプレイブックでは、RCCL(ROCm Communication Collectives Library)とvLLMを使用して4台のRyzen AI Haloシステムをクラスタリングし、397Bパラメータのモデルであるqwen3.5-397Bを、ROCmアクセラレーションを用いて4台すべてのマシンで実行する方法を学びます。

## このプレイブックで学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmサポート付きでのvLLMの起動
- 4台のRyzen AI Haloシステム間でのマルチノードテンソル並列推論のためのRCCL設定
- 4台のネットワーク接続されたRyzen AI Haloシステムにおける397Bパラメータモデルの実行

## 前提条件

### ハードウェア

このプレイブックには、4台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットをスイッチに直接接続するスター型トポロジーで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | クラスタを構成するコンピュートノード |
| 10Gbpsイーサネットスイッチ | 1 | 複数ノードのRyzen AI Halo間通信を可能にする中央スイッチ(ポートが4つ以上必要) |
| イーサネットケーブル | 4 | 各Haloユニットをスイッチに接続(Cat 7以上を推奨) |

> **注**: 4台のRyzen AI Haloユニットを接続するには、イーサネットスイッチのポートが4つ必要です。Haloユニットのいずれかではなく、別のクライアントマシンからモデルにアクセスする場合は、5つ目のポートが必要になります。

### ソフトウェア
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: この手順は4台すべてのマシン(マシン1からマシン4)で実施してください。

Cat 7(以上)のケーブルを使用して、各Ryzen AI Haloユニットをイーサネットスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。

### 1. ネットワークインターフェースの確認

各マシンで、そのネットワークインターフェースの名前を確認し、書き留めておきます(以降の手順では`IFNAME`として参照されます)。以下を実行します:

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

> **注**: `<IFNAME>`は[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)の出力インターフェース名に置き換えてください

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは、自動ネゴシエーションを無効にし、リンク速度を手動で設定する必要があります。詳細はお使いのスイッチのドキュメントを参照してください。

## VRAM割り当ての拡張

> **注**: この手順は4台すべてのマシン(マシン1からマシン4)で実施してください。

### 大規模モデル実行のためのメモリ構成

Linuxでは、ROCmは共有システムメモリプールを利用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順でカーネルのTranslation Table Manager(TTM)ページ設定を変更することで増やすことができます。AMDは、BIOSで最小専用VRAMを設定することを推奨します(0.5 GB)。

* pipxユーティリティをインストールし、pipxでインストールされたwheelのパスをシステム検索パスに追加します。

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

* 共有メモリ設定を**120 GB**に再構成します:
  ```bash
  amd-ttm --set 120
  ```

* 変更を反映させるため、システムを再起動します。

## vLLMコンテナの初期化

> **注**: この手順は4台すべてのマシン(マシン1からマシン4)で実施してください。

お使いのRyzen AI Haloには、事前にビルドされたコンテナイメージ内にパッケージ化されたvLLMが付属しており、無料のオープンソースコンテナツールであるPodmanを使用して実行します。

### 1. モデルダウンロードディレクトリの作成

このプレイブックでQwen3.5-397Bモデルを提供する際、vLLMはモデルの重みを自動的にシステムにダウンロードします。これらの重みがコンテナ内からアクセス可能であることを確認するために、まずコンテナがマウントできるmodelsディレクトリを作成します:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLMコンテナの起動

以下のコマンドはコンテナを起動し、インタラクティブシェルに入ります。先ほど作成したmodelsディレクトリをマウントし、`IFNAME`を`NCCL_SOCKET_IFNAME`と`GLOO_SOCKET_IFNAME`に渡すことで、RCCL(vLLMがクラスタ全体でGPUを調整するために使用するライブラリ)にどのインターフェースを使用するかを伝えます。

次のコマンドでコンテナを起動します:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注**: `<IFNAME>`は[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)の出力インターフェース名に置き換えてください

## クラスタでのモデル実行

vLLMはRayを使用してクラスタをオーケストレーションし、RCCLを使用してノード間のGPU-to-GPU通信を処理します。1台のマシンがヘッドノード(マシン1)として機能し、推論を調整します。残りの3台はワーカーノード(マシン2、3、4)として参加し、それぞれのGPUメモリと計算能力を提供します。

> **注**: Rayはvllmのオプションの依存関係であり、事前設定されたPodmanコンテナ内からのみ利用可能です。

起動時に、vLLMはテンソル並列処理を使用してモデルを4台すべてのノードにシャーディングします。読み込みが完了すると、推論は単一のアクセラレータ上で実行されているかのように進行します。

#### Ray OOMエラーの防止

デフォルトでは、Rayは各ノードのホストメモリを監視し、メモリ使用率が95%を超えると最大のプロセスを強制終了します。お使いのRyzen™ AI Haloでは、GPUとホストが1つの共有メモリプールを共有しているため、モデルの読み込みが`ray.exceptions.OutOfMemoryError`を引き起こし、ワーカープロセスを強制終了させる可能性があります。

これを防ぐため、クラスタの開始および参加前に、各マシンで`RAY_memory_monitor_refresh_ms=0`をエクスポートします。
### ステップ1: Ray ヘッドノードの起動 (Machine 1)

Machine 1 で、クラスターを初期化するために Ray ヘッドノードを起動します。

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` の確認方法**: Machine 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。

### ステップ2: クラスターへの参加 (Machine 2、3、4)

Machine 2、3、4 のそれぞれで、ヘッドノードに接続してクラスターを構成します。

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **`<MACHINE_N_IP>` の確認方法**: 各ワーカーマシンで `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。

### ステップ3: モデルの提供 (Machine 1)

Machine 1 で vLLM サーバーを起動します。これにより、モデルが自動的にダウンロードされ、4つすべてのノードにまたがってモデルの提供が開始されます。

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### パラメータリファレンス

| フラグ | 用途 |
|------|---------|
| `--port` | HTTP API を提供するポート |
| `--host` | サーバーをバインドする IP アドレス (すべてのインターフェースの場合は `0.0.0.0`) |
| `--max-model-len` | 最大コンテキスト長 (トークン数) |
| `--gpu-memory-utilization` | 割り当てる GPU メモリの割合 (0.0～1.0) |
| `--dtype` | モデルの重みのデータ型 |
| `--tensor-parallel-size` | モデルを分割する GPU の数 (クラスター内の GPU の合計数に設定) |
| `--distributed-executor-backend` | マルチノード実行用のバックエンド (クラスターデプロイメントの場合は `ray`) |
| `--enforce-eager` | 互換性のために CUDA グラフのコンパイルを無効化 |
| `--language-model-only` | 補助的なモデルコンポーネント (視覚エンコーダーなど) の読み込みをスキップ |
| `--reasoning-parser` | モデルの構造化された推論出力の解析を有効化 |

パラメータの詳細な使用方法については、[vLLM ドキュメント](https://docs.vllm.ai/en/latest/configuration/engine_args/)を参照してください。

## モデルへのアクセス

vLLM は OpenAI 互換の API を公開しているため、互換性のある任意のクライアントやインターフェースをクラスターに接続できます。人気のある選択肢の1つが [Open WebUI](https://github.com/open-webui/open-webui) で、ブラウザベースのチャットインターフェースを提供します。

Open WebUI を vLLM エンドポイントに接続するには:

1. **設定** > **管理者パネル** > **接続** を開きます
2. **OpenAI API 接続の管理** の **+** をクリックします
3. **接続タイプ** を **外部** に設定します
4. **URL** を `http://<MACHINE_1_IP>:7000/v1` に設定します
5. **認証** で、ドロップダウンから **なし** を選択します
6. エンドポイントからすべてのモデルを自動検出するために、**モデル ID** は空欄のままにします

> **`<MACHINE_1_IP>` の確認方法**: Machine 1 で `hostname -I | awk '{print $1}'` を実行し、そのローカル IP アドレスを確認します。Machine 1 自体から Open WebUI にアクセスする場合は、`http://localhost:7000/v1` を使用できます。

![vLLM エンドポイント用の Open WebUI 接続設定](assets/openwebui-connection.png)

接続後、Open WebUI のモデルドロップダウンからモデルを選択し、チャットを開始します。モデルは、4つすべての Ryzen AI Halo ノードにまたがって実行されています。

![Open WebUI での Qwen3.5-397B とのチャット](assets/openwebui-chat.png)

## 次のステップ

- **他のモデルを探す**: [Hugging Face](https://huggingface.co/models?&sort=trending) で、クラスターの合計 GPU メモリに収まる新しいモデルを見つけましょう
- **4ノードを超えてスケールする**: さらに Ryzen AI Halo システムを追加の Ray ワーカーとして追加し、さらに多くの GPU にモデルを分割します。各追加ワーカーで [ステップ2: クラスターへの参加](#step-2-join-the-cluster-machines-2-3-and-4) に従い、それに応じて `--tensor-parallel-size` を増やしてください
- **他の並列化戦略を試す**: vLLM は、mixture-of-experts モデル向けの [エキスパート並列](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)や、より高いスループットのための[データ並列](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)をサポートしています。`--enable-expert-parallel` や `--data-parallel-size` を試して、ワークロードに最適な構成を見つけてください