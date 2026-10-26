<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# Lemonade Server を使用してローカルで Hermes Agent を実行する

## 概要

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) は、Nous Research によって構築された自己改善型の AI エージェントです。内蔵の学習ループを備えており、経験からスキルを生み出し、セッションをまたいであなたに関する永続的な記憶を構築し、あなたに代わってスケジュールされた自動化処理を実行できます。単純なチャットアシスタントとは異なり、Hermes はシェルコマンドの実行、ファイルの書き込み、ウェブの閲覧、並列ワークストリームのサブエージェントへの委任といった、実際のアクションを実行します。

[**Lemonade Server**](https://lemonade-server.ai/) は、それを支えるローカル推論バックエンドです。これはオープンソースのサーバーであり、お使いの AMD ハードウェア上で直接 GenAI モデルを実行し、業界標準の OpenAI API を通じてそれらを公開します。

両者を組み合わせることで、完全にローカルな AI エージェントスタックが構成されます。Lemonade が GPU 上でのモデル推論を担当し、Hermes がエージェントループ、記憶、スキル、メッセージングゲートウェイを提供します。

> **続ける前に:** Hermes Agent は高度に自律的な AI エージェントです。いかなる AI エージェントにシステムへのアクセスを許可することも、予測不能または意図しない結果を招く可能性があります。リスクを理解し、自律的なソフトウェアがあなたに代わって動作することに納得できる場合にのみ進めてください。

---

## このプレイブックで学べること

このプレイブックを終える頃には、以下のことができるようになります。

- **Hermes Agent をインストール**し、AI バックエンドとして **Lemonade Server** を指定する。
- **(推奨) Docker/Podman によるサンドボックス化を有効化**し、エージェントの動作をホストから隔離する。
- **Hermes ゲートウェイを起動**し、エージェントの準備が整ったことを確認する。
- **通信チャネル(Discord または Telegram)を接続**し、あらゆるデバイスからエージェントとチャットできるようにする。

---

<!-- @device:halo_box,halo,stx,krk -->
## メモリ設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

<!-- @os:linux -->
- **Ubuntu 24.04+** または `apt-get` を使用できる互換性のある Debian ベースの Linux ディストリビューションを実行している PC
- 少なくとも **12 GB の RAM**(より大きなモデルには 64 GB 以上を推奨)
- モデルの重みのために**約 10〜30 GB の空きディスク容量**
- [Podman](https://podman.io/docs/installation)(任意、Hermes Agent のサンドボックス化のため)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** を実行している PC
- 少なくとも **12 GB の RAM**(より大きなモデルには 64 GB 以上を推奨)
- モデルの重みのために**約 10〜30 GB の空きディスク容量**
- Podman(任意、Hermes Agent のサンドボックス化のため)。WSL 内にインストールしてください。
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman は Halo Box にプリインストールされており、セットアップは不要です
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-6-35b-a3b,podman,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 推奨モデルをプルしてロードする

このプレイブックで推奨するモデルは、Unsloth 提供の **Qwen3.6-35B-A3B-GGUF** です。これは 263k トークンのコンテキストウィンドウを持つ強力な MoE モデルであり、エージェントのワークロードに適しています。このモデルは UD-Q4_K_XL 量子化を使用しています。今すぐプルしましょう。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

次に、大きなコンテキストウィンドウでロードし、その設定を今後の実行のために保存します。

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

このモデルのデフォルトのコンテキスト長は 262,144 トークンです。メモリ不足(OOM)エラーが発生する場合は、コンテキストウィンドウを縮小することを検討してください。

> **ヒント: より高速なエージェント応答のために思考を無効化する:** Qwen3.6-35B-A3B はデフォルトで思考モードで動作し、各応答の前に遅延が追加されます。エージェントループではこのオーバーヘッドが急速に蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリには、思考を無効化する用意済みの設定が用意されています。使用するには、ファイルをダウンロードしてインポートします。
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Hermes Agent は WSL 内で実行し、Windows 上でネイティブに動作している Lemonade に接続します。これにより、Lemonade の GPU アクセラレーションを Windows 側に保持しつつ、Hermes 用の Linux シェル環境を利用できます。

### WSL と Ubuntu のインストール

管理者として PowerShell を開き、WSL カーネルをインストールします。

```powershell
wsl --install --no-distribution
```

次に Ubuntu をインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL での systemd の有効化

Ubuntu ターミナル内で以下を実行します。

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

### Windows から WSL への Lemonade のブリッジ

WSL2 は仮想ネットワーク内で動作します。Windows 上の Lemonade は `127.0.0.1` にバインドされており、WSL から直接到達することはできません。Windows のポートプロキシを使用して、WSL ゲートウェイ IP から Windows のローカルホストへトラフィックを転送します。

**WSL ゲートウェイ IP を確認する**(WSL 内で実行):

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加する**(管理者として PowerShell で実行し、`<WSL-Gateway-IP>` をあなたの WSL ゲートウェイ IP に置き換えてください):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**ファイアウォールルールを追加する**(同じ昇格された PowerShell で実行):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL から確認する**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前の手順ですでに Qwen3.6-35B-A3B-GGUF モデルをロードしている場合、ロード済みモデルを一覧表示する JSON 出力が表示されるはずです。

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

> `netsh portproxy` ルールは再起動後も保持されますが、`wsl --shutdown` の後に WSL ゲートウェイ IP が変わることがあります。再起動後に WSL から Lemonade に到達できなくなった場合は、更新されたゲートウェイ IP を取得し、この新しい IP でプロキシを更新してください。

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Hermes Agent のインストール

<!-- @os:windows -->
> 特に断りのない限り、このセクションのコマンドは**WSL ターミナル**内で実行してください。
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` フラグは対話形式のセットアップウィザードをスキップするため、次のステップでモデルバックエンドを手動で設定できます。

シェルを再読み込みします。

```bash
source ~/.bashrc
```

インストールを確認します。

```bash
hermes --version
```

すべての依存関係を確認するための自己診断を実行します。

```bash
hermes doctor
```

> **ヒント:** インストール後に `command not found` と表示される場合は、Hermes を PATH に追加してください。
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> これを永続化するには、上記の行を `~/.bashrc` または `~/.zshrc` に追加してください。

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Hermes を Lemonade 用に設定する

Hermes はモデル設定を `~/.hermes/config.yaml` に保存します。対話形式の `hermes model` ピッカーを使用するか、設定を直接書き込むことができます。

### オプション1: 対話形式のピッカー

<!-- @os:windows -->
> 以下を **WSL ターミナル** 内で実行してください。
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

プロンプトが表示されたら:

1. **Custom endpoint (enter URL manually)** を選択
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** WSL ゲートウェイ IP を使用します。WSL 内で `ip route show default | awk '{print $3}' | head -1` を実行して取得し、`http://<WSL-Gateway-IP>:13305/api/v1` と入力してください
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** 一覧から `Qwen3.6-35B-A3B-GGUF` を選択
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade`(または任意の名前)

`hermes model` は、アクティブなモデル選択と、エンドポイントとともにコンテキスト長を保存する名前付きの `custom_providers` エントリの両方を保存します。結果として `~/.hermes/config.yaml` は以下のようになります。

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### オプション2: 設定を直接書き込む

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

WSL ターミナル内で、Windows ホストの IP を取得し、設定を書き込みます。

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (推奨) Podman サンドボックスを有効にする

Hermes Agent は、すべてのエージェントのシェル操作やファイル操作を、ホスト上で直接実行するのではなく、分離されたコンテナ経由でルーティングできます。これにより、意図しない操作による影響範囲をサンドボックス内に限定し、ホストのファイルシステムとネットワークには影響を与えません。

軽量なサンドボックスイメージをビルドします。

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
WSL ターミナルに入ります。

```powershell
wsl -d Ubuntu-24.04
```

次に、軽量なサンドボックスイメージをビルドします。

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

次に、Hermes がコンテナランタイムとして Podman を使用するように設定し、ターミナルバックエンドを設定します。

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` は引き続き `docker` のままです。
> `HERMES_DOCKER_BINARY` が、Hermes にランタイムとして Podman を使用するよう指示します。

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

これで Hermes は永続的なサンドボックスコンテナを起動し、すべての `terminal` およびファイルツールの呼び出しをそのコンテナ経由でルーティングするようになります。このコンテナは Hermes プロセスのライフサイクルを共有し、すべてのツール呼び出しで再利用され、Hermes 終了時に破棄されます。

> **サンドボックスが機能しているか確認する:** Hermes を起動し(`hermes`)、`run hostname` を実行させてください。マシンのホスト名ではなく、短いコンテナ ID が表示されるはずです。また、`rm -rf <path-to-a-dummy-file/folder>` を実行させることもできます。Hermes は削除を確認しますが、フォルダはホスト上にそのまま残っています。コマンドはあなたの `$HOME` ではなく、コンテナの分離された `$HOME` 内で実行されたためです。

> **より強力な分離が必要ですか?** Hermes は、ゲートウェイやツールなど、エージェントプロセス全体をコンテナ内で実行する公式の Docker イメージ(`nousresearch/hermes-agent`)も提供しています。セットアップの詳細については、[Hermes Docker ドキュメント](https://hermes-agent.nousresearch.com/docs/user-guide/docker)を参照してください。

---

<!-- @os:linux -->
## (推奨) Firecrawl サービスとの Hermes 統合

Hermes は、組み込みの Web ツールを使用して Web サイトを閲覧し、コンテンツを抽出できます。しかし、多くの最新の Web サイトはボット検知システムを使用しており、単純な HTTP リクエストをブロックして、実際のコンテンツの代わりにチャレンジページを返します。その結果、Hermes はこれらのサイトから情報を確実に抽出できない場合があります。

この制限を克服するために、[Firecrawl](https://docs.firecrawl.dev/introduction) はこれらのチャレンジを回避し、Hermes オートメーションの可能性を最大限に引き出すことができる、セルフホスト型の Web クローリングおよびコンテンツ抽出サービスを提供しています。

このセットアップでは、Firecrawl は Podman で管理される一連の Docker コンテナとして実行されます。ライフサイクル管理と自動起動を簡素化するために、Firecrawl をユーザーレベルの `systemd` サービスとして登録し、基盤となる Podman Compose スタックをオーケストレーションします。これにより、Hermes はコンテナと直接やり取りする代わりに、標準の `systemctl --user` コマンドを使用して Firecrawl サービスの起動、停止、確認を行えるようになります。

シンプルにするため、全体のプロセスを4つのステップに分けました。

---

### 1. システムサービスを登録する
systemd のユーザー設定ディレクトリに移動します。
```bash
cd ~/.config/systemd/user
```
`firecrawl.service` という名前の新しいファイルを作成して開きます。
```bash
nano firecrawl.service
```
以下の設定をコピーして貼り付けます。
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
この時点で、サービスは定義されていますが、まだ `systemd` には登録されていません。
上記で作成したファイル名と完全に一致していることを確認してから、以下を実行します。
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功した場合、以下のような出力が表示されます。

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` には、自動的に起動するように設定されたサービスへのシンボリックリンクが含まれています。

### 2. サービス用に Firecrawl を設定する

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) は、スクレイピングとデータ処理環境を完全に制御する必要があるユーザーに最適ですが、その代わりに追加のメンテナンスと設定作業が必要になります。

まず、リポジトリをクローンします。
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
ルートの `/firecrawl` ディレクトリに `.env` を作成します。
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> 特に信頼できないネットワークからアクセス可能なデプロイメントの場合は、`BULL_AUTH_KEY` に強力な秘密鍵を設定してください。
### 3. Composeによるの Hermes デプロイ

続行する前に、最新の Hermes Docker イメージをプルしていることを確認してください:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
これが完了したら、Hermes Compose ファイル [hermes-compose.yaml](assets/hermes-compose.yaml) をダウンロードし、ルートの `/firecrawl` ディレクトリに配置します:

> この規約は、`WorkingDirectory=${HOME}/firecrawl` で指定されているとおりに `systemd` がサービスを正しく見つけて起動するために必要です。

> 必要に応じて、Firecrawl サービスを追加してスタックをいつでも拡張できます。利用可能なサービスの完全な一覧は、公式の [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) に記載されています。

### 4. Firecrawl 経由で Hermes サービスを起動する

制御を `systemd` に渡す前に、スタックを手動で実行してすべてが正しく動作することを確認します:
```bash
podman compose -f hermes-compose.yaml up -d
```
すべてが正しく設定されていれば、Hermes コンテナが起動し、コマンドラインの出力は次のようになります:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

確認が完了したら、続行する前にスタックを停止します:
```bash
podman compose -f hermes-compose.yaml down
```
すべての検証が完了したので、`systemd` 経由でサービスを開始します:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) は対話型コンテナ内からアクセスでき、Web ダッシュボードは同じホストとポート(http://127.0.0.1:9119)で利用できます。
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

サービスを停止するには、次を実行します:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

インタラクティブな CLI セッションを直接開始します: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**おめでとうございます。完全にローカルで動作する AI エージェントスタックを構築できました。**

### Web ダッシュボード

Hermes には、設定、API キー、モデル、セッション、メモリ、cron ジョブを管理するためのブラウザベースの UI が含まれています。ゲートウェイまたは CLI が実行されている状態で、2つ目のターミナルを開き、次のコマンドで起動します:

```bash
hermes dashboard
```

これによりローカルサーバーが起動し、ブラウザで `http://127.0.0.1:9119` が開きます。機能の全リファレンスについては、[ダッシュボードのドキュメント](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)を参照してください。
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャネルの接続

ゲートウェイが起動すると、任意のデバイスからローカルエージェントにアクセスできるようになります。Hermes は [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)、[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)などに対応しています。

---

### Discord

Discord では、ボットを追加するために**管理者アクセス権を持っている**サーバーが必要です。サーバーを共有していても所有していない場合は、代わりに Telegram を使用してください。

#### Discord アプリケーションとボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、**New Application** をクリックします。名前を付けます(例: 「hermes-bot」)。
2. サイドバーで **Bot** をクリックします。ボットのユーザー名を設定します。
3. 同じ Bot ページで **Privileged Gateway Intents** までスクロールし、次を有効にします:
   - **Message Content Intent**(必須)
   - **Server Members Intent**(推奨)
4. 上にスクロールして戻り、**Reset Token** をクリックしてボットトークンを生成します。これをコピーします。

#### サーバーへのボットの追加

1. サイドバーで **OAuth2 / URL Generator** をクリックします。
2. **Scopes** の下で `bot` と `applications.commands` を有効にします。
3. **Bot Permissions** の下で、以下を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成された URL をコピーし、ブラウザに貼り付け、サーバーを選択して確定します。

#### ID の収集と DM の許可

Discord でデベロッパーモードを有効にし(**User Settings / Advanced / Developer Mode**)、以下を行います:
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

サーバーアイコンを右クリック / **Privacy Settings** / **Direct Messages** を有効にします。これはペアリング手順に必要です。

#### Discord 向けの Hermes の設定

次を `~/.hermes/.env` に追加します:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

次に、ゲートウェイを起動します:

```bash
hermes gateway
```

数秒以内に、ボットが Discord 上でオンラインになるはずです。DM またはボットが見えるチャンネルでメッセージを送信してください。

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Telegram ボットの作成

1. Telegram を開き、**@BotFather** にメッセージを送ります。
2. `/newbot` を送信し、画面の指示に従います。渡されたボットトークンを保存します。

#### Telegram 向けの Hermes の設定

次を `~/.hermes/.env` に追加します:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Telegram のユーザー ID がわからない場合は?** Telegram で [@userinfobot](https://t.me/userinfobot) にメッセージを送ると、数値の ID を返信してくれます。

次に、ゲートウェイを起動します:

```bash
hermes gateway
```

テストとして、Telegram でボットに任意のメッセージを送ってください。これで Telegram の DM からエージェントとチャットできるようになります。Webhook モードや高度なオプションについては、[Telegram の完全なセットアップガイド](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)を参照してください。

---

## 次のステップ

これでエージェントがスマートフォンからコマンドを受け取り、ローカルマシン上で動作できるようになったので、ぜひ試していただきたい3つの方向性を紹介します:

1. **自動リサーチダイジェスト**: 毎朝、関心のあるトピックについて Hermes に Web 検索をスケジュールさせ、ローカルモデルで調査結果を要約し、Telegram または Discord 経由でスマートフォンにダイジェストをプッシュします。すべて自分のハードウェア上で、クラウドコストなしで実行されます。

2. **オンデマンドのコードレビュー**: Hermes に GitHub リポジトリを指定し、オープンな pull request のレビューを依頼し、コメントや要約をチャットに投稿させます。Docker ターミナルバックエンドにより、すべての git 操作はサンドボックス内で実行されるため、ホスト環境はクリーンに保たれます。

3. **ローカルファイルアシスタント**: Hermes に作業ディレクトリへのアクセス権を与え、スマートフォンからオンデマンドでファイルの整理、名前変更、要約、変換を依頼します。Docker ターミナルバックエンドがすべての書き込みをサンドボックスのワークスペース内に限定するため、誤った破壊的操作が発生しても被害が抑えられます。