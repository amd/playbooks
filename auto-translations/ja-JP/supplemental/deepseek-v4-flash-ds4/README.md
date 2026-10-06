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

## 概要

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) は、DeepSeek V4 ファミリーの効率重視のバリアントであり、2840億パラメータの Mixture of Experts モデルで、アクティブパラメータは130億です。[DeepSeek の技術レポート](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)によると、SWE-bench Verified で79%、LiveCodeBench で91.6%のスコアを記録しています。

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) は、このモデルアーキテクチャ専用に構築された推論エンジンです。汎用ランタイムではなく、ds4 は AMD ROCm™ ソフトウェア向けのアーキテクチャ固有のカーネル最適化を施し、DeepSeek V4 ファミリーを直接ターゲットとしています。現在、Strix Halo 上で DeepSeek V4 Flash を実行する実装の中で、最も性能が高いものの一つです。

このチュートリアルでは、ターミナル UI である `ai-toolbox-cockpit` を使用して ds4 をセットアップし、モデルの重みをダウンロードして、AMD Ryzen™ AI Halo Developer Platform 上でローカルに DeepSeek V4 Flash の提供を開始する方法を紹介します。

## このチュートリアルで学べること

- `ai-toolbox-cockpit` ターミナル UI のインストールと起動方法
- ds4 ROCm ツールボックスコンテナの作成方法
- 単一の Halo ノード向けに推奨される量子化のダウンロード
- ds4 推論サーバーの起動と OpenAI 互換エンドポイントの公開
- Web UI またはコーディングエージェントをローカルサーバーに接続する方法

## メモリ構成の設定

<!-- @require:memory-config -->

## ソフトウェア前提条件のインストール

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **この構成（単一ノードの IQ2_XXS、126kコンテキスト）のシステム要件:**
> - **少なくとも128GBの統合メモリ**を搭載した Strix Halo システム。
> - **BIOS 専用 VRAM（UMA フレームバッファ）を最小値に設定**し、共有メモリプールをできるだけ大きくすること。
> - GPU の**共有メモリプールを少なくとも110GBに設定**すること: `amd-ttm --set 110` を実行し（上記のメモリ構成手順を参照）、再起動します。値が低すぎると、126kコンテキストでモデルをロードする際にメモリ不足で失敗する可能性があります。システムのメモリに余裕がない場合は、代わりにサーバーモードで**コンテキスト**の値を下げてください。
>
> **注:** まずは**GPU 共有メモリプール**を**110GB**に設定してみてください。メモリ不足エラーが発生した場合は、共有メモリプールを増やすか、コンテキストサイズを下げてください。

ai-toolbox-cockpit はコンテナツールボックスを使用して ds4 エンジンを実行します。`podman`、`distrobox`、`pipx` をインストールしてください:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## 利用可能な量子化

ds4 の作者は、GGUF 形式で DeepSeek V4 Flash のいくつかの量子化バージョンを提供しています。以下のすべてのモデルは重要度マトリックス（imatrix）キャリブレーションを使用しており、コーディングや推論タスクにとって最も重要な部分の精度をより高く維持しています。

| 量子化 | サイズ | 説明 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約80.8GB | 単一の128GBノードに推奨 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約97GB | レイヤー37〜42をQ4精度に保ち、より高い精度を実現。128GBに収まるが、コンテキスト用の余裕は少なくなる |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約153GB | より高品質。マルチノードクラスタリングによる2台のHaloノードが必要 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | 約3.6GB | 生成速度を向上させる投機的デコーディング用のオプションアドオン |

**IQ2_XXS imatrix** モデルは良い出発点です。単一ノードに無理なく収まり、妥当なコンテキストウィンドウに十分なメモリの余裕を残します。

## ai-toolbox-cockpit のインストール

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) は、さまざまな AI バックエンドのインストールを容易にする軽量なターミナル UI です。これを使って ds4 コンテナの作成、モデルの重みのダウンロード、サーバーの起動を処理します。`pipx` でインストールしてください:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

コックピットを起動します:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## ステップ1: ツールボックスの作成

**Interactive Toolboxes** タブで、ds4 向けの最新の利用可能/安定版ツールボックス（例: `ds4-rocm-10.0`）を選択し、**Create/Update** をクリックします。これによりコンテナイメージがプルされ、ツールボックス環境が作成されます。


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## ステップ2: モデルのダウンロード

**Models** タブに移動します。まずバックエンド（ds4）を選択します。次に、ドロップダウンから **IQ2_XXS imatrix (~80.8 GB)** を選択し、**Download** をクリックします。モデルファイルはデフォルトで `~/ds4` に保存されます（保存パスは変更可能です）。

> **注:** IQ2_XXS モデルは約80GBあるため、接続速度によってはダウンロードに時間がかかる場合があります。完了したら次に進むことができます。

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## ステップ3: サーバーの起動

**Server Mode** タブに移動します。ダウンロードしたモデルとツールボックスを選択し、コンテキストサイズ、ホスト、ポートを設定します。準備ができたら **Start ds4-server** をクリックします。

> **ヒント** コンテキストサイズ `126000` は、単一ノードに収まる妥当な初期値です。メモリに余裕があればもっと高く設定でき、メモリ不足エラーが発生する場合は下げることができます。ポート（このガイドでは `8000`）は任意です。空いているポートを選んでください。

> **KVディスクキャッシュ（任意）。** **KV Disk Cache** を有効にすると、KVキャッシュがディスク（**Host Cache Dir**、デフォルトは `~/.cache/ds4-kv`）にオフロードされ、繰り返されるシステムプロンプトが再計算されるのではなくSSDから復元されるようになります。これは、長く繰り返されるプロンプトを使うコーディングエージェントのワークフロー向けのパフォーマンス最適化であり、サーバーを実行するために**必須ではありません**。

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

サーバーが起動し、ポート8000で待ち受け、`http://localhost:8000/v1` に OpenAI 互換の API エンドポイントを公開します。

**簡単なテスト:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->
## Web UIの接続

OpenAI API形式をサポートするチャットインターフェースであれば、どれでも接続できます。例えば、HuggingFace ChatUIを使用する場合は次のようにします。

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

ブラウザで`http://localhost:3000`を開くとチャットを開始できます。

> **注:** `--network=host`はWeb UIをホストのネットワークに配置し、`localhost`上のds4サーバーに直接アクセスできるようにします。これにより、ds4サーバーはループバックにバインドされたままとなり(他のインターフェースに公開する必要がありません)。

> **ヒント:** Web UIのポート(ここでは`3000`、`PORT`で設定)は任意です。`3000`が既に使用されている場合は空いているポートを選択し、ブラウザではそのポートを開いてください。`OPENAI_BASE_URL`内のポートが、ds4サーバーが実行されているポートと一致していることを確認してください。

## コーディングエージェントの接続

ds4サーバーはOpenAIおよびAnthropic互換の両方のエンドポイントを公開しているため、ほとんどのコーディングエージェントは直接接続できます。例えば、`pi`コーディングエージェントに追加する場合は、`~/.pi/agent/models.json`に以下のブロックを追加します。

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **ヒント**: コーディングエージェントやWeb UIがHaloプラットフォームとは別のマシンで実行されている場合は、SSH経由でサーバーのポート(ここでは`8000`)を転送する必要があります。
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## 次のステップ

- **マルチノードクラスタリング**: Haloデバイスを2台お持ちの場合、ds4はパイプライン並列処理により、Q4モデル(約153GB)を両方のマシンに分散できます。セットアップ手順については[ds4-toolboxのドキュメント](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)を参照してください。
- **投機的デコーディング(MTP)**: MTPウェイト(約3.6GB)をダウンロードし、サーバーに`--mtp`を渡すことで、生成速度を向上できます。
- **KVキャッシュのディスクオフロード**: コーディングエージェントのワークフローでは、`--kv-disk-dir`を有効にすることで、繰り返されるシステムプロンプトが毎回再計算される代わりにSSDから復元されるようになります。

詳細については、[ds4リポジトリ](https://github.com/antirez/ds4)および[ds4-cockpitツールボックス](https://github.com/kyuz0/strix-halo-ds4-toolbox)を参照してください。