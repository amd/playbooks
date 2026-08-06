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

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) は、Nous Research が開発した自己改善型 AI エージェントです。組み込みの学習ループを備えており、経験からスキルを構築し、セッションをまたいでユーザーに関する永続的なメモリを構築し、ユーザーに代わってスケジュールされた自動化を実行できます。単純なチャットアシスタントとは異なり、Hermes はシェルコマンドの実行、ファイルの書き込み、Web の閲覧、並列ワークストリームのサブエージェントへの委任など、実際のアクションを実行します。

[**Lemonade Server**](https://lemonade-server.ai/) は、それを支えるローカル推論バックエンドです。これは、AMD ハードウェア上で直接 GenAI モデルを実行し、業界標準の OpenAI API を通じてそれらを公開するオープンソースのサーバーです。

これらを組み合わせることで、完全にローカルな AI エージェントスタックが構成されます。Lemonade は GPU 上でのモデル推論を担当し、Hermes はエージェントループ、メモリ、スキル、メッセージングゲートウェイを提供します。

> **続行する前に:** Hermes Agent は高度に自律的な AI エージェントです。AI エージェントにシステムへのアクセスを許可すると、予測不可能または意図しない結果が生じる可能性があります。リスクを理解し、自律的なソフトウェアがユーザーに代わって動作することに問題がないと確信できる場合にのみ、続行してください。

---

## このプレイブックで学べること

このプレイブックを終える頃には、以下ができるようになります。

- **Hermes Agent をインストール**し、その AI バックエンドとして **Lemonade Server** を指定する。
- **(推奨) Docker/Podman サンドボックス化を有効化**し、エージェントのアクションをホストから分離する。
- **Hermes ゲートウェイを起動**し、エージェントが準備完了であることを確認する。
- **通信チャネル (Discord または Telegram) を接続**し、任意のデバイスからエージェントとチャットできるようにする。

---

## メモリ設定を行う

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

<!-- @os:linux -->
- **Ubuntu 24.04+** または `apt-get` を利用できる互換性のある Debian ベースの Linux ディストリビューションを実行している PC
- 少なくとも **12 GB の RAM** (より大きなモデルには 64 GB 以上を推奨)
- モデルの重み用に **約 10〜30 GB の空きディスク容量**
- [Podman](https://podman.io/docs/installation) (オプション、Hermes Agent のサンドボックス化用)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** を実行している PC
- 少なくとも **12 GB の RAM** (より大きなモデルには 64 GB 以上を推奨)
- モデルの重み用に **約 10〜30 GB の空きディスク容量**
- Podman (オプション、Hermes Agent のサンドボックス化用)。WSL 内にインストールします。
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman は Halo Box にプリインストールされているため、セットアップは不要です
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 推奨モデルをプルしてロードする

このプレイブックの推奨モデルは、Unsloth の **Qwen3.6-35B-A3B-GGUF** です。これは 263,000 トークンのコンテキストウィンドウを持つ強力な MoE モデルで、エージェントワークロードに適しています。このモデルは UD-Q4_K_XL 量子化を使用しています。今すぐプルしてください。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

次に、大きなコンテキストウィンドウでロードし、今後の実行のためにその設定を保存します。

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

このモデルのデフォルトのコンテキスト長は 262,144 トークンです。メモリ不足 (OOM) エラーが発生した場合は、コンテキストウィンドウを小さくすることを検討してください。

> **ヒント: エージェントの応答を高速化するために思考モードを無効にする:** Qwen3.6-35B-A3B はデフォルトで思考モードで動作するため、各応答の前にレイテンシが追加されます。エージェントループではこのオーバーヘッドがすぐに蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリには、思考モードを無効にする設定済みの構成が用意されています。使用するには、ファイルをダウンロードしてインポートしてください。
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

## WSL をセットアップする

Hermes Agent は WSL 内で実行し、Windows 上でネイティブに実行されている Lemonade に接続します。これにより、Windows 側で Lemonade の GPU アクセラレーションを維持しながら、Hermes 用の Linux シェル環境を利用できます。

### WSL と Ubuntu をインストールする

PowerShell を管理者として開き、WSL カーネルをインストールします。

```powershell
wsl --install --no-distribution
```

次に Ubuntu をインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL で systemd を有効にする

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

### Windows から WSL へ Lemonade をブリッジする

WSL2 は仮想ネットワーク内で実行されます。Windows 上の Lemonade は `127.0.0.1` にバインドされますが、WSL は直接これに到達できません。Windows のポートプロキシを使用して、WSL ゲートウェイ IP から Windows のローカルホストへトラフィックを転送します。

**WSL ゲートウェイ IP を確認します** (WSL 内で実行):

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加します** (PowerShell を管理者として実行し、`<WSL-Gateway-IP>` を実際の WSL ゲートウェイ IP に置き換えてください):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**ファイアウォールルールを追加します** (同じ管理者権限の PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL から確認します**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前のステップで Qwen3.6-35B-A3B-GGUF モデルを既にロードしている場合、ロード済みモデルを一覧表示する JSON 出力が表示されるはずです。

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

> `netsh portproxy` ルールは再起動後も保持されますが、`wsl --shutdown` の後に WSL ゲートウェイ IP が変わる場合があります。再起動後に WSL から Lemonade に到達できなくなった場合は、更新されたゲートウェイ IP を取得し、その新しい IP でプロキシを更新してください。

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

## Hermes Agent をインストールする

<!-- @os:windows -->
> 特に断りのない限り、このセクションのコマンドは **WSL ターミナル**内で実行してください。
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` フラグは対話型のセットアップウィザードをスキップするため、次のステップでモデルバックエンドを手動で設定できます。

シェルを再読み込みします。

```bash
source ~/.bashrc
```

インストールを確認します。

```bash
hermes --version
```

自己診断を実行してすべての依存関係を確認します。

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
## Hermes を Lemonade を使用するように設定する

Hermes はモデル設定を `~/.hermes/config.yaml` に保存します。対話形式の `hermes model` ピッカーを使用するか、設定を直接記述することができます。

### オプション1：対話形式のピッカー

<!-- @os:windows -->
> 次のコマンドは **WSL ターミナル** 内で実行してください。
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

以下のプロンプトが表示されたら:

1. **Custom endpoint (enter URL manually)** を選択します
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** WSL のゲートウェイ IP を使用します。WSL 内で `ip route show default | awk '{print $3}' | head -1` を実行して取得し、`http://<WSL-Gateway-IP>:13305/api/v1` と入力します
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1`（自動検出）
5. **Select model:** 一覧から `Qwen3.6-35B-A3B-GGUF` を選択します
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade`（またはお好みの名前）

`hermes model` は、アクティブなモデルの選択と、コンテキスト長をエンドポイントとともに保存する名前付きの `custom_providers` エントリの両方を保存します。`~/.hermes/config.yaml` の結果は次のようになります:

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

### オプション2：設定を直接記述する

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

WSL ターミナル内で、Windows ホストの IP を取得し、設定を記述します:

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

Hermes Agent は、すべてのエージェントのシェル操作やファイル操作を、ホスト上で直接実行するのではなく、分離されたコンテナ経由でルーティングできます。これにより、意図しない操作の影響範囲がサンドボックス内に限定され、ホストのファイルシステムやネットワークは影響を受けません。

軽量なサンドボックスイメージをビルドします:

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
WSL ターミナルに入ります:

```powershell
wsl -d Ubuntu-24.04
```

次に、軽量なサンドボックスイメージをビルドします:

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

次に、Hermes がコンテナランタイムとして Podman を使用するように設定し、ターミナルバックエンドを設定します:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` は引き続き `docker` のままです。
> `HERMES_DOCKER_BINARY` は、Hermes にランタイムとして Podman を使用するよう指示するものです。

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

これで Hermes は永続的なサンドボックスコンテナを起動し、すべての `terminal` およびファイルツールの呼び出しをそのコンテナ経由でルーティングするようになります。このコンテナは Hermes プロセスと生存期間を共有し、すべてのツール呼び出しで再利用され、Hermes が終了すると破棄されます。

> **サンドボックスが機能していることを確認する:** Hermes（`hermes`）を起動し、`run hostname` を実行するよう依頼してください。マシンのホスト名の代わりに、短いコンテナ ID が表示されるはずです。また、`rm -rf <path-to-a-dummy-file/folder>` を実行するよう依頼することもできます。Hermes は削除を確認しますが、フォルダはホスト上にそのまま残ります。このコマンドはコンテナの分離された `$HOME` 内で実行されたのであって、あなたの `$HOME` 内ではありません。

> **より強力な分離が必要ですか？** Hermes は、ゲートウェイ、ツールなどエージェントプロセス全体をコンテナ内で実行する公式の Docker イメージ（`nousresearch/hermes-agent`）も提供しています。設定の詳細については、[Hermes Docker ドキュメント](https://hermes-agent.nousresearch.com/docs/user-guide/docker) を参照してください。

---

<!-- @os:linux -->
## (推奨) Firecrawl サービスと Hermes の統合

Hermes は、組み込みの Web ツールを使用して Web サイトを閲覧し、コンテンツを抽出できます。しかし、多くの最新の Web サイトはボット検出システムを使用しており、単純な HTTP リクエストをブロックし、実際のコンテンツの代わりにチャレンジページを返します。その結果、Hermes はこれらのサイトから確実に情報を抽出できない場合があります。

この制限を克服するために、[Firecrawl](https://docs.firecrawl.dev/introduction) は、これらのチャレンジを回避し、Hermes の自動化の可能性を最大限に引き出すことができる、セルフホスト型の Web クローリングおよびコンテンツ抽出サービスを提供します。

このセットアップでは、Firecrawl は Podman で管理される一連の Docker コンテナとして実行されます。ライフサイクル管理と自動起動を簡素化するために、Firecrawl をユーザーレベルの `systemd` サービスとして登録し、基盤となる Podman Compose スタックをオーケストレーションします。これにより、Hermes はコンテナと直接やり取りする代わりに、標準の `systemctl --user` コマンドを使用して Firecrawl サービスを開始、停止、確認できるようになります。

わかりやすくするために、プロセス全体を4つのステップに分けています:

---

### 1. システムサービスを登録する
systemd のユーザー設定ディレクトリに移動します:
```bash
cd ~/.config/systemd/user
```
`firecrawl.service` という名前の新しいファイルを作成して開きます。
```bash
nano firecrawl.service
```
以下の設定をコピーして貼り付けます:
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
この時点で、サービスは定義されていますが、まだ `systemd` に登録されていません。
上記で作成したファイル名と完全に一致していることを確認してから、次を実行します:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功すると、以下の出力が表示されます:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` には、自動的に起動するように設定されたサービスへのシンボリックリンクが含まれています。

### 2. サービス用に Firecrawl を設定する

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) は、スクレイピングとデータ処理環境を完全に制御する必要があるユーザーに最適ですが、その代わりに追加のメンテナンスと設定の手間が発生します。

まず、リポジトリをクローンします:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
ルートの `/firecrawl` ディレクトリに `.env` を作成します:
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
> 信頼できないネットワークからアクセス可能なデプロイメントの場合は特に、`BULL_AUTH_KEY` には強力なシークレットを設定してください。
### 3. Hermesの Composeによるデプロイ

先に進む前に、最新のHermes Dockerイメージをプルしていることを確認してください。
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
完了したら、Hermes Composeファイル[hermes-compose.yaml](assets/hermes-compose.yaml)をダウンロードし、`/firecrawl`のルートディレクトリに配置してください。

> `WorkingDirectory=${HOME}/firecrawl`で指定されている通り、`systemd`がサービスを正しく検出して起動するためには、この規則に従う必要があります。

> 必要に応じて、追加のFirecrawlサービスを組み込むことでスタックを拡張できます。利用可能なサービスの全一覧は、公式の[Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)で確認できます。

### 4. Firecrawl経由でHermesサービスを起動する

`systemd`に制御を委ねる前に、スタックを手動で実行してすべてが正しく動作することを確認してください。
```bash
podman compose -f hermes-compose.yaml up -d
```
すべてが正しく設定されていれば、Hermesコンテナが立ち上がるのが確認でき、コマンドラインの出力は以下のようになるはずです。
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

確認が済んだら、次に進む前にスタックを停止してください。
```bash
podman compose -f hermes-compose.yaml down
```
検証がすべて完了したので、`systemd`経由でサービスを起動します。
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints)はインタラクティブコンテナ内からアクセス可能で、Webダッシュボードも同じホスト上のhttp://127.0.0.1:9119で利用できます。
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

サービスを停止するには、以下を実行してください。
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

インタラクティブなCLIセッションを直接起動します。

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

**おめでとうございます。完全にローカルで動作するAIエージェントスタックを構築できました。**

### Webダッシュボード

Hermesには、設定、APIキー、モデル、セッション、メモリ、cronジョブを管理するためのブラウザベースのUIが含まれています。ゲートウェイまたはCLIが実行されている状態で、2つ目のターミナルを開き、以下のコマンドで起動してください。

```bash
hermes dashboard
```

これによりローカルサーバーが起動し、ブラウザで`http://127.0.0.1:9119`が開きます。全機能のリファレンスについては、[ダッシュボードのドキュメント](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)を参照してください。
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## オプション:通信チャネルの接続

ゲートウェイが動作していれば、どのデバイスからでもローカルエージェントにアクセスできます。Hermesは[Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)、[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)などをサポートしています。

---

### Discord

Discordでは、ボットを追加するために**管理者権限を持つ**サーバーが必要です。サーバーを共有していても所有していない場合は、代わりにTelegramを使用してください。

#### Discordアプリケーションとボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスし、**New Application**をクリックします。名前を付けます(例: "hermes-bot")。
2. サイドバーで**Bot**をクリックします。ボットのユーザー名を設定します。
3. Botページのまま、**Privileged Gateway Intents**までスクロールし、以下を有効にします。
   - **Message Content Intent**(必須)
   - **Server Members Intent**(推奨)
4. 上にスクロールして戻り、**Reset Token**をクリックしてボットトークンを生成します。コピーしてください。

#### ボットをサーバーに追加する

1. サイドバーで**OAuth2 / URL Generator**をクリックします。
2. **Scopes**の下で`bot`と`applications.commands`を有効にします。
3. **Bot Permissions**の下で、View Channels、Send Messages、Read Message History、Embed Links、Attach Filesを有効にします。
4. 生成されたURLをコピーしてブラウザに貼り付け、サーバーを選択して確定します。

#### IDの取得とDMの許可

Discordで開発者モードを有効にし(**User Settings / Advanced / Developer Mode**)、以下を行います。
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

サーバーアイコンを右クリック / **Privacy Settings** / **Direct Messages**を有効にします。これはペアリングの手順に必要です。

#### DiscordのためのHermesの設定

`~/.hermes/.env`に以下を追加してください。

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

次に、ゲートウェイを起動します。

```bash
hermes gateway
```

数秒以内にボットがDiscord上でオンラインになるはずです。DMまたはボットが見えるチャンネルでメッセージを送信してください。

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Telegramボットの作成

1. Telegramを開き、**@BotFather**にメッセージを送ります。
2. `/newbot`を送信し、指示に従います。表示されるボットトークンを保存してください。

#### TelegramのためのHermesの設定

`~/.hermes/.env`に以下を追加してください。

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Telegramのユーザー IDが分かりませんか?** Telegramで[@userinfobot](https://t.me/userinfobot)にメッセージを送ると、数値IDが返信されます。

次に、ゲートウェイを起動します。

```bash
hermes gateway
```

テストのため、Telegramでボットに何かメッセージを送ってください。これでTelegramのDMを通じてエージェントとチャットできるようになりました。Webhookモードや高度なオプションについては、[Telegramの完全なセットアップガイド](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)を参照してください。

---

## 次のステップ

これでエージェントがスマートフォンからコマンドを受け取り、ローカルマシン上で動作できるようになったので、以下の3つの方向性を検討する価値があります。

1. **自動化されたリサーチダイジェスト**: 毎朝、気になるトピックについてHermesにWeb検索をスケジュールさせ、ローカルモデルで結果を要約し、Telegramまたは Discord経由でダイジェストをスマートフォンにプッシュします。すべて自分のハードウェア上で動作し、クラウドコストは一切かかりません。

2. **オンデマンドのコードレビュー**: HermesにGitHubリポジトリを指定し、オープンなプルリクエストをレビューさせて、コメントや要約をチャットに投稿させます。Dockerターミナルバックエンドを使用することで、すべてのgit操作はサンドボックス内で実行されるため、ホスト環境をクリーンに保てます。

3. **ローカルファイルアシスタント**: Hermesに作業ディレクトリへのアクセス権を与え、スマートフォンからオンデマンドでファイルの整理、リネーム、要約、変換を指示できます。Dockerターミナルバックエンドがすべての書き込みをサンドボックスのワークスペース内に限定するため、誤った破壊的操作による被害を防げます。