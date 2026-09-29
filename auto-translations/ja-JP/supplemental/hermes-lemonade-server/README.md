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

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) は、Nous Research によって構築された自己改善型 AI エージェントです。組み込みの学習ループを持ち、経験からスキルを構築し、セッションをまたいであなたに関する永続的な記憶を構築し、あなたに代わってスケジュールされた自動化を実行できます。単純なチャットアシスタントとは異なり、Hermes はシェルコマンドの実行、ファイルの書き込み、Web の閲覧、並列作業の subagent への委任といった実際のアクションを行います。

[**Lemonade Server**](https://lemonade-server.ai/) は、それを支えるローカル推論バックエンドです。これは、GenAI モデルをお使いの AMD ハードウェア上で直接実行し、業界標準の OpenAI API を通じてそれらを公開するオープンソースサーバーです。

これらを組み合わせることで、完全にローカルな AI エージェントスタックが形成されます。Lemonade は GPU 上でのモデル推論を処理し、Hermes はエージェントループ、メモリ、スキル、メッセージングゲートウェイを提供します。

> **続ける前に:** Hermes Agent は高度な自律性を持つ AI エージェントです。AI エージェントにシステムへのアクセスを許可すると、予測できない、または意図しない結果を招く可能性があります。リスクを理解し、あなたに代わって自律的に動作するソフトウェアに納得できる場合にのみ、先へ進んでください。

---

## このプレイブックで学べること

このプレイブックを終える頃には、次のことができるようになります。

- **Hermes Agent をインストール**し、**Lemonade Server** をその AI バックエンドとして指定する。
- **（推奨）Docker/Podman サンドボックスを有効化**し、エージェントのアクションをホストから隔離する。
- **Hermes ゲートウェイを起動**し、エージェントが準備できたことを確認する。
- **通信チャネル（Discord または Telegram）を接続**し、どのデバイスからでもエージェントとチャットできるようにする。

---

<!-- @device:halo_box,halo,stx,krk -->
## メモリ設定を行う

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートを確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

<!-- @os:linux -->
- **Ubuntu 24.04+**、または `apt-get` を利用できる互換性のある Debian ベースの Linux ディストリビューションを実行している PC
- 少なくとも **12 GB の RAM**（より大きなモデルには 64 GB 以上を推奨）
- モデルの重みのために **約 10～30 GB の空きディスク容量**
- [Podman](https://podman.io/docs/installation)（Hermes Agent をサンドボックス化する場合、任意）
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** を実行している PC
- 少なくとも **12 GB の RAM**（より大きなモデルには 64 GB 以上を推奨）
- モデルの重みのために **約 10～30 GB の空きディスク容量**
- Podman（Hermes Agent をサンドボックス化する場合、任意）。WSL 内にインストールしてください。
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

## 推奨モデルを取得してロードする

このプレイブックで推奨するモデルは、Unsloth 提供の **Qwen3.6-35B-A3B-GGUF** です。これは 263k トークンのコンテキストウィンドウを持つ強力な MoE モデルで、エージェントのワークロードに適しています。このモデルは UD-Q4_K_XL 量子化を使用しています。今すぐ取得してください。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

続けて、大きなコンテキストウィンドウでロードし、その設定を今後の実行のために保存します。

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

このモデルのデフォルトのコンテキスト長は 262,144 トークンです。メモリ不足（OOM）エラーが発生する場合は、コンテキストウィンドウを縮小することを検討してください。

> **ヒント: より高速なエージェント応答のために思考モードを無効化する:** Qwen3.6-35B-A3B はデフォルトで思考モードで動作し、各応答の前にレイテンシが追加されます。エージェントループではこのオーバーヘッドがすぐに蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリには、思考を無効化する設定済みの構成がすぐに使える形で用意されています。使用するには、ファイルをダウンロードしてインポートしてください。
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

Hermes Agent は WSL 内で実行し、Windows 上でネイティブに実行されている Lemonade に接続します。これにより、Windows 側で Lemonade の GPU アクセラレーションを維持しつつ、Hermes 用の Linux シェル環境を得ることができます。

### WSL と Ubuntu をインストールする

PowerShell を管理者として開き、WSL カーネルをインストールします。

```powershell
wsl --install --no-distribution
```

続けて Ubuntu をインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL で systemd を有効化する

Ubuntu ターミナル内で次を実行します。

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

WSL2 は仮想ネットワーク内で動作します。Windows 上の Lemonade は `127.0.0.1` にバインドされるため、WSL から直接アクセスすることはできません。Windows のポートプロキシは、WSL のゲートウェイ IP からのトラフィックを Windows のローカルホストへ転送します。

**WSL のゲートウェイ IP を確認します**（WSL 内で実行）。

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加します**（PowerShell を管理者として実行し、`<WSL-Gateway-IP>` をご使用の WSL ゲートウェイ IP に置き換えてください）。

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**ファイアウォールルールを追加します**（同じ管理者権限の PowerShell で実行）。

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL から確認します**。

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前の手順で Qwen3.6-35B-A3B-GGUF モデルを既にロードしている場合、ロード済みモデルを一覧表示する JSON 出力が表示されるはずです。

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

> `netsh portproxy` ルールは再起動後も維持されますが、WSL のゲートウェイ IP は `wsl --shutdown` の後に変わることがあります。再起動後に WSL から Lemonade に到達できなくなった場合は、更新されたゲートウェイ IP を取得し、この新しい IP でプロキシを更新してください。

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
> このセクションのコマンドは、特に断りのない限り **WSL ターミナル**内で実行してください。
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` フラグは対話型セットアップウィザードをスキップするため、次のステップでモデルバックエンドを手動で設定できます。

シェルを再読み込みします。

```bash
source ~/.bashrc
```

インストールを確認します。

```bash
hermes --version
```

自己診断を実行して、すべての依存関係を確認します。

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
## HermesがLemonadeを使用するように設定する

Hermesはモデル設定を`~/.hermes/config.yaml`に保存します。インタラクティブな`hermes model`ピッカーを使用するか、直接設定ファイルを記述することができます。

### オプション1：インタラクティブピッカー

<!-- @os:windows -->
> 以下のコマンドは**WSLターミナル**内で実行してください。
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

プロンプトが表示されたら：

1. **Custom endpoint (enter URL manually)**を選択
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** WSLゲートウェイIPを使用します。WSL内で`ip route show default | awk '{print $3}' | head -1`を実行して取得し、`http://<WSL-Gateway-IP>:13305/api/v1`を入力してください
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1`（自動検出）
5. **Select model:** リストから`Qwen3.6-35B-A3B-GGUF`を選択
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade`（またはお好みの名前）

`hermes model`は、アクティブなモデルの選択と、エンドポイントとともにコンテキスト長を保存する名前付きの`custom_providers`エントリの両方を保存します。`~/.hermes/config.yaml`内の結果は次のようになります：

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

### オプション2：直接設定を記述する

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

WSLターミナル内で、Windowsホストのipを取得し、設定を記述します：

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

## （推奨）Podmanサンドボックスを有効にする

Hermes Agentは、すべてのエージェントのシェル操作とファイル操作を、ホスト上で直接実行するのではなく、分離されたコンテナ経由でルーティングできます。これにより、意図しない操作の影響範囲がサンドボックスに限定され、ホストのファイルシステムとネットワークは影響を受けません。

軽量なサンドボックスイメージをビルドします：

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
WSLターミナルに入ります：

```powershell
wsl -d Ubuntu-24.04
```

次に、軽量なサンドボックスイメージをビルドします：

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

次に、Podmanをコンテナランタイムとして使用するようにHermesを設定し、ターミナルバックエンドを設定します：

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend`は引き続き`docker`のままです。
> `HERMES_DOCKER_BINARY`は、Hermesにランタイムとして代わりにPodmanを使用するよう指示するものです。

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

これにより、Hermesは永続的なサンドボックスコンテナを起動し、すべての`terminal`ツールおよびファイルツールの呼び出しをそのコンテナ経由でルーティングします。このコンテナはHermesプロセスと生存期間を共有し、すべてのツール呼び出しで再利用され、Hermesが終了すると破棄されます。

> **サンドボックスが機能していることを確認する：** Hermes（`hermes`）を起動し、`run hostname`を実行するよう依頼してください。マシンのホスト名ではなく、短いコンテナIDが表示されるはずです。また、`rm -rf <path-to-a-dummy-file/folder>`を実行するよう依頼することもできます。Hermesは削除を確認しますが、フォルダはホスト上にそのまま残っています。このコマンドはコンテナの分離された`$HOME`内で実行されたのであり、あなたの`$HOME`ではありません。

> **より強力な分離が必要ですか？** Hermesは、ゲートウェイ、ツールなど、エージェントプロセス全体をコンテナ内で実行する公式のDockerイメージ（`nousresearch/hermes-agent`）も提供しています。セットアップの詳細については、[Hermes Dockerドキュメント](https://hermes-agent.nousresearch.com/docs/user-guide/docker)を参照してください。

---

<!-- @os:linux -->
## （推奨）HermesとFirecrawlサービスの統合

Hermesは、組み込みのWebツールを使用してウェブサイトを閲覧し、コンテンツを抽出できます。しかし、多くの最新のウェブサイトはボット検出システムを使用しており、単純なHTTPリクエストをブロックして、実際のコンテンツの代わりにチャレンジページを返します。その結果、Hermesはこれらのサイトから確実に情報を抽出できない場合があります。

この制限を克服するため、[Firecrawl](https://docs.firecrawl.dev/introduction)は、これらのチャレンジを回避し、Hermes自動化の可能性を最大限に引き出すことができる、セルフホスト型のウェブクローリングおよびコンテンツ抽出サービスを提供します。

このセットアップでは、Firecrawlは、Podmanで管理される一連のDockerコンテナとして実行されます。ライフサイクル管理と自動起動を簡素化するため、基盤となるPodman Composeスタックをオーケストレーションするユーザーレベルの`systemd`サービスとしてFirecrawlを登録します。これにより、Hermesは、コンテナと直接やり取りする代わりに、標準の`systemctl --user`コマンドを使用してFirecrawlサービスを開始、停止、確認できるようになります。

わかりやすくするため、全体のプロセスを4つのステップに分けています：

---

### 1. システムサービスを登録する
systemdユーザー設定ディレクトリに移動します：
```bash
cd ~/.config/systemd/user
```
`firecrawl.service`という新しいファイルを作成して開きます。
```bash
nano firecrawl.service
```
以下の設定をコピーして貼り付けます：
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
この時点では、サービスは定義されていますが、まだ`systemd`には登録されていません。
上記で作成したファイル名と完全に一致していることを確認してから、以下を実行します：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功すると、次のような出力が表示されるはずです：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/`には、自動起動するよう設定されたサービスへのシンボリックリンクが含まれています。

### 2. サービス用にFirecrawlを設定する

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)は、スクレイピングおよびデータ処理環境を完全に制御する必要があるユーザーに最適ですが、その代償として、追加のメンテナンスと設定作業が必要になります。

まず、リポジトリをクローンします：
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
ルートの`/firecrawl`ディレクトリに`.env`を作成します：
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
> 特に信頼されていないネットワークからアクセス可能なデプロイメントでは、`BULL_AUTH_KEY`を強力なシークレットに設定してください。
### 3. Compose 経由での Hermes のデプロイ

先に進む前に、最新の Hermes Docker イメージをプルしていることを確認してください:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
完了したら、Hermes の Compose ファイル [hermes-compose.yaml](assets/hermes-compose.yaml) をダウンロードし、`/firecrawl` ディレクトリの直下に配置してください:

> この規則は、`WorkingDirectory=${HOME}/firecrawl` で指定されているとおりに `systemd` がサービスを正しく見つけて起動するために必要です。

> 必要に応じて、Firecrawl のサービスを追加することでスタックを拡張できます。利用可能なサービスの全一覧は、公式の [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) で確認できます。

### 4. Firecrawl 経由で Hermes サービスを起動する

制御を `systemd` に渡す前に、スタックを手動で実行してすべてが正しく動作することを確認してください:
```bash
podman compose -f hermes-compose.yaml up -d
```
正しく設定されていれば、Hermes コンテナが立ち上がるのが確認でき、コマンドラインの出力は次のような内容になるはずです:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

確認が済んだら、先に進む前にスタックを停止してください:
```bash
podman compose -f hermes-compose.yaml down
```
すべての確認が済んだら、`systemd` 経由でサービスを起動します:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) はインタラクティブコンテナ内からアクセスでき、Web ダッシュボードは同じホストとポートの http://127.0.0.1:9119 で利用できます。
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

**おめでとうございます。完全にローカルで動作する AI エージェントスタックが構築できました。**

### Web ダッシュボード

Hermes には、設定、API キー、モデル、セッション、メモリ、cron ジョブを管理するためのブラウザベースの UI が含まれています。ゲートウェイまたは CLI を実行したまま、2 つ目のターミナルを開いて次のコマンドで起動します:

```bash
hermes dashboard
```

これによりローカルサーバーが起動し、ブラウザで `http://127.0.0.1:9119` が開きます。全機能のリファレンスについては、[ダッシュボードのドキュメント](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) を参照してください。
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャネルの接続

ゲートウェイが稼働していれば、任意のデバイスからローカルエージェントにアクセスできます。Hermes は [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)、[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) などをサポートしています。

---

### Discord

Discord では、ボットを追加するために**管理者権限を持つ**サーバーが必要です。サーバーを共有していても所有していない場合は、代わりに Telegram を使用してください。

#### Discord アプリケーションとボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、**New Application** をクリックします。名前を付けます（例: "hermes-bot"）。
2. サイドバーで **Bot** をクリックします。ボットのユーザー名を設定します。
3. Bot ページのまま、**Privileged Gateway Intents** までスクロールし、以下を有効にします:
   - **Message Content Intent**（必須）
   - **Server Members Intent**（推奨）
4. 上にスクロールして戻り、**Reset Token** をクリックしてボットトークンを生成します。これをコピーしてください。

#### ボットをサーバーに追加する

1. サイドバーで **OAuth2 / URL Generator** をクリックします。
2. **Scopes** の下で、`bot` と `applications.commands` を有効にします。
3. **Bot Permissions** の下で、以下を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成された URL をコピーし、ブラウザに貼り付けて、サーバーを選択し、確定します。

#### ID を取得し、DM を許可する

Discord で開発者モードを有効にし（**User Settings / Advanced / Developer Mode**）、その後:
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

サーバーアイコンを右クリック / **Privacy Settings** / **Direct Messages** をオンに切り替えます。これはペアリング手順に必要です。

#### Discord 用に Hermes を設定する

`~/.hermes/.env` に以下を追加します:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

次に、ゲートウェイを起動します:

```bash
hermes gateway
```

数秒以内にボットが Discord 上でオンラインになるはずです。DM またはボットが見えるチャンネルでメッセージを送信してください。

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Telegram ボットの作成

1. Telegram を開き、**@BotFather** にメッセージを送信します。
2. `/newbot` を送信し、案内に従います。表示されるボットトークンを保存してください。

#### Telegram 用に Hermes を設定する

`~/.hermes/.env` に以下を追加します:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Telegram のユーザー ID が分からない場合は？** Telegram で [@userinfobot](https://t.me/userinfobot) にメッセージを送ると、あなたの数値 ID が返信されます。

次に、ゲートウェイを起動します:

```bash
hermes gateway
```

テストのため、Telegram でボットに何かメッセージを送信してください。これで Telegram の DM 経由でエージェントとチャットできるようになりました。webhook モードや高度なオプションについては、[Telegram の詳細セットアップガイド](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) を参照してください。

---

## 次のステップ

エージェントがスマートフォンからコマンドを受け取り、ローカルマシン上で動作するようになった今、さらに探求する価値のある 3 つの方向性を紹介します:

1. **自動リサーチダイジェスト**: 毎朝、関心のあるトピックについて Hermes に Web 検索をさせ、ローカルモデルで調査結果を要約し、Telegram や Discord 経由でスマートフォンにダイジェストを送信するようスケジュールします。すべて自分のハードウェア上で実行され、クラウドコストは一切かかりません。

2. **オンデマンドのコードレビュー**: Hermes に GitHub リポジトリを指定し、オープンなプルリクエストをレビューさせ、コメントや要約をチャットに投稿させます。Docker ターミナルバックエンドを使用することで、すべての git 操作はサンドボックス内で実行され、ホスト環境をクリーンに保てます。

3. **ローカルファイルアシスタント**: Hermes に作業ディレクトリへのアクセス権を与え、スマートフォンからオンデマンドでファイルの整理、リネーム、要約、変換をさせます。Docker ターミナルバックエンドがすべての書き込みをサンドボックスのワークスペース内に制限するため、誤って破壊的な操作を行っても被害は限定されます。