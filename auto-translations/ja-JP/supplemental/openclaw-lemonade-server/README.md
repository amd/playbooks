<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# OpenClawをLemonade Serverバックエンドで実行する

## 概要

[**OpenClaw**](https://openclaw.ai/)は、コードを書いて実行し、ファイルを管理し、複雑な複数ステップのタスクをあなたに代わって遂行できる自律型AIエージェントです。質問に答えるだけのチャットアシスタントとは異なり、OpenClawはシステム上で実際にアクションを実行するため、要求の厳しいエージェントループに対応できる高速で高性能なAIバックエンドを必要とします。

[**Lemonade Server**](https://lemonade-server.ai/)がそのバックエンドです。これは、GenAIモデルをお使いのハードウェア上で直接実行し、業界標準のOpenAI APIを通じて公開するオープンソースのローカル推論サーバーです。

両者を組み合わせることで、完全にローカルなAIエージェントスタックが構成されます。Lemonadeがモデル推論を担当し、OpenClawがモデルの出力を実際のアクションに変換するエージェントループを提供します。

> **続ける前に:** OpenClawは高度に自律的なAIエージェントです。どのようなAIエージェントであっても、システムへのアクセスを許可することで予測不能または意図しない結果が生じる可能性があります。リスクを理解し、自律的なソフトウェアが代理で動作することに納得できる場合にのみ、先に進んでください。

---

## このプレイブックで学べること

このプレイブックを完了すると、以下ができるようになります。

- **Lemonade Server**について学ぶ
- **OpenClawをインストール**し、AIバックエンドとして**Lemonade Serverを指定する**。
- **OpenClawゲートウェイを起動**し、エージェントが動作可能な状態であることを確認する。
- **コミュニケーションチャネル**（DiscordまたはTelegram）を接続し、任意のデバイスからエージェントとチャットできるようにする。

---

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @os:linux -->
- `apt-get`を使用できる**Ubuntu 24.04+**または互換性のあるDebianベースのLinuxディストリビューションを実行しているPC
- 少なくとも**12 GBのRAM**（より大規模なモデルには64 GB以上を推奨）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（オプション、OpenClawのサンドボックス化用）

- モデルの重みのために**約10～30 GBの空きディスク容量**
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11**を実行しているPC
- 少なくとも**12 GBのRAM**（より大規模なモデルには64 GB以上を推奨）
- モデルの重みのために**約10～30 GBの空きディスク容量**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（オプション、OpenClawのサンドボックス化用）
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

このプレイブックでの推奨モデルは、Unsloth製の**Qwen3.6-35B-A3B-GGUF**です。これは、263kトークンのコンテキストウィンドウを持つ、エージェントのワークロードに適した強力なMoEモデルです。このモデルはUD-Q4_K_XL量子化を使用しています。今すぐプルしましょう。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

続いて、大きなコンテキストウィンドウでロードし、その設定を今後の実行のために保存します。

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

このモデルのデフォルトのコンテキスト長は262,144トークンです。メモリ不足（OOM）エラーが発生した場合は、コンテキストウィンドウを小さくすることを検討してください。ただし、Qwen3.6は複雑なタスクに拡張コンテキストを活用するため、思考能力を維持するために少なくとも128Kトークンのコンテキスト長を維持することをお勧めします。

> **ヒント: エージェントの応答を高速化するために思考モードを無効化する:** Qwen3.6-35B-A3Bはデフォルトで思考モードで動作し、各応答の前にレイテンシーが加わります。エージェントループではこのオーバーヘッドがすぐに蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json)リポジトリには、思考モードを無効化するすぐに使える設定が用意されています。使用するには、ファイルをダウンロードしてインポートします。
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

## WSLのセットアップ

OpenClawはWSL内で実行し（推奨）、Windows上でネイティブに動作するLemonadeに接続します。これにより、Lemonadeのウィンドウズ側でのGPUアクセラレーションを維持しつつ、OpenClaw用のLinuxシェル環境を得られます。

### WSLとUbuntuのインストール

管理者としてPowerShellを開き、WSLカーネルをインストールします。

```powershell
wsl --install --no-distribution
```

続いてUbuntuをインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSLでsystemdを有効化する

Ubuntuターミナル内で以下を実行します。

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

WSLを再起動します。

```powershell
wsl --shutdown
wsl
```

### WindowsからWSLへのLemonadeのブリッジ

WSL2は仮想ネットワーク内で動作します。Windows上のLemonadeは`127.0.0.1`にバインドされますが、WSLから直接到達することはできません。Windowsのポートプロキシを使用して、WSLのゲートウェイIPからWindowsのlocalhostへトラフィックを転送します。

**WSLのゲートウェイIPを確認します**（WSL内で実行）。

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加します**（管理者としてPowerShellで実行し、`<WSL-Gateway-IP>`をお使いのWSLゲートウェイIPに置き換えてください）。

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**ファイアウォールルールを追加します**（同じ昇格済みPowerShellで実行）。

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSLから確認します**。

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前のステップですでにQwen3.6-35B-A3B-GGUFモデルをロードしている場合は、以下のようなJSON出力が表示されるはずです。

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

> `netsh portproxy`ルールは再起動後も維持されますが、`wsl --shutdown`後にWSLのゲートウェイIPが変わることがあります。再起動後にWSLからLemonadeに到達できなくなった場合は、更新後のゲートウェイIPを取得し、新しいIPでプロキシを更新してください。

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

## OpenClawのインストールと構成

### OpenClawのインストール
<!-- @os:windows -->
> このセクションのコマンドは、**WSLターミナル**内で実行してください。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard`フラグは対話型セットアップウィザードをスキップします。次のステップでモデルバックエンドを手動で構成することになるため、どのモデルとサーバーを使用するかを細かく制御できます。

新しいターミナルを開き、インストールを確認します。

```bash
openclaw --version
```

> **ヒント:** インストール後に`command not found`と表示される場合は、npmのグローバルbinディレクトリをPATHに追加してください。
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> これを恒久的にするには、上記の行を`~/.bashrc`または`~/.zshrc`ファイルに追加してください。

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
### OpenClawをLemonadeで使用するように設定する

OpenClawの非対話型オンボーディングを実行します。
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

このコマンドは、OpenClawの設定を`~/.openclaw/openclaw.json`に書き込みます。

> **OpenClawのコンテキストウィンドウサイズ設定:** OpenClawの圧縮処理は、`contextTokens > contextWindow − reserveTokens`のときにトリガーされます。デフォルトの`reserveTokensFloor`は20,000トークンで、これは`reserveTokens`より低い場合にそれを上書きする下限値であるため、コンテキストが約37k未満のモデルでは無限圧縮ループが発生します。設定内で一度低い予約値を設定し下限を無効化すれば、それがすべてのモデルに適用され、モデルごとの調整は不要です:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor`は*下限値*（最低保証値）であり、予約値そのものではないため、下限値のみを設定しても効果はありません。`reserveTokensFloor: 0`はこの保証を無効化し、より低い`reserveTokens`が受け入れられるようにします。
>
> **適用すべき場合:** モデルの実効コンテキストウィンドウが約37k未満の場合、この設定を使用してください。これは、モデル自体が小さい場合（例: 8k、16k、32k）や、意図的に低い値に制限している場合（例: 128kモデルをロードしつつLemonadeでコンテキストを16kに設定している場合）に該当します。この設定を行わないと、OpenClawは起動時に無限圧縮ループに陥ります。
>
> **フルコンテキストの大規模コンテキストモデルの場合:** この設定は完全にスキップできます。デフォルト設定で問題なく動作し、ウィンドウが満杯になるかなり前に圧縮が開始され、モデルには長い応答を生成するための十分な余裕があります。もしこの設定を適用する場合は、`reserveTokens: 4096`によって応答長が約4kトークンに制限されることに注意してください。これにより、長いファイル生成や詳細な計画が途中で切れる可能性があります。
>
> **設定を追加する場所:** `compaction`ブロックは、`openclaw.json`（通常は`~/.openclaw/openclaw.json`）内の`agents.defaults`の中に配置します:
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
> それ以外の設定（gateway、channels、modelsなど）は変更する必要はなく、`compaction`キーのみを追加すれば十分です。

### （推奨）Dockerサンドボックス化を有効にする

OpenClawは、エージェントによるファイル操作やコード操作をホスト上で直接実行するのではなく、すべて隔離されたDockerコンテナ経由で実行するように設定できます。これにより、意図しない操作が発生した場合の影響範囲がサンドボックス内に限定され、ホストのファイルシステムやネットワークには影響が及びません。

サンドボックスイメージを一度だけビルドします（Dockerがインストールされている必要があります）:

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

`~/.openclaw/openclaw.json`内の既存の`agents.defaults`ブロック内に`sandbox`キーを追加するには、次を実行します:

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

サンドボックスコンテナは、デフォルトでは**ネットワークアクセスを持ちません**。バインドマウントやネットワークのオーバーライドについては、[サンドボックス化に関するリファレンス](https://docs.openclaw.ai/gateway/sandboxing)を参照してください。

> #### トラブルシューティング: Dockerのアクセス権限が拒否される場合
> 
> Dockerコマンドの実行時に「permission denied」と表示される場合:
> 
> **手順1: ユーザーをdockerグループに追加する**
> 
> ```bash
> sudo groupadd docker                    # 必要に応じてグループを作成
> sudo usermod -aG docker $USER           # 自分自身をグループに追加
> newgrp docker                           # 変更を有効化
> docker run hello-world                  # 動作確認
> ```
> 
> **手順2: エラーが解消しない場合は、恒久的な修正を適用する**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> その後、システムを**再起動**してください。
> 
> **一時的な簡易対応**（再起動後にリセットされます）:
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

<!-- @os:linux -->
## （推奨）FirecrawlサービスとのOpenClaw連携

[Firecrawl](https://docs.firecrawl.dev/introduction)は、これらの課題を回避し、OpenClawによる自動化の可能性を最大限に引き出すことができる、セルフホスト型のWebクローリングおよびコンテンツ抽出サービスを提供します。

このセットアップでは、OpenClawはPodmanによって管理される一連のDockerコンテナとして実行されます。ライフサイクル管理と自動起動を簡素化するため、Firecrawlをユーザーレベルの`systemd`サービスとして登録し、基盤となるPodman Composeスタックをオーケストレーションします。これにより、コンテナを直接操作する代わりに、標準の`systemctl --user`コマンドを使用して、OpenClawのgatewayの起動・停止、およびFirecrawlサービスの検証が行えるようになります。

わかりやすくするため、プロセス全体を4つのステップに分けています:

---

### 1. システムサービスを登録する
systemdのユーザー設定ディレクトリに移動します:
```bash
cd ~/.config/systemd/user
```
`firecrawl.service`という名前の新しいファイルを作成し、開きます。
```bash
nano firecrawl.service
```
以下の設定内容をコピーして貼り付けます:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
この時点で、サービスは定義されていますが、まだ`systemd`には登録されていません。
上記で作成したファイル名と完全に一致していることを確認してから、以下を実行してください:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功すると、次のような出力が表示されます:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/`には、自動起動するように設定されたサービスへのシンボリックリンクが含まれています。
### 2. Firecrawlの設定

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)は、スクレイピングおよびデータ処理環境を完全に制御したいユーザーに最適ですが、その分メンテナンスや設定の手間が増えるというトレードオフがあります。

まずリポジトリをクローンします:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
`/firecrawl`ルートディレクトリに`.env`を作成します: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Podman ComposeでOpenClawをデプロイする

先に進む前に、最新のOpenClaw Dockerイメージをプルしていることを確認してください:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
完了したら、OpenClaw Composeファイル[openclaw-compose.yaml](assets/openclaw-compose.yaml)をダウンロードし、`/firecrawl`ルートディレクトリに配置します:

> `WorkingDirectory=${HOME}/firecrawl`で指定されているように、`systemd`がサービスを正しく検出して起動するためには、この規約に従う必要があります。

> 必要に応じて、Firecrawlサービスを追加してスタックをいつでも拡張できます。利用可能なサービスの全リストは、公式の[Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)に記載されています。

### 4. FirecrawlからOpenClawサービスを起動する

`systemd`に制御を渡す前に、スタックを手動で実行してすべてが正しく動作することを確認します:
```bash
podman compose -f openclaw-compose.yaml up -d
```
すべてが正しく構成されていれば、OpenClawコンテナが立ち上がり、コマンドラインの出力は次のようになるはずです。
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

確認できたら、先に進む前にスタックを停止します:
```bash
podman compose -f openclaw-compose.yaml down
```
サービスを開始する前に、`firecrawl`ディレクトリとその`.env`ファイルに正しい所有権と権限が設定されていることを確認する必要があります。
これは、サービスが起動時に認証情報を書き込むために不可欠です。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
すべての確認が済んだので、`systemd`経由でサービスを開始します:
```bash
systemctl --user start firecrawl.service
```
[The OpenClaw Actions](https://docs.openclaw.ai/)はインタラクティブなコンテナ内からアクセス可能で、Webダッシュボードは同じホストとポート http://127.0.0.1:18789 で利用できます。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN`の取得

サービスが起動して実行されると、ホームフォルダー内に新しい`.openclaw`ディレクトリ(~/.openclaw)が作成されていることに気づくでしょう。このディレクトリはデフォルトでロックされているため、ゲートウェイトークンを取得するにはロックを解除する必要があります。

1. ディレクトリへのアクセス権を付与します:
```bash
sudo chmod 777 ~/.openclaw/
```
2. ゲートウェイトークンを読み取ります:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
出力内で`OPENCLAW_GATEWAY_TOKEN`の値を探してください。

3. ブラウザでゲートウェイダッシュボード http://127.0.0.1:18789 を開きます。認証を求められたらトークンを貼り付けてください。

サービスを停止するには、次を実行します:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## OpenClaw Gatewayを起動する

ゲートウェイは、エージェントループを管理しダッシュボードを提供するOpenClawプロセスです。

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

ダッシュボードを開くには、ゲートウェイが実行されたままの状態で、2つ目のターミナルで次を実行します:

```bash
openclaw dashboard
```

ゲートウェイはループバックにバインドされているため、同じマシンから開いた場合、ダッシュボードは自動的に認証されます。ローカルアクセスにはトークンの入力やデバイス承認は必要ありません。アクティブなバックエンドとしてLemonadeモデルが表示されたOpenClawダッシュボードが表示されるはずです。

> サンドボックス化を有効にしている場合は、ダッシュボードからエージェントに`run hostname`を実行させることで確認できます。マシンのホスト名ではなく短いコンテナIDが表示されれば、サンドボックスは正常に機能しています。

**おめでとうございます。これで完全にローカルなAIエージェントスタックをゼロから構築できました。**

> **ゲートウェイトークンが必要ですか？** `openclaw dashboard --no-open`を実行すると、トークンが埋め込まれたダッシュボードURLが表示されます(クリップボードへのコピーも試みられます)。あるいは、トークンは`~/.openclaw/openclaw.json`内の`gateway.auth.token`にあります。
>
> **リモートデバイスの承認:** 2台目のマシンやスマートフォンからダッシュボードを開くと、ブラウザにリクエストIDが表示されます。ゲートウェイを実行しているマシンに戻り、次を実行します:
> ```bash
> openclaw devices approve <requestId>
> ```
> これはリモートまたは2台目のデバイスの場合にのみ必要です。同じマシンからのループバックアクセスは自動的に認証されます。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャネルを接続する

ゲートウェイが実行されると、任意のデバイスからローカルエージェントにアクセスできるようになります。ご自身の環境に合ったオプションを選択してください。OpenClawは[Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram)、その他のチャネルをサポートしています。全リストは[docs.openclaw.ai](https://docs.openclaw.ai)をご覧ください。

---

### オプションA: Discord

Discordでは、ボットを追加するために**管理者権限を持つ**サーバーが必要です。サーバーを共有していても所有していない場合は、代わりにオプションB(Telegram)をご利用ください。

#### Discordアカウントとサーバーの作成

Discordアカウントをお持ちでない場合は、[discord.com](https://discord.com)でサインアップしてください。また、管理者権限を持つサーバーも必要です。Discordサイドバーの**+**アイコンをクリックし、**Create My Own**を選択して作成してください。プライベートサーバーで問題ありません。

#### Discordアプリケーションとボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスし、**New Application**をクリックします。名前を付けてください(例: "openclaw-bot")。
2. サイドバーで**Bot**をクリックします。ボットのユーザー名を設定します。
3. Botページ内で下にスクロールし、**Privileged Gateway Intents**で以下を有効にします:
   - **Message Content Intent**(必須)
   - **Server Members Intent**(推奨)
4. 上にスクロールして戻り、**Reset Token**をクリックしてボットトークンを生成します。コピーしてください。

#### サーバーへのボットの追加

1. サイドバーで**OAuth2/ URL Generator**をクリックします。
2. **Scopes**で`bot`と`applications.commands`を有効にします。
3. **Bot Permissions**で以下を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成されたURLをコピーしてブラウザに貼り付け、サーバーを選択して確認します。ボットがサーバーのメンバーリストに表示されるはずです。
#### IDを収集する

Discordで開発者モードを有効にします(**ユーザー設定/ 詳細設定/ 開発者モード**)。その後:
- サーバーアイコンを右クリック: **サーバーIDをコピー**
- 自分のアバターを右クリック: **ユーザーIDをコピー**

#### サーバーメンバーからのDMを許可する

サーバーアイコンを右クリック/ **プライバシー設定**/ **ダイレクトメッセージ**をオンに切り替えます。これにより、ボットがあなたにDMを送れるようになり、ペアリング手順で必要になります。

#### Discord用にOpenClawを設定する

ボットトークンを環境変数として保存し、Discordを有効化し、トークンを参照し、サーバーをallowlistに登録する単一のパッチファイルを作成します。上記で収集した`<server_id>`と`<user_id>`を実際のIDに置き換えてください。

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

> **エージェントに設定を任せることに頼らないでください。** サンドボックスが有効な場合、エージェントはサンドボックス内から`~/.openclaw/openclaw.json`に書き込むことができません。代わりに、上記のCLIコマンドをホスト上で使用してください。

新しいチャンネル設定を反映させるため、ゲートウェイを再起動します:

```bash
openclaw gateway run --bind loopback --port 18789
```

数秒以内にゲートウェイの出力に`logged in to discord as <bot-name>`と表示されるはずです。

#### Discordアカウントをペアリングする

Discordでボットにダイレクトメッセージを送ります。ボットは短いペアリングコードで返信します。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClawを実行しているマシン上でそれを承認します:
```bash
openclaw pairing approve discord <CODE>
```

> ペアリングコードは1時間で期限切れになります。

これで、Discordから直接エージェントとチャットし、ローカルハードウェアにタスクをオフロードできるようになります。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### オプションB: Telegram

TelegramはほとんどのユーザーにとってDiscordよりシンプルで、サーバーも管理者権限も不要です。

#### Telegramボットを作成する

1. Telegramを開き、**@BotFather**にメッセージを送ります。
2. `/newbot`を送信し、指示に従います。渡されるボットトークンを保存してください。

#### Telegram用にOpenClawを設定する

トークンを環境変数として保存します:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

チャンネル設定を`~/.openclaw/openclaw.json`に追加します(またはダッシュボード経由でパッチを適用します):

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

ゲートウェイを再起動し、Telegramでボットに何かメッセージを送ります。ペアリングを承認します:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

ペアリングコードは1時間で期限切れになります。これで、TelegramのDMを通じてエージェントとチャットできるようになります。

---

## 次のステップ

これで、エージェントがスマートフォンからコマンドを受け取り、ローカルマシン上で動作できるようになったので、探求する価値のある3つの方向性を紹介します:

1. **株式市場サマライザー**: OpenClawをスケジュールして、一定間隔で金融APIからデータを取得し、ローカルモデルでその日の値動きを要約し、選択したチャンネルを通じて毎朝スマートフォンにダイジェストをプッシュします。

2. **ファインチューニングモニター**: TelegramまたはDiscordからリモートでトレーニングジョブを開始し、エージェントにトレーニングログを追跡させ、定期的な損失値、GPU使用率、ディスク使用量をスマートフォンに報告させます。実行が停止したり、VRAMが急上昇したりした場合、マシンの前にいなくてもすぐに気付くことができます。

3. **ローカルVLMを使ったIoT**: カメラを玄関に向け、Lemonade上でビジョンモデルを実行し、OpenClawにオンデマンドまたはトリガーでフレームを分析させます。スマートフォンから「今日荷物は届いた?」と尋ねれば、自分のハードウェアから的確な答えが得られます。

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->