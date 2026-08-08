<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# OpenClaw を Lemonade Server バックエンドで実行する

## 概要

[**OpenClaw**](https://openclaw.ai/) は、コードの記述と実行、ファイル管理、複雑な多段階タスクの遂行をユーザーに代わって行う自律型 AI エージェントです。単に質問に答えるだけのチャットアシスタントとは異なり、OpenClaw はシステム上で実際のアクションを実行します。そのため、要求の厳しいエージェントループに対応できる、高速かつ高性能な AI バックエンドが必要になります。

[**Lemonade Server**](https://lemonade-server.ai/) はまさにそのバックエンドです。これはオープンソースのローカル推論サーバーであり、GenAI モデルをお使いのハードウェア上で直接実行し、業界標準の OpenAI API を通じて公開します。

両者を組み合わせることで、完全にローカルな AI エージェントスタックが構築されます。Lemonade がモデル推論を担当し、OpenClaw がモデルの出力を実際のアクションへと変換するエージェントループを提供します。

> **続ける前に:** OpenClaw は高度に自律的な AI エージェントです。いかなる AI エージェントにもシステムへのアクセスを許可すると、予測不能または意図しない結果が生じる可能性があります。リスクを理解し、自律的なソフトウェアがユーザーに代わって動作することに納得できる場合にのみ、先に進んでください。

---

## このプレイブックで学べること

このプレイブックを完了すると、次のことができるようになります。

- **Lemonade Server** について学ぶ
- **OpenClaw をインストール**し、その AI バックエンドとして **Lemonade Server を指定する**。
- **OpenClaw ゲートウェイを起動**し、エージェントが動作準備完了であることを確認する。
- **通信チャンネル**（Discord または Telegram）を接続し、任意のデバイスからエージェントとチャットできるようにする。

---

## メモリ設定を行う

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

<!-- @os:linux -->
- `apt-get` を備えた **Ubuntu 24.04+** または互換性のある Debian ベースの Linux ディストリビューションを実行する PC
- 少なくとも **12 GB の RAM**（より大きなモデルには 64 GB 以上を推奨）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（オプション、OpenClaw をサンドボックス化する場合）
- モデルの重みのために**約 10～30 GB の空きディスク容量**
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** を実行する PC
- 少なくとも **12 GB の RAM**（より大きなモデルには 64 GB 以上を推奨）
- モデルの重みのために**約 10～30 GB の空きディスク容量**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（オプション、OpenClaw をサンドボックス化する場合）
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 推奨モデルを取得しロードする

このプレイブックで推奨するモデルは、Unsloth の **Qwen3.6-35B-A3B-GGUF** です。これは 263k トークンのコンテキストウィンドウを持つ強力な MoE モデルで、エージェントのワークロードに適しています。このモデルは UD-Q4_K_XL 量子化を使用しています。今すぐ取得しましょう。

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

このモデルのデフォルトのコンテキスト長は 262,144 トークンです。メモリ不足（OOM）エラーが発生した場合は、コンテキストウィンドウを小さくすることを検討してください。ただし、Qwen3.6 は複雑なタスクのために拡張コンテキストを活用するため、思考能力を維持するにはコンテキスト長を少なくとも 128K トークンに保つことをお勧めします。

> **ヒント: エージェントの応答を高速化するために思考を無効化する:** Qwen3.6-35B-A3B はデフォルトで思考モードで動作し、各応答の前に遅延が加わります。エージェントループではこのオーバーヘッドが急速に蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリには、思考を無効化するための設定ファイルが用意されています。使用するには、ファイルをダウンロードしてインポートします。
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

## WSL をセットアップする

OpenClaw は WSL 内で実行し（推奨）、Windows 上でネイティブに実行されている Lemonade に接続します。これにより、Lemonade の GPU アクセラレーションを Windows 側に保ちながら、OpenClaw 用の Linux シェル環境を利用できます。

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

WSL を終了して再起動します。

```powershell
exit
wsl --shutdown
wsl
```

### Windows から WSL へ Lemonade をブリッジする

WSL2 は仮想ネットワーク内で実行されます。Windows 上の Lemonade は `127.0.0.1` にバインドされますが、WSL から直接到達することはできません。Windows のポートプロキシを使用して、WSL のゲートウェイ IP から Windows のローカルホストへトラフィックを転送します。

**WSL のゲートウェイ IP を確認する**（WSL 内で実行）:

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加する**（PowerShell を管理者として実行し、`<WSL-Gateway-IP>` をお使いの WSL ゲートウェイ IP に置き換えてください）:

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> 注: `netsh: command not found` エラーが発生した場合は、代わりに明示的な実行ファイル名 `netsh.exe` を使用してみてください

**ファイアウォールルールを追加する**（同じ昇格済み PowerShell で）:

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL から確認する**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前のステップで Qwen3.6-35B-A3B-GGUF モデルを既にロードしている場合、以下のような JSON 出力が表示されるはずです。

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

#### 再起動後もブリッジを機能させ続ける

`netsh portproxy` ルールは再起動後も残りますが、`wsl --shutdown` や再起動の後に WSL のゲートウェイ IP が変わることがあります。その場合、プロキシは古い IP を指したままとなり、Lemonade は WSL から到達できなくなります。そうなった場合は、以下のいずれかの方法を使用してください。

**オプション 1（推奨）— ブリッジを自動的に修復する。** 毎回手動で対応する手間を省くため、起動時とサインイン時にブリッジをチェックし、ゲートウェイ IP が変わった場合にのみ再構築するスケジュールされたタスクを使用します。詳しくは [Lemonade WSL ブリッジ自動修復ガイド](assets/RepairLemonadeWslBridge.md) を参照してください。


**オプション 2 — ブリッジを手動で修復する。** まず、WSL 内で次を実行して現在の WSL ゲートウェイ IP を取得します。

```bash
ip route show default | awk '{print $3}' | head -1
```

この値をコピーしてください。以下で `<new-WSL-Gateway-IP>` の代わりに使用します。

次に、**管理者権限の PowerShell**（管理者として実行）で、既存のルールを一覧表示し、古い Lemonade のルールだけを削除して、現在の IP を使った新しいルールを追加します。

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

`show all` の出力において、古い Lemonade のルールは、接続アドレスが `127.0.0.1`、ポートが `13305` となっているエントリです。そのリッスンアドレスがあなたの `<old-WSL-Gateway-IP>` です。そのアドレスを指定して削除すると、このルールのみが削除され、マシン上の他のポートプロキシルールには影響しません。

セットアップ時に追加したファイアウォールルールはポート `13305`（IP ではなく）に紐づいているため、引き続き機能し、再作成する必要はありません。

> **推奨事項：** ゲートウェイの問題を避けるため、以下のシェル構成を強く推奨します。
> - **Windows コマンド**は **PowerShell** で実行してください
> - **WSL ディストロのコマンド**は（**管理者として**実行した）**コマンドプロンプト**で実行してください

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

`--no-onboard` フラグは対話型セットアップウィザードをスキップします。次のステップでモデルバックエンドを手動で設定するため、使用するモデルとサーバーを正確に制御できます。

新しいターミナルを開き、インストールを確認します。

```bash
openclaw --version
```

> **ヒント：** インストール後に `command not found` と表示される場合は、npm のグローバル bin ディレクトリを PATH に追加してください。
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> これを永続的にするには、上記の行を `~/.bashrc` または `~/.zshrc` ファイルに追加してください。

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


### OpenClaw に Lemonade を使用させる設定

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

> **OpenClaw のコンテキストウィンドウサイジング：** OpenClaw の圧縮（compaction）は `contextTokens > contextWindow − reserveTokens` の場合にトリガーされます。デフォルトの `reserveTokensFloor` は 20,000 トークンで、これは `reserveTokens` がそれより小さい場合に上書きする下限値であるため、コンテキストが約 37k を下回るモデルでは無限の圧縮ループが発生します。設定内で reserve を低く設定し、floor を一度無効にすれば、すべてのモデルに適用され、モデルごとの個別調整は不要です。
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` は *floor*（下限のガード）であり、reserve そのものではないため、floor のみを設定しても効果はありません。`reserveTokensFloor: 0` はこのガードを無効にするため、より小さい `reserveTokens` の値が受け入れられます。
>
> **これを適用すべき場合：** モデルの有効なコンテキストウィンドウが約 37k を下回る場合にこの設定を使用してください。これは、モデル自体が小さい場合（例：8k、16k、32k）や、意図的に低い値に制限している場合（例：128k のモデルを読み込んでいるが、Lemonade でコンテキストを 16k に設定している場合）のいずれかに該当します。この設定を行わないと、OpenClaw は起動時に無限の圧縮ループに陥ります。
>
> **フルコンテキストの大規模コンテキストモデルの場合：** この設定は完全にスキップしても構いません。デフォルトの設定で問題なく動作し、ウィンドウが埋まる前に圧縮が適切に働き、モデルには長い応答を生成する十分な余地があります。それでも適用する場合は、`reserveTokens: 4096` によって応答の長さが約 4k トークンに制限されることに注意してください。これにより、長いファイル生成や詳細なプランが途中で打ち切られる可能性があります。
>
> **どこに追加するか：** `compaction` ブロックは、`openclaw.json`（通常は `~/.openclaw/openclaw.json`）内の `agents.defaults` の中に配置してください。
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
> 設定の残りの部分（gateway、channels、models など）はそのままで変更不要です。追加が必要なのは `compaction` キーのみです。
### (推奨) Docker サンドボックス化を有効にする

OpenClaw では、エージェントによるファイル操作やコード操作をホスト上で直接実行するのではなく、隔離された Docker コンテナ経由で実行させることができます。これにより、意図しない操作が発生した場合の影響範囲をサンドボックス内に限定し、ホストのファイルシステムやネットワークには影響を与えません。

サンドボックス用のイメージを一度だけビルドします(Docker がインストールされている必要があります)。

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

`~/.openclaw/openclaw.json` 内にある既存の `agents.defaults` ブロックの中に `sandbox` キーを追加するには、以下を実行します。

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

サンドボックスコンテナは、デフォルトでは**ネットワークアクセスを持ちません**。バインドマウントやネットワークの上書き設定については、[サンドボックス化に関するリファレンス](https://docs.openclaw.ai/gateway/sandboxing)を参照してください。

> #### トラブルシューティング: Docker のパーミッションが拒否される
> 
> Docker コマンドを実行した際に「permission denied」と表示される場合:
> 
> **手順 1: ユーザーを docker グループに追加する**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **手順 2: エラーが解消しない場合は、恒久的な対処を適用する**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> その後、システムを**再起動**してください。
> 
> **一時的な簡易対処**(再起動後にリセットされます):
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
## (推奨) Firecrawl サービスとの OpenClaw 連携

[Firecrawl](https://docs.firecrawl.dev/introduction) は、こうした課題を回避し、OpenClaw の自動化の可能性を最大限に引き出すことができる、セルフホスト型の Web クローリングおよびコンテンツ抽出サービスを提供します。

このセットアップでは、OpenClaw は Podman によって管理される一連の Docker コンテナとして実行されます。ライフサイクル管理と自動起動を簡素化するために、Firecrawl をユーザーレベルの `systemd` サービスとして登録し、基盤となる Podman Compose スタックをオーケストレーションします。これにより、OpenClaw はコンテナと直接やり取りする代わりに、標準の `systemctl --user` コマンドを使用して、ゲートウェイの起動、停止、および Firecrawl サービスの検証を行うことができます。

シンプルにするため、全体のプロセスを4つの手順に分けています。

---

### 1. システムサービスを登録する
systemd のユーザー設定ディレクトリに移動します。
```bash
cd ~/.config/systemd/user
```
`firecrawl.service` という新しいファイルを作成して開きます。
```bash
nano firecrawl.service
```
以下の設定内容をコピーして貼り付けます。
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
この時点では、サービスは定義済みですが、まだ `systemd` に登録されていません。
上記で作成したファイル名と完全に一致していることを確認してから、以下を実行します。
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功すると、以下のような出力が表示されます。

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` には、自動起動するように設定されたサービスへのシンボリックリンクが含まれています。

### 2. Firecrawl を設定する

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) は、スクレイピングおよびデータ処理環境を完全に制御したいユーザーに最適ですが、その分、追加のメンテナンスや設定の手間が発生するというトレードオフがあります。

まず、リポジトリをクローンすることから始めます。
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
`/firecrawl` ルートディレクトリ内に `.env` を作成します。
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Podman Compose で OpenClaw をデプロイする

先に進む前に、最新の OpenClaw Docker イメージを pull していることを確認してください。
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
これが完了したら、OpenClaw の Compose ファイル [openclaw-compose.yaml](assets/openclaw-compose.yaml) をダウンロードし、`/firecrawl` ルートディレクトリに配置します。

> `WorkingDirectory=${HOME}/firecrawl` で指定されている通り、`systemd` がサービスを正しく検出・起動するためには、この配置規則に従う必要があります。

> 必要に応じて、追加の Firecrawl サービスを組み込むことで、スタックをいつでも拡張できます。利用可能なサービスの一覧は、公式の [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) で確認できます。

### 4. Firecrawl 経由で OpenClaw サービスを起動する

`systemd` に制御を委ねる前に、スタックを手動で実行して、すべてが正しく動作することを確認します。
```bash
podman compose -f openclaw-compose.yaml up -d
```
すべてが正しく設定されていれば、OpenClaw コンテナが起動し、コマンドラインの出力は以下のようになるはずです。
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

確認が済んだら、次に進む前にスタックを停止します。
```bash
podman compose -f openclaw-compose.yaml down
```
サービスを起動する前に、`firecrawl` ディレクトリとその `.env` ファイルに、正しい所有権とパーミッションが設定されていることを確認する必要があります。
これは、サービスが起動時に認証情報を書き込むために不可欠です。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
これですべての検証が完了したので、`systemd` 経由でサービスを起動します。
```bash
systemctl --user start firecrawl.service
```
[OpenClaw Actions](https://docs.openclaw.ai/) は、インタラクティブコンテナ内からアクセス可能であり、Web ダッシュボードは同じホストおよびポート(http://127.0.0.1:18789)で利用できます。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN` を取得する

サービスが起動して実行されると、ホームフォルダー(~/.openclaw)内に新しい `.openclaw` ディレクトリが作成されていることに気付くはずです。このディレクトリはデフォルトでロックされているため、ゲートウェイトークンを取得するにはロックを解除する必要があります。

1. ディレクトリへのアクセス権を付与します。
```bash
sudo chmod 777 ~/.openclaw/
```
2. ゲートウェイトークンを読み取ります。
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
出力の中から `OPENCLAW_GATEWAY_TOKEN` の値を探します。

3. ブラウザでゲートウェイダッシュボード(http://127.0.0.1:18789)を開きます。認証を求められたら、取得したトークンを貼り付けます。

サービスを停止するには、以下を実行します。
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## OpenClaw ゲートウェイを起動する

ゲートウェイは、エージェントループを管理し、ダッシュボードを提供する OpenClaw プロセスです。

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

ダッシュボードを開くには、ゲートウェイを実行したまま、2 つ目のターミナルで以下を実行します。

```bash
openclaw dashboard
```

ゲートウェイはループバックにバインドされているため、同じマシンから開いた場合、ダッシュボードは自動的に認証されます。ローカルアクセスにはトークンの入力もデバイスの承認も必要ありません。ダッシュボードには、アクティブなバックエンドとして Lemonade モデルが表示されているはずです。

> サンドボックス機能を有効にしている場合は、ダッシュボードからエージェントに `run hostname` を実行させることで動作を確認できます。マシンのホスト名ではなく短いコンテナ ID が表示されれば、サンドボックスは正しく機能しています。

**おめでとうございます。これで完全にローカルな AI エージェントスタックをゼロから構築できました。**

> **ゲートウェイトークンが必要ですか？** `openclaw dashboard --no-open` を実行すると、トークンが埋め込まれたダッシュボード URL が出力されます（クリップボードへのコピーも自動的に試みられます）。あるいは、トークンは `~/.openclaw/openclaw.json` 内の `gateway.auth.token` にも保存されています。

**別のデバイスからダッシュボードにアクセスする（SSH トンネル経由）**

OpenClaw をリモートマシンで実行している場合、SSH トンネルを介してローカルマシンからそのダッシュボードにアクセスできます。トンネルはゲートウェイのポート（`18789`）を転送するため、ローカルのブラウザは `127.0.0.1` 経由でリモートのゲートウェイと通信できます。

1. **ローカルマシン**から、一度リモートマシンに接続し、フィンガープリントの確認プロンプトを承認してホストを known hosts に追加します。

   ```bash
   ssh user@<host-ip>
   ```

2. 引き続き**ローカルマシン**で、SSH トンネルを開きます。

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **注:** パスワードを入力した後、ターミナルには何も出力されず、フリーズしたように見えます。これは想定どおりの動作です。`-N` フラグは SSH にリモートコマンドを実行しないよう指示するもので、単にトンネルを開いたままにするだけです。このターミナルは実行したままにしておいてください。

3. **ローカルマシン**でブラウザを開き、`http://127.0.0.1:18789` にアクセスします。

4. **リモートマシン**でゲートウェイトークンを出力し、それをブラウザに貼り付けてログインします。

   ```bash
   openclaw dashboard --no-open
   ```

   これにより、トークンが埋め込まれたダッシュボード URL が出力されます。そのトークンをコピーしてログインしてください。（トークンは `~/.openclaw/openclaw.json` 内の `gateway.auth.token` にも保存されています。）

> **リモートデバイスの承認:** 別のマシンやスマートフォンからダッシュボードを開くと、ブラウザにリクエスト ID が表示される場合があります。**リモートマシン**で、保留中のリクエストを一覧表示します。
> ```bash
> openclaw devices list
> ```
> 続いて、該当するリクエストを承認します。
> ```bash
> openclaw devices approve <requestId>
> ```
> これは、リモートまたは二次的なデバイスからアクセスする場合にのみ必要です。同じマシンからのループバックアクセスは自動的に認証されます。詳細については、[リモートアクセス](https://docs.openclaw.ai/gateway/remote)のドキュメントを参照してください。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャネルを接続する

ゲートウェイが起動していれば、どのデバイスからでもローカルエージェントにアクセスできます。ご自身の環境に合ったオプションを選んでください。OpenClaw は [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram)、その他のチャネルに対応しています。完全なリストは [docs.openclaw.ai](https://docs.openclaw.ai) をご覧ください。

---

### オプション A: Discord

Discord を利用するには、**管理者権限を持つ**サーバーが必要です（ボットを追加するため）。サーバーを共有していても自分が所有者でない場合は、代わりにオプション B（Telegram）を使用してください。

#### Discord アカウントとサーバーを作成する

Discord アカウントをお持ちでない場合は、[discord.com](https://discord.com) で登録してください。また、管理者権限を持つサーバーも必要です。Discord のサイドバーにある **+** アイコンをクリックし、**Create My Own** を選択して作成してください。プライベートサーバーで問題ありません。

#### Discord アプリケーションとボットを作成する

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、**New Application** をクリックします。名前を付けてください（例: "openclaw-bot"）。
2. サイドバーで **Bot** をクリックします。ボットのユーザー名を設定します。
3. 引き続き Bot ページで、**Privileged Gateway Intents** までスクロールし、以下を有効にします。
   - **Message Content Intent**（必須）
   - **Server Members Intent**（推奨）
4. 上にスクロールして戻り、**Reset Token** をクリックしてボットトークンを生成します。トークンをコピーしてください。

#### ボットをサーバーに追加する

1. サイドバーで **OAuth2/ URL Generator** をクリックします。
2. **Scopes** で `bot` と `applications.commands` を有効にします。
3. **Bot Permissions** で以下を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成された URL をコピーしてブラウザに貼り付け、サーバーを選択して確定します。ボットがサーバーのメンバー一覧に表示されるはずです。

#### ID を収集する

Discord でデベロッパーモードを有効にし（**User Settings/ Advanced/ Developer Mode**）、その後以下を行います。
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

#### サーバーメンバーからの DM を許可する

サーバーアイコンを右クリック/ **Privacy Settings**/ **Direct Messages** をオンに切り替えます。これにより、ボットがあなたに DM を送信できるようになり、ペアリング手順に必要です。

#### Discord 用に OpenClaw を設定する

ボットトークンを環境変数として保存し、Discord を有効化してトークンを参照し、サーバーを許可リストに追加する単一のパッチファイルを作成します。上記で収集した ID を使って `<server_id>` と `<user_id>` を置き換えてください。

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

> **エージェントに設定を任せるのはやめてください。** サンドボックス機能が有効な場合、エージェントはサンドボックス内から `~/.openclaw/openclaw.json` に書き込むことができません。代わりに、上記の CLI コマンドをホスト上で使用してください。

新しいチャネル設定を反映させるため、ゲートウェイを再起動します。

```bash
openclaw gateway run --bind loopback --port 18789
```

数秒以内に、ゲートウェイの出力に `logged in to discord as <bot-name>` と表示されるはずです。
#### Discordアカウントをペアリングする

Discordでボットにダイレクトメッセージを送ります。すると、短いペアリングコードが返信されます。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClawを実行しているマシンで承認します:
```bash
openclaw pairing approve discord <CODE>
```

> ペアリングコードは1時間で失効します。

これで、Discordから直接エージェントとチャットし、タスクをローカルハードウェアにオフロードできるようになりました。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### オプションB: Telegram

TelegramはほとんどのユーザーにとってDiscordよりもシンプルで、サーバーも管理者権限も不要です。

#### Telegramボットを作成する

1. Telegramを開き、**@BotFather**にメッセージを送ります。
2. `/newbot`を送信し、案内に従います。渡されたボットトークンを保存してください。

#### TelegramでOpenClawを設定する

トークンを環境変数として保存します:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

`~/.openclaw/openclaw.json`にチャンネル設定を追加します(またはダッシュボード経由でパッチを適用します):

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

ペアリングコードは1時間で失効します。これで、Telegramのダイレクトメッセージからエージェントとチャットできるようになりました。

---

## 次のステップ

これで、エージェントがスマートフォンからのコマンドを受け取り、ローカルマシン上で実行できるようになりました。ここでは、さらに探求する価値のある3つの方向性を紹介します。

1. **株式市場サマライザー**: OpenClawをスケジュール実行し、金融APIから一定間隔でデータを取得し、ローカルモデルでその日の値動きを要約して、毎朝選択したチャンネル経由でスマートフォンにダイジェストをプッシュします。

2. **ファインチューニングモニター**: TelegramやDiscordを介してリモートでトレーニングジョブを開始し、エージェントにトレーニングログを追跡させ、損失値、GPU使用率、ディスク使用量を定期的にスマートフォンへ報告させます。実行が停止したりVRAMが急上昇したりした場合、マシンの前にいなくてもすぐに気付くことができます。

3. **ローカルVLMを使ったIOT**: 玄関にカメラを向け、Lemonade上でビジョンモデルを実行し、OpenClawにオンデマンドまたはトリガーでフレームを分析させます。スマートフォンから「今日荷物は届いた?」と尋ねれば、自分自身のハードウェアから的確な答えが返ってきます。

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