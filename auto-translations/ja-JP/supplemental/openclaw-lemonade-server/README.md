<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# LemonadeサーバーをバックエンドとしてOpenClawを実行する

## 概要

[**OpenClaw**](https://openclaw.ai/) は、コードの記述と実行、ファイルの管理、複雑な多段階タスクの実行をユーザーに代わって行える自律型AIエージェントです。質問に答えるだけのチャットアシスタントとは異なり、OpenClawはシステム上で実際にアクションを実行します。つまり、要求の厳しいエージェントループに対応できる、高速で高性能なAIバックエンドが必要になります。

[**Lemonadeサーバー**](https://lemonade-server.ai/) がそのバックエンドです。これは、GenAIモデルをお使いのハードウェア上で直接実行し、業界標準のOpenAI APIを通じて公開する、オープンソースのローカル推論サーバーです。

両者を組み合わせることで、完全にローカルなAIエージェントスタックが構築されます。Lemonadeがモデル推論を担当し、OpenClawがモデルの出力を実際のアクションに変換するエージェントループを提供します。

> **続ける前に:** OpenClawは高度に自律的なAIエージェントです。AIエージェントにシステムへのアクセスを許可すると、予測不能または意図しない結果が生じる可能性があります。リスクを理解し、自律的なソフトウェアが自分に代わって動作することに納得できる場合にのみ、続行してください。

---

## この記事で学べること

このプレイブックを最後まで読むと、以下のことができるようになります。

- **Lemonadeサーバー**について学ぶ
- **OpenClawをインストール**し、AIバックエンドとして**Lemonadeサーバーを指定する**。
- **OpenClawゲートウェイを起動**し、エージェントが動作可能であることを確認する。
- **通信チャネル**（DiscordまたはTelegram）を接続し、あらゆるデバイスからエージェントとチャットできるようにする。

---

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

<!-- @os:linux -->
- `apt-get` を使用できる**Ubuntu 24.04+**、または互換性のあるDebianベースのLinuxディストリビューションを実行しているPC
- **12 GB以上のRAM**（より大きなモデルを使用する場合は64 GB以上を推奨）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（OpenClawをサンドボックス化する場合のみ、任意）

- モデルの重み用に**約10～30 GBの空きディスク容量**
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11**を実行しているPC
- **12 GB以上のRAM**（より大きなモデルを使用する場合は64 GB以上を推奨）
- モデルの重み用に**約10～30 GBの空きディスク容量**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（OpenClawをサンドボックス化する場合のみ、任意）
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

このプレイブックで推奨するモデルは、Unsloth提供の**Qwen3.6-35B-A3B-GGUF**です。263kトークンのコンテキストウィンドウを備えた強力なMoEモデルで、エージェント向けのワークロードに適しています。このモデルはUD-Q4_K_XL量子化を使用しています。今すぐプルしてください。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

次に、大きなコンテキストウィンドウでロードし、その設定を今後の実行のために保存します。

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

このモデルのデフォルトのコンテキスト長は262,144トークンです。メモリ不足（OOM）エラーが発生した場合は、コンテキストウィンドウを小さくすることを検討してください。ただし、Qwen3.6は複雑なタスクのために拡張されたコンテキストを活用するため、思考能力を維持するために少なくとも128Kトークンのコンテキスト長を維持することをお勧めします。

> **ヒント: エージェントの応答を高速化するために思考を無効にする:** Qwen3.6-35B-A3Bはデフォルトで思考モードで動作するため、各応答の前に遅延が発生します。エージェントループでは、このオーバーヘッドが急速に蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリには、思考を無効にする、そのまま使える構成が用意されています。使用するには、ファイルをダウンロードしてインポートします。
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

OpenClawはWSL内で実行し（推奨）、Windows上でネイティブに動作しているLemonadeに接続します。これにより、Windows側でLemonadeのGPUアクセラレーションを維持しつつ、OpenClaw用のLinuxシェル環境を利用できます。

### WSLとUbuntuのインストール

PowerShellを管理者として開き、WSLカーネルをインストールします。

```powershell
wsl --install --no-distribution
```

続いてUbuntuをインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSLでsystemdを有効にする

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

### WindowsからWSLへLemonadeをブリッジする

WSL2は仮想ネットワーク内で動作します。Windows上のLemonadeは`127.0.0.1`にバインドされているため、WSLから直接アクセスすることはできません。Windowsのポートプロキシを使用して、WSLゲートウェイIPからWindowsのlocalhostへトラフィックを転送します。

**WSLのゲートウェイIPを確認する**（WSL内で実行）:

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加する**（PowerShellを管理者として実行し、`<WSL-Gateway-IP>` をお使いのWSLゲートウェイIPに置き換えてください）:

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**ファイアウォールルールを追加する**（同じ管理者権限のPowerShell）:

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSLから確認する**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前のステップですでにQwen3.6-35B-A3B-GGUFモデルをロードしている場合、以下のようなJSON出力が表示されるはずです。

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

> `netsh portproxy` のルールは再起動後も保持されますが、`wsl --shutdown` の後にWSLのゲートウェイIPが変わることがあります。再起動後にWSLからLemonadeへ到達できなくなった場合は、更新後のゲートウェイIPを取得し、その新しいIPでプロキシを更新してください。

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

## OpenClawのインストールと設定

### OpenClawのインストール
<!-- @os:windows -->
> このセクションのコマンドは、**WSLターミナル**内で実行してください。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` フラグは対話形式のセットアップウィザードをスキップします。次のステップでモデルバックエンドを手動で設定するため、どのモデルとサーバーを使用するかを正確に制御できます。

新しいターミナルを開き、インストールを確認します。

```bash
openclaw --version
```

> **ヒント:** インストール後に `command not found` と表示される場合は、npmのグローバルbinディレクトリをPATHに追加してください。
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
### OpenClaw を Lemonade で使用するための設定

OpenClaw の非対話型オンボーディングを実行します。
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

このコマンドは、OpenClaw の設定を `~/.openclaw/openclaw.json` に書き込みます。

> **OpenClaw のコンテキストウィンドウサイズ設定:** OpenClaw の圧縮(compaction)は `contextTokens > contextWindow − reserveTokens` の条件でトリガーされます。デフォルトの `reserveTokensFloor` は 20,000 トークンで、この値は `reserveTokens` がそれより低い場合にそれを上書きするフロア値であるため、コンテキストが約 37k トークンを下回るモデルでは無限圧縮ループが発生します。設定内で reserve を低く設定し、フロアを一度無効化すれば、すべてのモデルに適用され、モデルごとの個別調整は不要です:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` は *フロア*(最小保証値)であり、reserve そのものではないため、フロアだけを設定しても効果はありません。`reserveTokensFloor: 0` とすることでこのガードを無効化し、より低い `reserveTokens` の値が受け入れられるようになります。
>
> **これを適用すべき場面:** モデルの実効コンテキストウィンドウが約 37k を下回る場合(モデル自体が小さい場合、例えば 8k、16k、32k、または意図的に低い値に制限している場合、例えば 128k モデルを読み込みつつ Lemonade でコンテキストを 16k に設定している場合)に、この設定を使用してください。設定しない場合、OpenClaw は起動時に無限圧縮ループに陥ります。
>
> **フルコンテキストで使用する大規模コンテキストモデルの場合:** この設定は完全にスキップできます。デフォルト設定で問題なく動作し、ウィンドウが満杯になるかなり前に圧縮が働き、モデルには長い応答を生成するための十分な余裕があります。もし適用する場合は、`reserveTokens: 4096` によって応答長が約 4k トークンに制限されることに注意してください。これは長いファイル生成や詳細なプランの生成を途中で打ち切ってしまう可能性があります。
>
> **追加する場所:** `compaction` ブロックは、`openclaw.json`(通常は `~/.openclaw/openclaw.json`)内の `agents.defaults` の中に配置してください:
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
> それ以外の設定(gateway、channels、models など)はそのままで、`compaction` キーのみを追加すれば問題ありません。

### (推奨)Docker サンドボックスの有効化

OpenClaw では、エージェントによるすべてのファイル操作やコード操作を、ホスト上で直接実行するのではなく、隔離された Docker コンテナ経由で実行するように設定できます。これにより、意図しない操作の影響範囲がサンドボックス内に限定され、ホストのファイルシステムやネットワークには影響が及びません。

サンドボックスイメージを一度だけビルドします(Docker がインストールされている必要があります):

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

以下を実行して、`~/.openclaw/openclaw.json` の既存の `agents.defaults` ブロック内に `sandbox` キーを追加します:

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

サンドボックスコンテナはデフォルトで**ネットワークアクセスがありません**。バインドマウントやネットワークの上書き設定については、[サンドボックスに関するリファレンス](https://docs.openclaw.ai/gateway/sandboxing)を参照してください。

> #### トラブルシューティング: Docker のパーミッションが拒否される場合
> 
> Docker コマンドを実行した際に「permission denied」というエラーが出る場合:
> 
> **手順 1: ユーザーを docker グループに追加する**
> 
> ```bash
> sudo groupadd docker                    # 必要であればグループを作成
> sudo usermod -aG docker $USER           # 自分自身をグループに追加
> newgrp docker                           # 変更を反映
> docker run hello-world                  # 動作確認
> ```
> 
> **手順 2: それでもエラーが解消しない場合、恒久的な修正を適用する**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> その後、システムを**再起動**してください。
> 
> **一時的な簡易対処法**(再起動後にリセットされます):
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

### OpenClaw ゲートウェイの起動

ゲートウェイは、エージェントループを管理し、ダッシュボードを提供する OpenClaw のプロセスです:

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

ダッシュボードを開くには、ゲートウェイを起動したまま、2つ目のターミナルで以下を実行します:

```bash
openclaw dashboard
```

ゲートウェイはループバックにバインドされているため、同じマシンから開いた場合、ダッシュボードは自動的に認証され、ローカルアクセスにはトークンの入力やデバイスの承認は不要です。Lemonade モデルがアクティブなバックエンドとして表示された OpenClaw ダッシュボードが表示されるはずです。

> サンドボックスを有効にしている場合は、ダッシュボードからエージェントに `run hostname` を実行させることで確認できます。マシンのホスト名の代わりに短いコンテナ ID が表示されれば、サンドボックスは正常に機能しています。

**おめでとうございます。これでゼロから完全にローカルな AI エージェントスタックを構築できました。**

> **ゲートウェイのトークンが必要ですか?** `openclaw dashboard --no-open` を実行すると、トークンが埋め込まれたダッシュボード URL が出力されます(同時にクリップボードへのコピーも試みられます)。あるいは、トークンは `~/.openclaw/openclaw.json` の `gateway.auth.token` にあります。
>
> **リモートデバイスの承認:** 2台目のマシンやスマートフォンからダッシュボードを開くと、ブラウザにリクエスト ID が表示されます。ゲートウェイを実行しているマシン側で、以下を実行してください:
> ```bash
> openclaw devices approve <requestId>
> ```
> これはリモートまたは副次的なデバイスの場合にのみ必要であり、同一マシンからのループバックアクセスは自動的に認証されます。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャネルの接続

ゲートウェイが起動すると、任意のデバイスからローカルエージェントにアクセスできるようになります。ご自身の環境に合ったオプションを選択してください。OpenClaw は [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram)、およびその他のチャネルをサポートしています。全リストについては [docs.openclaw.ai](https://docs.openclaw.ai) を参照してください。

---

### オプション A: Discord

Discord を使用するには、bot を追加するための**管理者権限を持つ**サーバーが必要です。サーバーを共有しているが所有していない場合は、代わりにオプション B(Telegram)を使用してください。
#### Discordアカウントとサーバーの作成

Discordアカウントをお持ちでない場合は、[discord.com](https://discord.com)でサインアップしてください。また、管理者権限を持つサーバーが必要です。Discordのサイドバーにある**+**アイコンをクリックし、**Create My Own**を選択して作成してください。プライベートサーバーで問題ありません。

#### Discordアプリケーションとボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスし、**New Application**をクリックします。名前を付けてください（例:「openclaw-bot」）。
2. サイドバーの**Bot**をクリックします。ボットのユーザー名を設定します。
3. 引き続きBotページで、**Privileged Gateway Intents**までスクロールし、以下を有効にします:
   - **Message Content Intent**（必須）
   - **Server Members Intent**（推奨）
4. 上にスクロールして戻り、**Reset Token**をクリックしてボットトークンを生成します。コピーしてください。

#### ボットをサーバーに追加する

1. サイドバーの**OAuth2/ URL Generator**をクリックします。
2. **Scopes**の下で、`bot`と`applications.commands`を有効にします。
3. **Bot Permissions**の下で、以下を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成されたURLをコピーしてブラウザに貼り付け、サーバーを選択して確定します。ボットがサーバーのメンバーリストに表示されるはずです。

#### IDを収集する

Discordで開発者モードを有効にし（**User Settings/ Advanced/ Developer Mode**）、以下を行います:
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

#### サーバーメンバーからのDMを許可する

サーバーアイコンを右クリック/**Privacy Settings**/**Direct Messages**を有効にします。これにより、ボットがあなたにDMを送信できるようになり、ペアリング手順に必要です。

#### DiscordでOpenClawを設定する

ボットトークンを環境変数として保存し、Discordを有効化し、トークンを参照し、サーバーをアローリストに追加する単一のパッチファイルを作成します。上記で収集した`<server_id>`と`<user_id>`をIDに置き換えてください。

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

> **エージェントにこの設定を依頼することに頼らないでください。** サンドボックスが有効な場合、エージェントはサンドボックス内から`~/.openclaw/openclaw.json`に書き込むことができません。代わりにホスト上で上記のCLIコマンドを使用してください。

新しいチャンネル設定を反映させるため、ゲートウェイを再起動します:

```bash
openclaw gateway run --bind loopback --port 18789
```

数秒以内にゲートウェイの出力に`logged in to discord as <bot-name>`が表示されるはずです。

#### Discordアカウントをペアリングする

Discordでボットにダイレクトメッセージを送信します。ボットは短いペアリングコードで返信します。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClawを実行しているマシン上で承認します:
```bash
openclaw pairing approve discord <CODE>
```

> ペアリングコードは1時間で期限切れになります。

これで、Discordから直接エージェントとチャットし、タスクをローカルハードウェアにオフロードできるようになりました。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### オプションB: Telegram

TelegramはほとんどのユーザーにとってDiscordよりシンプルで、サーバーも管理者権限も不要です。

#### Telegramボットを作成する

1. Telegramを開き、**@BotFather**にメッセージを送ります。
2. `/newbot`を送信し、指示に従います。渡されたボットトークンを保存してください。

#### TelegramでOpenClawを設定する

トークンを環境変数として保存します:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

チャンネル設定を`~/.openclaw/openclaw.json`に追加します（またはダッシュボード経由でパッチを適用します）:

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

ゲートウェイを再起動し、Telegramでボットに何かメッセージを送信します。ペアリングを承認します:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

ペアリングコードは1時間で期限切れになります。これで、Telegramのダイレクトメッセージでエージェントとチャットできるようになりました。

---

## 次のステップ

これで、あなたのエージェントはスマートフォンからコマンドを受け取り、ローカルマシン上で動作できるようになりました。以下は、探求する価値のある3つの方向性です。

1. **株式市場サマライザー**: OpenClawをスケジュールして、一定間隔で金融APIからデータを取得し、その日の値動きをローカルモデルで要約し、毎朝選択したチャンネル経由でダイジェストをスマートフォンにプッシュします。

2. **ファインチューニングモニター**: TelegramまたはDiscord経由でトレーニングジョブをリモートで開始し、エージェントにトレーニングログを追跡させ、定期的に損失値、GPU使用率、ディスク使用量をスマートフォンに報告させます。実行が停止したりVRAMが急増したりした場合、マシンの前にいなくてもすぐに気付くことができます。

3. **ローカルVLMを使ったIOT**: 玄関にカメラを向け、Lemonadeでビジョンモデルを実行し、OpenClawにオンデマンドまたはトリガーでフレームを解析させます。「今日荷物は届きましたか？」とスマートフォンから尋ねれば、自分のハードウェアから直接答えが返ってきます。