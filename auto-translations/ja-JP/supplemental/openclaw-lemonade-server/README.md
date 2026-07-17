<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Lemonade Server をバックエンドとして OpenClaw を実行する

## 概要

[**OpenClaw**](https://openclaw.ai/) は、コードの記述と実行、ファイルの管理、複雑なマルチステップタスクの処理をあなたに代わって行う自律型 AI エージェントです。質問に答えるだけのチャットアシスタントとは異なり、OpenClaw はシステム上で実際のアクションを実行します。そのため、要求の厳しいエージェントループに対応できる、高速で高性能な AI バックエンドが必要です。

[**Lemonade Server**](https://lemonade-server.ai/) はそのバックエンドです。オープンソースのローカル推論サーバーであり、GenAI モデルをお使いのハードウェア上で直接実行し、業界標準の OpenAI API を通じて公開します。

これらを組み合わせることで、完全にローカルな AI エージェントスタックが構成されます。Lemonade がモデル推論を担当し、OpenClaw がモデルの出力を実際のアクションに変換するエージェントループを提供します。

> **続行する前に:** OpenClaw は高度に自律的な AI エージェントです。AI エージェントにシステムへのアクセスを許可すると、予測不能または意図しない結果が生じる可能性があります。リスクを理解し、自律的なソフトウェアがあなたの代わりに行動することに問題がない場合にのみ続行してください。

---

## 学習内容

このプレイブックを完了すると、以下のことができるようになります。

- **Lemonade Server** について学ぶ
- **OpenClaw をインストール**し、AI バックエンドとして **Lemonade Server を指定**する。
- **OpenClaw ゲートウェイを起動**し、エージェントが動作可能な状態であることを確認する。
- **通信チャンネル**（Discord または Telegram）を接続し、任意のデバイスからエージェントとチャットできるようにする。

---

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @os:linux -->
- `apt-get` を備えた **Ubuntu 24.04+** または互換性のある Debian ベースの Linux ディストリビューションを実行している PC
- 少なくとも **12 GB の RAM**（大規模モデルには 64 GB 以上を推奨）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（オプション、OpenClaw のサンドボックス化用）

- モデルウェイト用に **約 10〜30 GB の空きディスク容量**
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11** を実行している PC
- 少なくとも **12 GB の RAM**（大規模モデルには 64 GB 以上を推奨）
- モデルウェイト用に **約 10〜30 GB の空きディスク容量**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（オプション、OpenClaw のサンドボックス化用）
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 推奨モデルのプルとロード

このプレイブックで推奨するモデルは、Unsloth の **Qwen3.6-35B-A3B-GGUF** です。263k トークンのコンテキストウィンドウを持つ強力な MoE モデルで、エージェントワークロードに適しています。このモデルは UD-Q4_K_XL 量子化を使用しています。今すぐプルしてください。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

次に、大きなコンテキストウィンドウでロードし、その設定を将来の実行のために保存します。

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

モデルのデフォルトコンテキスト長は 262,144 トークンです。メモリ不足（OOM）エラーが発生した場合は、コンテキストウィンドウを縮小することを検討してください。ただし、Qwen3.6 は複雑なタスクに拡張コンテキストを活用するため、思考能力を維持するためにコンテキスト長を少なくとも 128K トークンに保つことをお勧めします。

> **ヒント: 思考を無効にしてエージェントの応答を高速化する:** Qwen3.6-35B-A3B はデフォルトで思考モードで動作するため、各応答の前にレイテンシが発生します。エージェントループではこのオーバーヘッドが蓄積されます。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリには、思考を無効にする既製の設定が用意されています。使用するには、ファイルをダウンロードしてインポートしてください。
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## WSL のセットアップ

OpenClaw を WSL 内で実行し（推奨）、Windows 上でネイティブに動作する Lemonade に接続します。これにより、OpenClaw 用の Linux シェル環境を確保しながら、Windows 側で Lemonade の GPU アクセラレーションを維持できます。

### WSL と Ubuntu のインストール

管理者として PowerShell を開き、WSL カーネルをインストールします。

```powershell
wsl --install --no-distribution
```

次に Ubuntu をインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL で systemd を有効にする

Ubuntu ターミナル内でこれを実行します。

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

WSL を再起動します。

```powershell
wsl --shutdown
wsl
```

### Windows から WSL へ Lemonade をブリッジする

WSL2 は仮想ネットワーク内で動作します。Windows 上の Lemonade は `127.0.0.1` にバインドされており、WSL から直接アクセスすることはできません。Windows のポートプロキシが WSL ゲートウェイ IP から Windows のローカルホストへトラフィックを転送します。

**WSL ゲートウェイ IP を確認する**（WSL 内で実行）:

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加する**（管理者として PowerShell で実行し、`<WSL-Gateway-IP>` を WSL ゲートウェイ IP に置き換えてください）:

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**ファイアウォールルールを追加する**（同じ昇格された PowerShell で）:

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL から確認する**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前のステップで Qwen3.6-35B-A3B-GGUF モデルをすでにロードしている場合、次のような JSON 出力が表示されるはずです。

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> `netsh portproxy` ルールは再起動後も維持されますが、`wsl --shutdown` 後に WSL ゲートウェイ IP が変わる場合があります。再起動後に WSL から Lemonade にアクセスできなくなった場合は、更新されたゲートウェイ IP を取得し、この新しい IP でプロキシを更新してください。

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## OpenClaw のインストールと設定

### OpenClaw のインストール
<!-- @os:windows -->
> このセクションのコマンドは **WSL ターミナル**内で実行してください。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` フラグはインタラクティブなセットアップウィザードをスキップします。次のステップでモデルバックエンドを手動で設定することで、使用するモデルとサーバーを正確に制御できます。

新しいターミナルを開き、インストールを確認します。

```bash
openclaw --version
```

> **ヒント:** インストール後に `command not found` と表示された場合は、npm のグローバル bin ディレクトリを PATH に追加してください。
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> これを永続化するには、上記の行を `~/.bashrc` または `~/.zshrc` ファイルに追加してください。

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Lemonade を使用するように OpenClaw を設定する

OpenClaw の非インタラクティブなオンボーディングを実行します。
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

このコマンドは OpenClaw の設定を `~/.openclaw/openclaw.json` に書き込みます。

> **OpenClaw のコンテキストウィンドウのサイズ設定:** OpenClaw のコンパクションは `contextTokens > contextWindow − reserveTokens` のときにトリガーされます。デフォルトの `reserveTokensFloor` は 20,000 トークンであり、これより低い場合に `reserveTokens` を上書きするフロアとして機能します。そのため、モデルコンテキストが約 37k 未満の場合、無限コンパクションループが発生します。設定でリザーブを低く設定してフロアを無効にすれば、すべてのモデルに適用されます。モデルごとの調整は不要です。
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` はリザーブ自体ではなく*フロア*（最小ガード）です。フロアのみを設定しても効果はありません。`reserveTokensFloor: 0` はガードを無効にし、より低い `reserveTokens` が受け入れられるようにします。
>
> **適用するタイミング:** モデルの有効なコンテキストウィンドウが約 37k 未満の場合（モデルが小さい場合（例: 8k、16k、32k）や、Lemonade でコンテキストを意図的に低い値に制限している場合（例: 128k モデルをロードしてコンテキストを 16k に設定している場合））にこの設定を使用してください。これを適用しないと、OpenClaw は起動時に無限コンパクションループに入ります。
>
> **フルコンテキストの大規模コンテキストモデル:** 完全にスキップできます。デフォルト設定で問題なく動作し、ウィンドウがいっぱいになる前にコンパクションが開始され、モデルには長い応答を生成するための十分な余裕があります。適用する場合は、`reserveTokens: 4096` により応答長が約 4k トークンに制限され、長いファイル生成や詳細な計画が途中で切れる可能性があることに注意してください。
>
> **追加場所:** `compaction` ブロックを `openclaw.json`（通常は `~/.openclaw/openclaw.json`）の `agents.defaults` 内に配置してください。
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> 設定の残りの部分（ゲートウェイ、チャンネル、モデルなど）は変更不要です。追加が必要なのは `compaction` キーのみです。

### （推奨）Docker サンドボックスを有効にする

OpenClaw は、すべてのエージェントのファイルおよびコード操作をホスト上で直接実行するのではなく、隔離された Docker コンテナを通じてルーティングできます。これにより、意図しないアクションの影響範囲をサンドボックス内に限定し、ホストのファイルシステムとネットワークを保護します。

サンドボックスイメージを一度ビルドします（Docker がインストールされている必要があります）。

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

`~/.openclaw/openclaw.json` の既存の `agents.defaults` ブロック内に `sandbox` キーを追加するには、次を実行します。

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

サンドボックスコンテナはデフォルトで**ネットワークアクセスがありません**。バインドマウントとネットワークオーバーライドについては、[サンドボックスリファレンス](https://docs.openclaw.ai/gateway/sandboxing)を参照してください。

> #### トラブルシューティング: Docker の権限拒否
> 
> Docker コマンドの実行時に「permission denied」が表示された場合:
> 
> **ステップ 1: ユーザーを docker グループに追加する**
> 
> ```bash
> sudo groupadd docker                    # 必要に応じてグループを作成
> sudo usermod -aG docker $USER           # 自分をグループに追加
> newgrp docker                           # 変更を有効化
> docker run hello-world                  # テスト
> ```
> 
> **ステップ 2: エラーが続く場合は、永続的な修正を適用する**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> その後、システムを**再起動**してください。
> 
> **一時的な簡易修正**（再起動後にリセットされます）:
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### OpenClaw ゲートウェイを起動する

ゲートウェイは、エージェントループを管理しダッシュボードを提供する OpenClaw プロセスです。

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

ゲートウェイが起動している状態で、2 番目のターミナルでこれを実行してダッシュボードを開きます。

```bash
openclaw dashboard
```

ゲートウェイはループバックにバインドされているため、同じマシンから開いた場合はダッシュボードが自動認証されます。ローカルアクセスにはトークンの入力やデバイスの承認は不要です。Lemonade モデルがアクティブなバックエンドとして表示された OpenClaw ダッシュボードが表示されるはずです。

> サンドボックスを有効にしている場合は、ダッシュボードからエージェントに `run hostname` を実行するよう依頼することで確認できます。マシンのホスト名ではなく短いコンテナ ID が表示された場合、サンドボックスは正常に動作しています。

**おめでとうございます。完全にローカルな AI エージェントスタックをゼロから構築しました。**

> **ゲートウェイトークンが必要な場合:** `openclaw dashboard --no-open` を実行すると、トークンが埋め込まれたダッシュボード URL が表示されます（クリップボードへのコピーも試みます）。または、トークンは `~/.openclaw/openclaw.json` の `gateway.auth.token` にあります。
>
> **リモートデバイスの承認:** 別のマシンや電話からダッシュボードを開くと、ブラウザにリクエスト ID が表示されます。ゲートウェイを実行しているマシンに戻り、次を実行します。
> ```bash
> openclaw devices approve <requestId>
> ```
> これはリモートまたはセカンダリデバイスにのみ必要です。同じマシンからのループバックアクセスは自動認証されます。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## オプション: 通信チャンネルを接続する

ゲートウェイが起動したら、任意のデバイスからローカルエージェントにアクセスできます。セットアップに合ったオプションを選択してください。OpenClaw は [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram)、およびその他のチャンネルをサポートしています。完全なリストは [docs.openclaw.ai](https://docs.openclaw.ai) を参照してください。

---

### オプション A: Discord

Discord では、ボットを追加するために**管理者アクセス権を持つ**サーバーが必要です。サーバーを共有しているが所有していない場合は、代わりにオプション B（Telegram）を使用してください。

#### Discord アカウントとサーバーを作成する

Discord アカウントをお持ちでない場合は、[discord.com](https://discord.com) でサインアップしてください。また、管理者であるサーバーが必要です。Discord サイドバーの **+** アイコンをクリックし、**Create My Own** を選択して作成してください。プライベートサーバーで問題ありません。

#### Discord アプリケーションとボットを作成する

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、**New Application** をクリックします。名前を付けてください（例: "openclaw-bot"）。
2. サイドバーで **Bot** をクリックします。ボットのユーザー名を設定します。
3. Bot ページのまま、**Privileged Gateway Intents** までスクロールし、以下を有効にします。
   - **Message Content Intent**（必須）
   - **Server Members Intent**（推奨）
4. 上にスクロールして **Reset Token** をクリックし、ボットトークンを生成します。コピーしてください。

#### ボットをサーバーに追加する

1. サイドバーで **OAuth2/ URL Generator** をクリックします。
2. **Scopes** で `bot` と `applications.commands` を有効にします。
3. **Bot Permissions** で以下を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成された URL をコピーしてブラウザに貼り付け、サーバーを選択して確認します。ボットがサーバーのメンバーリストに表示されるはずです。

#### ID を収集する

Discord で開発者モードを有効にします（**User Settings/ Advanced/ Developer Mode**）。次に:
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

#### サーバーメンバーからの DM を許可する

サーバーアイコンを右クリック/ **Privacy Settings**/ **Direct Messages** をオンに切り替えます。これにより、ボットがあなたに DM を送れるようになります。これはペアリングステップに必要です。

#### Discord 用に OpenClaw を設定する

ボットトークンを環境変数として保存し、Discord を有効にし、トークンを参照し、サーバーをホワイトリストに登録する単一のパッチファイルを作成します。`<server_id>` と `<user_id>` を上で収集した ID に置き換えてください。

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **エージェントにこの設定を依頼しないでください。** サンドボックスが有効な場合、エージェントはサンドボックス内から `~/.openclaw/openclaw.json` に書き込むことができません。代わりに、ホスト上で上記の CLI コマンドを使用してください。

新しいチャンネル設定を反映させるためにゲートウェイを再起動します。

```bash
openclaw gateway run --bind loopback --port 18789
```

数秒以内にゲートウェイの出力に `logged in to discord as <bot-name>` と表示されるはずです。

#### Discord アカウントをペアリングする

Discord でボットに DM を送ります。ボットが短いペアリングコードで返信します。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClaw を実行しているマシンで承認します。
```bash
openclaw pairing approve discord <CODE>
```

> ペアリングコードは 1 時間後に期限切れになります。

これで Discord から直接エージェントとチャットし、ローカルハードウェアにタスクをオフロードできます。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### オプション B: Telegram

Telegram はほとんどのユーザーにとって Discord より簡単です。サーバーも管理者アクセスも不要です。

#### Telegram ボットを作成する

1. Telegram を開き、**@BotFather** にメッセージを送ります。
2. `/newbot` を送信し、プロンプトに従います。提供されるボットトークンを保存してください。

#### Telegram 用に OpenClaw を設定する

トークンを環境変数として保存します。

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

チャンネル設定を `~/.openclaw/openclaw.json` に追加します（またはダッシュボード経由でパッチを適用します）。

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

ゲートウェイを再起動し、Telegram でボットにメッセージを送ります。ペアリングを承認します。

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

ペアリングコードは 1 時間後に期限切れになります。これで Telegram DM を通じてエージェントとチャットできます。

---

## 次のステップ

エージェントがスマートフォンからコマンドを受け取り、ローカルマシン上でアクションを実行できるようになりました。次の 3 つの方向性を探ってみてください。

1. **株式市場サマライザー**: OpenClaw をスケジュールして、一定間隔で金融 API からデータを取得し、ローカルモデルでその日の動きを要約し、毎朝選択したチャンネルを通じてスマートフォンにダイジェストを送信します。

2. **ファインチューニングモニター**: Telegram または Discord からリモートでトレーニングジョブを開始し、エージェントにトレーニングログを追跡させ、定期的な損失値、GPU 使用率、ディスク使用量をスマートフォンに報告させます。実行が停止したり VRAM がスパイクしたりした場合、マシンの前にいなくてもすぐに通知されます。

3. **ローカル VLM を使った IoT**: カメラを玄関に向け、Lemonade 上でビジョンモデルを実行し、OpenClaw にオンデマンドまたはトリガーに基づいてフレームを分析させます。スマートフォンから「今日荷物は届きましたか？」と尋ねると、自分のハードウェアから直接回答が得られます。