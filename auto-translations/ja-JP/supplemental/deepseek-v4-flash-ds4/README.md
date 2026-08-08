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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) は、DeepSeek V4 ファミリーの効率性重視のバリアントであり、2840 億パラメータの Mixture of Experts モデルで、アクティブパラメータ数は 130 億です。[DeepSeek のテクニカルレポート](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)によると、SWE-bench Verified で 79%、LiveCodeBench で 91.6% のスコアを記録しています。

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) は、このモデルアーキテクチャ専用に構築された推論エンジンです。汎用ランタイムではなく、ds4 は DeepSeek V4 ファミリーを直接ターゲットとし、AMD ROCm™ ソフトウェア向けにアーキテクチャ固有のカーネル最適化を行っています。現在、Strix Halo 上での DeepSeek V4 Flash の実装として最も優れたパフォーマンスを発揮するものの一つです。

このチュートリアルでは、ターミナル UI である `ds4-cockpit` を使用して ds4 をセットアップし、モデルの重みをダウンロードし、AMD Ryzen™ AI Halo Developer Platform 上でローカルに DeepSeek V4 Flash の提供を開始する方法を紹介します。

## 学習内容

- `ds4-cockpit` ターミナル UI をインストールして起動する方法
- ds4 ROCm ツールボックスコンテナを作成する方法
- 単一の Halo ノード向けに推奨される量子化をダウンロードする方法
- ds4 推論サーバーを起動し、OpenAI 互換のエンドポイントを公開する方法
- Web UI またはコーディングエージェントをローカルサーバーに接続する方法

## メモリ構成の設定

<!-- @require:memory-config -->

## ソフトウェア前提条件のインストール

> **この構成(単一ノードの IQ2_XXS、コンテキスト長 126k)におけるシステム要件:**
> - **128 GB 以上の統合メモリ**を搭載した Strix Halo システム。
> - **BIOS の専用 VRAM(UMA フレームバッファ)を最小値に設定**し、共有メモリプールをできるだけ大きく確保できるようにします。
> - GPU の**共有メモリプールを最低 110 GB に設定**します。`amd-ttm --set 110` を実行し(上記のメモリ構成の手順を参照)、再起動してください。この値が低いと、モデルを 126k コンテキストで読み込む際にメモリ不足エラーが発生する可能性があります。システムのメモリがそれより少ない場合は、代わりに Server Mode の **Context** 値を下げてください。
>
> **注:** まずは **GPU 共有メモリプール**を **110 GB** に設定してみてください。メモリ不足エラーが発生する場合は、共有メモリプールを増やすか、コンテキストサイズを下げてください。

ds4-cockpit は、ds4 エンジンを実行するためにコンテナツールボックスを使用します。`podman`、`distrobox`、`pipx` をインストールしてください:

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

ds4 の作者は、GGUF 形式で DeepSeek V4 Flash のいくつかの量子化バージョンを提供しています。以下のモデルはすべて重要度行列(imatrix)キャリブレーションを使用しており、コーディングや推論タスクにとって重要な部分についてより高い精度を維持します。

| 量子化 | サイズ | 説明 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 80.8 GB | 単一の 128 GB ノードに推奨 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 97 GB | レイヤー 37〜42 を Q4 精度に保ち、精度を向上。128 GB に収まるが、コンテキストの余地は少なくなる |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 153 GB | より高品質。マルチノードクラスタリングによる 2 台の Halo ノードが必要 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 3.6 GB | 生成速度を向上させる投機的デコーディング用のオプションアドオン |

**IQ2_XXS imatrix** モデルは良い出発点です。単一ノードに無理なく収まり、適度なコンテキストウィンドウのための十分なメモリを残します。

## ds4-cockpit のインストール

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) は、Strix Halo 上で ds4 を簡単に使い始められるようにする軽量なターミナル UI です。ツールボックスコンテナの作成、モデルの重みのダウンロード、サーバーの起動を処理します。`pipx` でインストールします:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

コックピットを起動します:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## ツールボックスの作成

**Interactive Toolboxes** タブで、最新の利用可能/安定版のツールボックス(例: `ds4-rocm-7.2.4`)を選択し、**Create/Update** をクリックします。これにより、コンテナイメージがプルされ、ツールボックス環境が作成されます。


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## モデルのダウンロード

**Model Manager** タブに移動します。ドロップダウンから **IQ2_XXS imatrix (~80.8 GB)** を選択し、**Download** をクリックします。モデルファイルはデフォルトで `~/ds4` に保存されます(保存パスは変更可能です)。

> **注:** IQ2_XXS モデルはおよそ 80 GB あるため、接続状況によってはダウンロードに時間がかかる場合があります。完了したら次に進んでください。

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
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

## サーバーの起動

**Server Mode** タブに移動します。ダウンロードしたモデルとツールボックスを選択し、コンテキストサイズ、ホスト、ポートを設定します。準備ができたら、**Start ds4-server** をクリックします。

> **ヒント** コンテキストサイズ `126000` は、単一ノードに収まる妥当な初期値です。メモリに余裕がある場合はさらに大きく設定でき、メモリ不足エラーが発生する場合は下げることができます。ポート(このガイドでは `8000`)は任意です。空いている任意のポートを選択してください。

> **KV ディスクキャッシュ(オプション)。** **KV Disk Cache** を有効にすると、KV キャッシュがディスク(**Host Cache Dir**、デフォルトは `~/.cache/ds4-kv`)にオフロードされ、繰り返されるシステムプロンプトが再計算されるのではなく SSD から復元されるようになります。これは、長く繰り返されるプロンプトを伴うコーディングエージェントのワークフロー向けのパフォーマンス最適化であり、サーバーを実行するために**必須ではありません**。

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

サーバーが起動し、ポート 8000 でリッスンを開始します。これにより、`http://localhost:8000/v1` で OpenAI 互換の API エンドポイントが公開されます。

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
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
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

## Web UI の接続

OpenAI API 形式をサポートする任意のチャットインターフェースを接続できます。例えば、HuggingFace ChatUI を使用する場合:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

ブラウザで `http://localhost:3000` を開くと、チャットを開始できます。
## コーディングエージェントの接続

ds4サーバーはOpenAIとAnthropic互換の両方のエンドポイントを公開しているため、ほとんどのコーディングエージェントは直接接続できます。例えば、`pi`コーディングエージェントに追加するには、`~/.pi/agent/models.json`に次のブロックを追加します。

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

> **ヒント**: コーディングエージェントやWeb UIがHaloプラットフォームとは別のマシンで動作している場合は、SSH経由でポート8000を転送する必要があります。
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## 次のステップ

- **マルチノードクラスタリング**: Haloデバイスを2台お持ちの場合、ds4はパイプライン並列処理を通じてQ4モデル(約153GB)を両方のマシンに分散させることができます。セットアップ手順については、[ds4-toolboxのドキュメント](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)を参照してください。
- **推測的デコード(MTP)**: MTPの重み(約3.6GB)をダウンロードし、サーバーに`--mtp`を渡すことで、生成速度を高速化できます。
- **KVキャッシュのディスクオフロード**: コーディングエージェントのワークフローでは、`--kv-disk-dir`を有効にすることで、繰り返し使用されるシステムプロンプトを毎回再計算するのではなく、SSDから復元できるようにします。

詳細については、[ds4リポジトリ](https://github.com/antirez/ds4)と[ds4-cockpitツールボックス](https://github.com/kyuz0/strix-halo-ds4-toolbox)を参照してください。