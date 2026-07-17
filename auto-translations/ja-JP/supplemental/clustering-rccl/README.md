<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# RCCLを使用した2台のRyzen™ AI Haloのクラスタリング

## 概要

Ryzen™ AI Haloは、すでにローカルで大規模言語モデルを実行する能力を備えています。クラスタリングはこれをさらに発展させ、ローカルネットワーク上で複数のシステムのGPUメモリを組み合わせることで、より強力な推論、優れたコード生成、深い多言語理解を持つさらに大きなモデルへのアクセスを可能にします。これらはすべて、完全にご自身のハードウェア上で実現できます。

このPlaybookでは、RCCL（ROCm Communication Collectives Library）を使用して2台のRyzen AI Haloシステムをクラスタリングし、vLLMとROCmアクセラレーションを活用して、3970億パラメータのモデルであるQwen3.5-397Bを両マシンにまたがって実行する方法を説明します。

## 学習内容

- Ryzen AI HaloシステムでのVRAM割り当ての拡張方法
- ROCmサポートを有効にしたvLLMの起動
- 2台のRyzen AI Haloシステムにまたがるマルチノードテンソル並列推論のためのRCCL設定
- ネットワーク接続された2台のRyzen AI Haloシステムにまたがる3970億パラメータモデルの実行

## 前提条件

### ハードウェア

このPlaybookには、2台のRyzen AI Haloユニットと1台のEthernetスイッチが必要です。各ユニットをスイッチに直接接続するスタートポロジーで構成します。

| コンポーネント | 数量 | 説明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | クラスターを構成するコンピュートノード |
| 10Gbps Ethernetスイッチ | 1 | マルチノードRyzen AI Halo通信を可能にする中央スイッチ（最低2ポート） |
| Ethernetケーブル | 2 | 各Haloユニットをスイッチへ接続（Cat 7以上推奨） |

> **注意**: 2台のRyzen AI HaloユニットをEthernetスイッチに接続するには、2つのスイッチポートが必要です。Haloユニットの1台ではなく別のクライアントマシンからモデルにアクセスする場合は、3つ目のポートが必要です。

### ソフトウェア
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理ハードウェアのセットアップ

> **注意**: このステップはマシン1とマシン2の両方で実施してください。

Cat 7（以上）のケーブルを使用して、各Ryzen AI HaloユニットをEthernetスイッチに接続します。これにより、ノード間の高速通信に使用される10Gbpsリンクが確立されます。

### 1. ネットワークインターフェースの確認

各マシンで、ネットワークインターフェース名を確認してメモしておきます（以降の手順では`IFNAME`として参照します）。次のコマンドを実行します：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

これにより、インターフェース名が直接出力されます。例：

```bash
enp191s0
```

### 2. ネットワークリンク速度の確認

インターフェースの速度を確認して、リンクがアクティブで全速度で動作していることを確認します：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**: `<IFNAME>`は[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)で取得したインターフェース名に置き換えてください。

速度が`10000Mb/s`と表示されるはずです：

```bash
	Speed: 10000Mb/s
```

> **注意**: 速度が`10000Mb/s`より低い場合、またはリンクが確立されない場合は、ケーブル接続を確認し、スイッチポートが10Gbpsに設定されていることを確認してください。スイッチによっては、オートネゴシエーションを無効にしてリンク速度を手動で設定する必要がある場合があります。スイッチのドキュメントを参照してください。

## VRAM割り当ての拡張

> **注意**: このステップはマシン1とマシン2の両方で実施してください。

### 大規模モデル実行のためのメモリ設定

LinuxでROCmは共有システムメモリプールを使用しており、このプールはデフォルトでシステムメモリの半分に設定されています。

この量は、以下の手順でカーネルのTranslation Table Manager（TTM）ページ設定を変更することで増やすことができます。AMDはBIOSで最小専用VRAMを0.5 GBに設定することを推奨しています。

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

## vLLMコンテナの初期化

> **注意**: このステップはマシン1とマシン2の両方で実施してください。

Ryzen AI Haloには、事前にビルドされたコンテナイメージ内にvLLMがパッケージされており、無料のオープンソースコンテナツールであるPodmanを使用して実行します。

### 1. モデルダウンロードディレクトリの作成

このPlaybookでQwen3.5-397Bモデルを提供する際、vLLMは自動的にモデルの重みをシステムにダウンロードします。それらの重みがコンテナ内からアクセスできるようにするため、コンテナがマウントできるmodelsディレクトリを事前に作成します：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLMコンテナの起動

以下のコマンドはコンテナを起動し、インタラクティブシェルに入ります。作成したmodelsディレクトリをマウントし、`IFNAME`を`NCCL_SOCKET_IFNAME`と`GLOO_SOCKET_IFNAME`に渡すことで、クラスター全体でGPUを調整するためにvLLMが使用するライブラリであるRCCLに使用するインターフェースを指示します。

次のコマンドでコンテナを起動します：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**: `<IFNAME>`は[1. ネットワークインターフェースの確認](#1-determine-network-interfaces)で取得したインターフェース名に置き換えてください。

## クラスター上でのモデルの実行

vLLMはクラスターのオーケストレーションにRayを使用し、ノード間のGPU間通信にRCCLを使用します。一方のマシンが**ヘッドノード**（マシン1）として推論を調整し、もう一方が**ワーカーノード**（マシン2）として参加し、GPUメモリとコンピュートを提供します。

> **注意**: RayはvLLMのオプション依存関係であり、事前設定済みのPodmanコンテナ内からのみ利用可能です。

起動時に、vLLMはテンソル並列処理を使用してモデルを両ノードに分散します。ロード後は、単一のアクセラレーター上で実行しているかのように推論が進行します。

### ステップ1: Rayヘッドノードの起動（マシン1）

マシン1で、Rayヘッドノードを起動してクラスターを初期化します：

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>`の確認方法**: マシン1で`hostname -I | awk '{print $1}'`を実行してローカルIPアドレスを確認します。

### ステップ2: クラスターへの参加（マシン2）

マシン2で、ヘッドノードに接続してクラスターを形成します：

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>`の確認方法**: マシン2で`hostname -I | awk '{print $1}'`を実行してローカルIPアドレスを確認します。

### ステップ3: モデルの提供（マシン1）

マシン1でvLLMサーバーを起動します。これにより、モデルが自動的にダウンロードされ、両ノードにまたがって提供が開始されます：

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

#### パラメーターリファレンス

| フラグ | 目的 |
|------|---------|
| `--port` | HTTP APIを提供するポート |
| `--host` | サーバーをバインドするIPアドレス（すべてのインターフェースには`0.0.0.0`） |
| `--max-model-len` | トークン単位の最大コンテキスト長 |
| `--gpu-memory-utilization` | 割り当てるGPUメモリの割合（0.0〜1.0） |
| `--dtype` | モデルの重みのデータ型 |
| `--tensor-parallel-size` | モデルを分散するGPUの数（クラスター内の合計GPU数に設定） |
| `--distributed-executor-backend` | マルチノード実行のバックエンド（クラスターデプロイメントには`ray`） |
| `--enforce-eager` | 互換性のためにCUDAグラフのコンパイルを無効化 |
| `--language-model-only` | 補助モデルコンポーネント（例：ビジョンエンコーダー）のロードをスキップ |
| `--reasoning-parser` | モデルの構造化推論出力解析を有効化 |

完全なパラメーターの使用方法については、[vLLMドキュメント](https://docs.vllm.ai/en/latest/configuration/engine_args/)を参照してください。

## モデルへのアクセス

vLLMはOpenAI互換のAPIを公開しているため、互換性のあるクライアントやインターフェースをクラスターに接続できます。人気のある選択肢の一つが[Open WebUI](https://github.com/open-webui/open-webui)で、ブラウザベースのチャットインターフェースを提供します。

Open WebUIをvLLMエンドポイントに接続するには：

1. **設定** > **管理パネル** > **接続**を開きます
2. **OpenAI API接続の管理**の**+**をクリックします
3. **接続タイプ**を**外部**に設定します
4. **URL**を`http://<MACHINE_1_IP>:7000/v1`に設定します
5. **認証**で、ドロップダウンから**なし**を選択します
6. **モデルID**は空のままにして、エンドポイントからすべてのモデルを自動検出します

> **`<MACHINE_1_IP>`の確認方法**: マシン1で`hostname -I | awk '{print $1}'`を実行してローカルIPアドレスを確認します。マシン1自体からOpen WebUIにアクセスする場合は、`http://localhost:7000/v1`を使用できます。

![vLLMエンドポイントのOpen WebUI接続設定](assets/openwebui-connection.png)

接続後、Open WebUIのモデルドロップダウンからモデルを選択してチャットを開始します。モデルは現在、2台のRyzen AI Haloノードにまたがって実行されています：

![Open WebUIでQwen3.5-397Bとチャット](assets/openwebui-chat.png)

## 次のステップ

- **他のモデルを探索する**: [Hugging Face](https://huggingface.co/models?&sort=trending)でクラスターの合計GPUメモリに収まる新しいモデルを探す
- **4ノードへのスケールアップ**: さらに2台のRyzen AI Haloシステムを追加のRayワーカーとして追加し、さらに多くのGPUにまたがってモデルを分散させる。これには少なくとも4つのポートを持つEthernetスイッチが必要です（各ノードに1つ）。追加の各ワーカーで[ステップ2: クラスターへの参加](#step-2-join-the-cluster-machine-2)を実行し、`--tensor-parallel-size`を適宜増やしてください
- **他の並列処理戦略を試す**: vLLMはMixture-of-Expertsモデル向けの[エキスパート並列](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)と、より高いスループット向けの[データ並列](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)をサポートしています。`--enable-expert-parallel`と`--data-parallel-size`を試して、ワークロードに最適な設定を見つけてください