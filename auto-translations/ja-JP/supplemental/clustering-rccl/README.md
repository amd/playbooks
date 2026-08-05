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

# RCCLで2台のRyzen™ AI Haloをクラスタ化する

## 概要

お使いのRyzen™ AI Haloは、すでにローカルで大規模言語モデルを実行できます。クラスタ化は、これをさらに一歩進め、ローカルネットワーク上で複数のシステムのGPUメモリを組み合わせることで、より強力な推論力、優れたコード生成、より深い多言語理解を備えた、さらに大規模なモデルへのアクセスを、完全にご自身のハードウェア上で実現します。

このプレイブックでは、RCCL(ROCm Communication Collectives Library)を使用して2台のRyzen AI Haloシステムをクラスタ化し、vLLMと共に397Bパラメータのモデルであるqwen3.5-397Bを両方のマシンにまたがってROCmアクセラレーションで実行する方法を説明します。

## 学べること

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmサポート付きでのvLLMの起動
- 2台のRyzen AI Haloシステムにまたがるマルチノードテンソル並列推論のためのRCCL設定
- ネットワーク接続された2台のRyzen AI Haloシステムにまたがる397Bパラメータモデルの実行

## 前提条件

### ハードウェア

このプレイブックには、2台のRyzen AI Haloユニットと1台のイーサネットスイッチが必要で、各ユニットがスイッチに直接接続されるスター型トポロジーで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスタを構成するコンピュートノード |
| 10Gbpsイーサネットスイッチ | 1 | マルチノードのRyzen AI Halo通信を可能にする中央スイッチ(少なくとも2ポート) |
| イーサネットケーブル | 2 | 各Haloユニットをスイッチに接続する(Cat 7以上を推奨) |

> **注**: 2台のRyzen AI Haloユニットを接続するには、イーサネットスイッチの2つのポートが必要です。Haloユニットの一方ではなく別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要になります。

### ソフトウェア
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注**: このステップはマシン1とマシン2の両方で完了してください。

Cat 7(以上)のケーブルを使用して、各Ryzen AI HaloユニットをイーサネットスイッチにObject接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。

### 1. ネットワークインターフェースを確認する

各マシンで、そのネットワークインターフェースの名前を見つけてメモしておいてください(以降の手順では`IFNAME`として参照されます)。次を実行します:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これによりインターフェース名が直接表示されます。例:

```bash
enp191s0
```

### 2. ネットワークリンクの速度を確認する

インターフェースの速度を確認して、リンクがアクティブでありフル速度で動作していることを確認します:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注**: [1. ネットワークインターフェースを確認する](#1-ネットワークインターフェースを確認する)の出力インターフェース名で`<IFNAME>`を置き換えてください

`10000Mb/s`の速度が表示されるはずです:

```bash
	Speed: 10000Mb/s
```

> **注**: 速度が`10000Mb/s`より低い場合、またはリンクが確立しない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。一部のスイッチでは自動ネゴシエーションを無効にしてリンク速度を手動で設定する必要があります。お使いのスイッチのドキュメントを参照してください。

## VRAM割り当ての拡張

> **注**: このステップはマシン1とマシン2の両方で完了してください。

### 大規模モデル実行のためのメモリ設定

Linuxでは、ROCmは共有システムメモリプールを利用し、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順に従ってカーネルのTranslation Table Manager(TTM)ページ設定を変更することで増やすことができます。AMDでは、BIOSで専用VRAMの最小値を設定することを推奨します(0.5 GB)。

* pipxユーティリティをインストールし、pipxでインストールされたホイールへのパスをシステム検索パスに追加します。

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

* 変更を有効にするためにシステムを再起動します。

## vLLMコンテナの初期化

> **注**: このステップはマシン1とマシン2の両方で完了してください。

お使いのRyzen AI Haloには、事前構築済みのコンテナイメージ内にvLLMがパッケージ化されています。これは、無料のオープンソースコンテナツールであるPodmanを使用して実行します。

### 1. モデルダウンロードディレクトリの作成

このプレイブックでQwen3.5-397Bモデルを提供する際、vLLMは自動的にモデルの重みをシステムにダウンロードします。これらの重みがコンテナ内からアクセス可能であることを確実にするため、まずコンテナがマウントできるモデルディレクトリを作成します:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLMコンテナの起動

以下のコマンドはコンテナを起動し、対話型シェルに移行します。先ほど作成したモデルディレクトリをマウントし、`IFNAME`を`NCCL_SOCKET_IFNAME`と`GLOO_SOCKET_IFNAME`に渡すことで、vLLMがクラスタ全体のGPUを調整するために使用するライブラリであるRCCLに、どのインターフェースを使用するかを伝えます。

次のコマンドでコンテナを起動します:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注**: [1. ネットワークインターフェースを確認する](#1-ネットワークインターフェースを確認する)の出力インターフェース名で`<IFNAME>`を置き換えてください

## クラスタでのモデルの実行

vLLMはRayを使用してクラスタをオーケストレーションし、RCCLを使用してノード間のGPU間通信を処理します。1台のマシンが**ヘッドノード**(マシン1)として機能し、推論を調整します。もう1台は**ワーカーノード**(マシン2)として参加し、そのGPUメモリと計算能力を提供します。

> **注**: Rayはオプションのvllm依存関係であり、事前構成済みのPodmanコンテナ内からのみ利用可能です。

起動時、vLLMはテンソル並列処理を使用して両方のノードにモデルを分散します。読み込みが完了すると、推論は単一のアクセラレータ上で実行されているかのように進行します。

### ステップ1: Rayヘッドノードの起動(マシン1)

マシン1で、Rayヘッドノードを起動してクラスタを初期化します:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`の確認方法**: マシン1で`hostname -I | awk '{print $1}'`を実行して、そのローカルIPアドレスを確認してください。
### ステップ2: クラスターに参加する(マシン2)

マシン2で、ヘッドノードに接続してクラスターを構成します:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` の確認方法**: マシン2で `hostname -I | awk '{print $1}'` を実行し、そのローカルIPアドレスを確認します。

### ステップ3: モデルを提供する(マシン1)

マシン1で、vLLMサーバーを起動します。これによりモデルが自動的にダウンロードされ、両方のノードにまたがって提供が開始されます:

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
| `--max-model-len` | 最大コンテキスト長(トークン数) |
| `--gpu-memory-utilization` | 割り当てるGPUメモリの割合(0.0〜1.0) |
| `--dtype` | モデルの重みのデータ型 |
| `--tensor-parallel-size` | モデルをシャーディングするGPUの数(クラスター内のGPUの合計数に設定) |
| `--distributed-executor-backend` | マルチノード実行用のバックエンド(クラスターデプロイメントの場合は `ray`) |
| `--enforce-eager` | 互換性のためCUDAグラフのコンパイルを無効化 |
| `--language-model-only` | 補助的なモデルコンポーネント(視覚エンコーダーなど)の読み込みをスキップ |
| `--reasoning-parser` | モデルの構造化された推論出力の解析を有効化 |

パラメータの完全な使用方法については、[vLLM documentation](https://docs.vllm.ai/en/latest/configuration/engine_args/)を参照してください。

## モデルへのアクセス

vLLMはOpenAI互換のAPIを公開しているため、互換性のある任意のクライアントやインターフェースをクラスターに接続できます。人気のあるオプションの一つが[Open WebUI](https://github.com/open-webui/open-webui)で、ブラウザベースのチャットインターフェースを提供します。

Open WebUIをvLLMエンドポイントに接続するには:

1. **Settings** > **Admin Panel** > **Connections** を開きます
2. **Manage OpenAI API Connections** の **+** をクリックします
3. **Connection Type** を **External** に設定します
4. **URL** を `http://<MACHINE_1_IP>:7000/v1` に設定します
5. **Auth** の下で、ドロップダウンから **None** を選択します
6. **Model IDs** は空のままにして、エンドポイントからすべてのモデルを自動的に検出させます

> **`<MACHINE_1_IP>` の確認方法**: マシン1で `hostname -I | awk '{print $1}'` を実行し、そのローカルIPアドレスを確認します。マシン1自体からOpen WebUIにアクセスする場合は、`http://localhost:7000/v1` を使用できます。

![vLLMエンドポイント用のOpen WebUI接続設定](assets/openwebui-connection.png)

接続が完了したら、Open WebUIのモデルドロップダウンからモデルを選択し、チャットを開始します。これで、モデルは2台のRyzen AI Haloノードにまたがって実行されています:

![Open WebUIでQwen3.5-397Bとチャットする](assets/openwebui-chat.png)

## 次のステップ

- **他のモデルを探す**: クラスターの合計GPUメモリに収まるモデルを[Hugging Face](https://huggingface.co/models?&sort=trending)で新たに探してみましょう
- **4ノードへのスケール**: さらに2台のRyzen AI Haloシステムを追加のRayワーカーとして加え、より多くのGPUにわたってモデルをシャーディングします。これには、各ノードごとに1ポート、合計4ポート以上のイーサネットスイッチが必要です。各追加ワーカーで[ステップ2: クラスターに参加する](#step-2-join-the-cluster-machine-2)に従い、`--tensor-parallel-size` を適宜増やしてください
- **他の並列化戦略を試す**: vLLMは、Mixture-of-Expertsモデル向けの[expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)や、より高いスループットのための[data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)をサポートしています。`--enable-expert-parallel` や `--data-parallel-size` を試して、ワークロードに最適な構成を見つけてください