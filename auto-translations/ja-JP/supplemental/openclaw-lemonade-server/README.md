<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# Lemonade Server をバックエンドとして OpenClaw を実行する

## 概要

[**OpenClaw**](https://openclaw.ai/) は、コードの記述と実行、ファイルの管理、複雑な複数ステップのタスクをユーザーに代わって実行できる自律型 AI エージェントです。質問に答えるだけのチャットアシスタントとは異なり、OpenClaw はシステム上で実際のアクションを実行します。そのため、要求の厳しいエージェントループに対応できる、高速で高性能な AI バックエンドが必要です。

[**Lemonade Server**](https://lemonade-server.ai/) がそのバックエンドです。これは、ハードウェア上で直接 GenAI モデルを実行し、業界標準の OpenAI API を通じてそれらを公開する、オープンソースのローカル推論サーバーです。

両者が組み合わさることで、完全にローカルで動作する AI エージェントスタックが構成されます。Lemonade がモデルの推論を担当し、OpenClaw がモデルの出力を実際のアクションへと変換するエージェントループを提供します。

> **続行する前に:** OpenClaw は高度に自律的な AI エージェントです。AI エージェントにシステムへのアクセスを許可すると、予測できない、または意図しない結果が生じる可能性があります。リスクを理解し、自律型ソフトウェアがユーザーに代わって動作することに問題がない場合にのみ続行してください。

---

## このプレイブックで学べること

このプレイブックを終える頃には、次のことができるようになります。

- **Lemonade Server** について学ぶ
- **OpenClaw をインストール**し、AI バックエンドとして **Lemonade Server を指定**する。
- **OpenClaw ゲートウェイを起動**し、エージェントが動作可能であることを確認する。
- **通信チャネル(Discord または Telegram)を接続**し、任意のデバイスからエージェントとチャットできるようにする。

---

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @os:linux -->
- `apt-get` を備えた **Ubuntu 24.04 以降**、または互換性のある Debian ベースの Linux ディストリビューションを実行している PC
- 少なくとも **12 GB の RAM**(より大規模なモデルには 64 GB 以上を推奨)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)(OpenClaw をサンドボックス化する場合はオプション)
- モデルの重み付け用に **約 10~30 GB の空きディスク容量**
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11** を実行している PC
- 少なくとも **12 GB の RAM**(より大規模なモデルには 64 GB 以上を推奨)
- モデルの重み付け用に **約 10~30 GB の空きディスク容量**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)(OpenClaw をサンドボックス化する場合はオプション)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 推奨モデルのプルとロード

このプレイブックで推奨されるモデルは、Unsloth 提供の **Qwen3.6-35B-A3B-GGUF** です。これは 263k トークンのコンテキストウィンドウを備えた強力な MoE モデルで、エージェントワークロードに適しています。このモデルは UD-Q4_K_XL 量子化を使用します。今すぐプルしてください。

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

このモデルのデフォルトのコンテキスト長は 262,144 トークンです。メモリ不足(OOM)エラーが発生した場合は、コンテキストウィンドウを縮小することを検討してください。ただし、Qwen3.6 は複雑なタスクに拡張コンテキストを活用するため、思考能力を維持するために少なくとも 128K トークンのコンテキスト長を維持することをお勧めします。

> **ヒント: より高速なエージェント応答のために思考を無効にする:** Qwen3.6-35B-A3B はデフォルトで思考モードで動作し、応答ごとに遅延が発生します。エージェントループでは、このオーバーヘッドが急速に蓄積します。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) リポジトリは、思考を無効にする構成済みの設定を提供しています。使用するには、ファイルをダウンロードしてインポートしてください。
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

OpenClaw は WSL 内で実行し(推奨)、Windows 上でネイティブに実行されている Lemonade に接続します。これにより、Lemonade の GPU アクセラレーションを Windows 側に維持しながら、OpenClaw 用の Linux シェル環境を利用できます。

### WSL と Ubuntu のインストール

管理者として PowerShell を開き、WSL カーネルをインストールします。

```powershell
wsl --install --no-distribution
```

次に、Ubuntu をインストールします。

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL での systemd の有効化

Ubuntu ターミナル内でこれを実行します。

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

WSL を終了し、再起動します。

```powershell
exit
wsl --shutdown
wsl
```

### Windows から WSL へ Lemonade をブリッジする

WSL2 は仮想ネットワーク内で動作します。Windows 上の Lemonade は `127.0.0.1` にバインドされているため、WSL から直接到達することはできません。Windows のポートプロキシは、WSL ゲートウェイ IP から Windows のローカルホストへトラフィックを転送します。

**WSL のゲートウェイ IP を確認する**(WSL 内で実行):

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシを追加する**(管理者として PowerShell で実行し、`<WSL-Gateway-IP>` を WSL のゲートウェイ IP に置き換えます):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> 注: `netsh: command not found` エラーが発生した場合は、代わりに明示的な実行ファイル名 `netsh.exe` を使用してみてください

**ファイアウォールルールを追加する**(同じ昇格された PowerShell で):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL から確認する**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

前の手順ですでに Qwen3.6-35B-A3B-GGUF モデルをロードしている場合、次のような JSON 出力が表示されるはずです。

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

`netsh portproxy` ルールは再起動後も残りますが、WSL のゲートウェイ IP は `wsl --shutdown` やリブートの後に変わることがあります。変わってしまうと、プロキシは古い IP を指したままになり、WSL から Lemonade に到達できなくなります。その場合は、以下のいずれかの方法を使用してください。

**オプション1（推奨）— ブリッジを自動で修復する。** 毎回手動で対応する手間を省くには、起動時およびサインイン時にブリッジを確認し、ゲートウェイ IP が変化した場合のみ再構築するスケジュールタスクを使用します。[Lemonade WSL ブリッジ自動修復ガイド](assets/RepairLemonadeWslBridge.md) を参照してください。


**オプション2 — ブリッジを手動で修復する。** まず、WSL 内で以下を実行して現在の WSL ゲートウェイ IP を取得します。

```bash
ip route show default | awk '{print $3}' | head -1
```

この値をコピーしてください。以下で `<new-WSL-Gateway-IP>` の代わりに使用します。

次に、**管理者権限の PowerShell**（管理者として実行）で既存のルールを一覧表示し、古くなった Lemonade のルールのみを削除し、現在の IP で新しいルールを追加します。

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

`show all` の出力において、古くなった Lemonade ルールは、接続アドレスがポート `13305` 上の `127.0.0.1` であるエントリです。そのリッスンアドレスが `<old-WSL-Gateway-IP>` です。そのアドレスで削除することで、このルールのみが削除され、マシン上の他のポートプロキシルールには影響がありません。

セットアップ時に追加したファイアウォールルールは、IP ではなくポート `13305` にバインドされているため、そのまま機能し続け、再作成する必要はありません。

> **推奨事項：** ゲートウェイの問題を避けるために、以下のシェル構成を強く推奨します：
> - **Windows コマンド** は **PowerShell** で実行してください
> - **WSL ディストリビューションのコマンド** は **コマンドプロンプト**（**管理者**として実行）で実行してください

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
> このセクションのコマンドは **WSL ターミナル** 内で実行してください。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` フラグは対話型セットアップウィザードをスキップします。次のステップでモデルバックエンドを手動で設定することになり、どのモデルとサーバーを使用するかを正確に制御できます。

新しいターミナルを開き、インストールを確認します。

```bash
openclaw --version
```

> **ヒント：** インストール後に `command not found` と表示される場合は、npm のグローバル bin ディレクトリを PATH に追加してください：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> これを恒久的にするには、上記の行を `~/.bashrc` または `~/.zshrc` ファイルに追加してください。

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


### OpenClaw に Lemonade を使用させるよう設定する

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

> **OpenClaw のコンテキストウィンドウサイズ設定：** OpenClaw の圧縮（compaction）は `contextTokens > contextWindow − reserveTokens` のときにトリガーされます。デフォルトの `reserveTokensFloor` は20,000トークンで、これは `reserveTokens` がそれより低い場合にそれを上書きする下限値のため、約37k未満のモデルコンテキストでは無限圧縮ループが発生します。設定で一度だけ低い reserve を設定し、floor を無効化すれば、すべてのモデルに適用され、モデルごとの個別調整は不要です：
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` は *下限値*（最低保証）であり、reserve そのものではありません。floor だけを設定しても効果はありません。`reserveTokensFloor: 0` はこの保護を無効化し、より低い `reserveTokens` が受け入れられるようにします。
>
> **これを適用すべき場合：** モデルの実効コンテキストウィンドウが約37k未満の場合にこの設定を使用してください。モデルが小さい（例：8k、16k、32k）場合や、意図的に低い値に制限している場合（例：128kモデルを読み込んでいるが Lemonade でコンテキストを16kに設定している場合）です。これを適用しないと、OpenClaw は起動時に無限圧縮ループに陥ります。
>
> **フルコンテキストで使用する大規模コンテキストモデル：** この設定は完全にスキップできます。デフォルトのままで問題なく、ウィンドウが埋まるかなり前に圧縮が発動し、モデルには長い応答を生成するための十分な余裕があります。それでも適用する場合は、`reserveTokens: 4096` が応答の長さを約4kトークンに制限することに注意してください。長いファイル生成や詳細なプランが途中で切れる可能性があります。
>
> **これをどこに追加するか：** `compaction` ブロックは、`openclaw.json`（通常は `~/.openclaw/openclaj.json`）内の `agents.defaults` の中に配置します：
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
> 設定の残りの部分（gateway、channels、models など）はそのままで、`compaction` キーのみ追加すればよいです。
### (推奨) Dockerサンドボックス化を有効にする

OpenClawは、エージェントのファイル操作やコード操作を、ホスト上で直接実行するのではなく、分離されたDockerコンテナ経由で行うように設定できます。これにより、意図しない操作の影響範囲をサンドボックス内に限定し、ホストのファイルシステムとネットワークを保護します。

サンドボックスイメージを一度ビルドします(Dockerがインストールされている必要があります):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

`~/.openclaw/openclaw.json` 内の既存の `agents.defaults` ブロックに `sandbox` キーを追加するには、以下を実行します:

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

サンドボックスコンテナには、デフォルトで**ネットワークアクセスがありません**。バインドマウントやネットワークの上書きについては、[サンドボックス化リファレンス](https://docs.openclaw.ai/gateway/sandboxing)を参照してください。

> #### トラブルシューティング: Dockerのパーミッションエラー
> 
> Dockerコマンドを実行した際に「permission denied」が発生する場合:
> 
> **手順1: ユーザーをdockerグループに追加する**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
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
> **簡易的な一時対応**(再起動後にリセットされます):
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
## (推奨) Firecrawlサービスを用いたOpenClaw連携

[Firecrawl](https://docs.firecrawl.dev/introduction)は、セルフホスト型のWebクロールおよびコンテンツ抽出サービスを提供しており、こうした課題を回避してOpenClawの自動化の可能性を最大限に引き出すことができます。

このセットアップでは、OpenClawはPodmanで管理される一連のDockerコンテナとして稼働します。ライフサイクル管理と自動起動を簡素化するため、Firecrawlをユーザーレベルの `systemd` サービスとして登録し、その内部でPodman Composeスタックを統括させます。これにより、コンテナを直接操作する代わりに、標準の `systemctl --user` コマンドを使って、OpenClawがゲートウェイを起動・停止したり、Firecrawlサービスの状態を確認したりできるようになります。

わかりやすくするため、このプロセス全体を4つの手順に分けて説明します。

---

### 1. システムサービスを登録する
systemdのユーザー設定ディレクトリに移動します:
```bash
cd ~/.config/systemd/user
```
新しいファイル `firecrawl.service` を作成し、開きます。
```bash
nano firecrawl.service
```
次の設定をコピー&ペーストします:
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
この時点で、サービスは定義済みですが、まだ `systemd` には登録されていません。
上記で作成したファイル名と正確に一致していることを確認したうえで、以下を実行します:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功すると、以下のような出力が表示されます:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` には、自動起動するように設定されたサービスへのシンボリックリンクが含まれています。

### 2. Firecrawlを設定する

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)は、スクレイピングやデータ処理環境を完全に管理したいユーザーに最適ですが、その分メンテナンスや設定の手間が追加で発生するというトレードオフがあります。

まず、リポジトリをクローンします:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
`/firecrawl` ディレクトリ内に `.env` ファイルを作成します:
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
完了したら、OpenClawのComposeファイル [openclaw-compose.yaml](assets/openclaw-compose.yaml) をダウンロードし、ルートの `/firecrawl` ディレクトリに配置します:

> `systemd` が `WorkingDirectory=${HOME}/firecrawl` で指定されたサービスを正しく見つけて起動するためには、この配置規則に従う必要があります。

> 必要に応じて、Firecrawlの追加サービスをスタックに組み込むことでいつでも拡張できます。利用可能なサービスの全リストは、公式の[Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)で確認できます。

### 4. Firecrawl経由でOpenClawサービスを起動する

制御を `systemd` に渡す前に、スタックを手動で実行してすべてが正しく動作することを確認します:
```bash
podman compose -f openclaw-compose.yaml up -d
```
すべてが正しく設定されていれば、OpenClawコンテナが起動し、コマンドラインの出力は以下のようになるはずです:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

確認が済んだら、次に進む前にスタックを停止します:
```bash
podman compose -f openclaw-compose.yaml down
```
サービスを起動する前に、`firecrawl` ディレクトリおよびその `.env` ファイルの所有権とパーミッションが正しく設定されていることを確認する必要があります。
これは、起動時にサービスが認証情報を書き込むために不可欠です。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
これですべての確認が済んだので、`systemd` 経由でサービスを起動します:
```bash
systemctl --user start firecrawl.service
```
[The OpenClaw Actions](https://docs.openclaw.ai/)は対話型コンテナ内からアクセスでき、Webダッシュボードは同じホストおよびポート(http://127.0.0.1:18789)で利用できます。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN` を取得する

サービスが起動すると、ホームフォルダ(~/.openclaw)内に新しい `.openclaw` ディレクトリが作成されていることに気づくはずです。このディレクトリはデフォルトでロックされているため、ゲートウェイトークンを取得するにはロックを解除する必要があります。

1. ディレクトリへのアクセス権を付与します:
```bash
sudo chmod 777 ~/.openclaw/
```
2. ゲートウェイトークンを読み取ります:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
出力内の `OPENCLAW_GATEWAY_TOKEN` の値を確認してください。

3. ブラウザでゲートウェイダッシュボード(http://127.0.0.1:18789)を開きます。認証を求められたら、取得したトークンを貼り付けてください。

サービスを停止するには、以下を実行します:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## OpenClaw Gatewayの起動

Gatewayは、エージェントループを管理しダッシュボードを提供するOpenClawのプロセスです:

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

ダッシュボードを開くには、Gatewayを起動したまま、別のターミナルで以下を実行します:

```bash
openclaw dashboard
```

Gatewayはループバックにバインドされているため、同じマシンから開いた場合、ダッシュボードは自動的に認証されます。ローカルアクセスにはトークンの入力やデバイスの承認は必要ありません。アクティブなバックエンドとしてLemonadeモデルが表示された、OpenClawダッシュボードが表示されるはずです。

> サンドボックスを有効にしている場合は、ダッシュボードからエージェントに`run hostname`を依頼することで確認できます。マシンのホスト名ではなく短いコンテナIDが表示されれば、サンドボックスは正常に機能しています。

**おめでとうございます。これで完全にローカルなAIエージェントスタックをゼロから構築できました。**

> **Gatewayトークンが必要ですか?** `openclaw dashboard --no-open`を実行すると、トークンが埋め込まれたダッシュボードのURLが出力されます(クリップボードへのコピーも試みます)。あるいは、トークンは`~/.openclaw/openclaw.json`内の`gateway.auth.token`にあります。

**別のデバイスからダッシュボードにアクセスする(SSHトンネル経由)**

OpenClawがリモートマシン上で動作している場合、SSHトンネルを使用してローカルマシンからそのダッシュボードにアクセスできます。トンネルはGatewayのポート(`18789`)を転送するため、ローカルのブラウザは`127.0.0.1`経由でリモートのGatewayと通信できます。

1. **ローカルマシン**から、一度リモートマシンに接続し、フィンガープリントのプロンプトを承諾して、ホストをknown_hostsに追加します:

   ```bash
   ssh user@<host-ip>
   ```

2. 引き続き**ローカルマシン**で、SSHトンネルを開きます:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **注:** パスワードを入力した後、ターミナルには何も表示されず、ハングしているように見えます。これは想定された動作です。`-N`フラグはSSHにリモートコマンドを実行しないよう指示するため、単にトンネルを開いたままにします。このターミナルは実行したままにしてください。

3. **ローカルマシン**でブラウザを開き、`http://127.0.0.1:18789`にアクセスします。

4. **リモートマシン**で、Gatewayトークンを出力し、それをブラウザに貼り付けてログインします:

   ```bash
   openclaw dashboard --no-open
   ```

   これにより、トークンが埋め込まれたダッシュボードのURLが出力されます。ログインするにはそのトークンをコピーしてください。(トークンは`~/.openclaw/openclaw.json`内の`gateway.auth.token`にも保存されています。)

> **リモートデバイスの承認:** 別のマシンやスマートフォンからダッシュボードを開くと、ブラウザにリクエストIDが表示されることがあります。**リモートマシン**で、保留中のリクエストを一覧表示します:
> ```bash
> openclaw devices list
> ```
> 次に、該当するリクエストを承認します:
> ```bash
> openclaw devices approve <requestId>
> ```
> これはリモートまたは二次的なデバイスの場合にのみ必要です。同じマシンからのループバックアクセスは自動的に認証されます。詳細は[Remote Access](https://docs.openclaw.ai/gateway/remote)のドキュメントを参照してください。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャネルの接続

Gatewayが起動したら、どのデバイスからでもローカルのエージェントにアクセスできます。ご自身の環境に合ったオプションを選んでください。OpenClawは[Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram)、その他のチャネルをサポートしています。全リストは[docs.openclaw.ai](https://docs.openclaw.ai)をご覧ください。

---

### オプションA: Discord

Discordでは、Botを追加するために**管理者権限を持つ**サーバーが必要です。サーバーを共有していても自分がオーナーでない場合は、代わりにオプションB(Telegram)を使用してください。

#### Discordアカウントとサーバーの作成

Discordアカウントをお持ちでない場合は、[discord.com](https://discord.com)でサインアップしてください。また、自分が管理者であるサーバーも必要です。Discordサイドバーの**+**アイコンをクリックし、**Create My Own**を選択して作成してください。プライベートサーバーで問題ありません。

#### Discordアプリケーションとボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスし、**New Application**をクリックします。名前(例: "openclaw-bot")を付けます。
2. サイドバーで**Bot**をクリックします。ボットのユーザー名を設定します。
3. 引き続きBotページで、**Privileged Gateway Intents**までスクロールし、以下を有効にします:
   - **Message Content Intent**(必須)
   - **Server Members Intent**(推奨)
4. 上にスクロールして戻り、**Reset Token**をクリックしてボットトークンを生成します。コピーしてください。

#### Botをサーバーに追加する

1. サイドバーで**OAuth2/ URL Generator**をクリックします。
2. **Scopes**の下で、`bot`と`applications.commands`を有効にします。
3. **Bot Permissions**の下で、View Channels、Send Messages、Read Message History、Embed Links、Attach Filesを有効にします。
4. 生成されたURLをコピーし、ブラウザに貼り付け、サーバーを選択して確定します。ボットがサーバーのメンバーリストに表示されるはずです。

#### IDの収集

Discordで開発者モードを有効にし(**ユーザー設定/詳細設定/開発者モード**)、その後:
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

#### サーバーメンバーからのDMを許可する

サーバーアイコンを右クリック/**プライバシー設定**/**ダイレクトメッセージ**をオンにします。これにより、ボットがあなたにDMを送信できるようになり、ペアリングのステップに必要です。

#### Discord用にOpenClawを設定する

ボットトークンを環境変数として保存し、Discordを有効にし、トークンを参照し、サーバーを許可リストに登録する単一のパッチファイルを作成します。上記で収集したIDで`<server_id>`と`<user_id>`を置き換えてください。

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

> **設定をエージェントに依頼することに頼らないでください。** サンドボックスが有効な場合、エージェントはサンドボックス内から`~/.openclaw/openclaw.json`に書き込むことができません。代わりにホスト上で上記のCLIコマンドを使用してください。

新しいチャネル設定を反映させるため、Gatewayを再起動します:

```bash
openclaw gateway run --bind loopback --port 18789
```

数秒以内にGatewayの出力に`logged in to discord as <bot-name>`と表示されるはずです。
#### Discordアカウントをペアリングする

Discordでボットにダイレクトメッセージを送信します。ボットは短いペアリングコードで返信します。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClawを実行しているマシンで承認します:
```bash
openclaw pairing approve discord <CODE>
```

> ペアリングコードは1時間で期限切れになります。

これでDiscordから直接エージェントとチャットし、タスクをローカルハードウェアにオフロードできるようになりました。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### オプションB: Telegram

TelegramはほとんどのユーザーにとってDiscordよりもシンプルで、サーバーも管理者権限も不要です。

#### Telegramボットを作成する

1. Telegramを開き、**@BotFather** にメッセージを送信します。
2. `/newbot` を送信し、指示に従います。付与されたボットトークンを保存してください。

#### OpenClawをTelegram用に設定する

トークンを環境変数として保存します:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

チャンネル設定を `~/.openclaw/openclaw.json` に追加するか（またはダッシュボード経由でパッチを適用します）:

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

ゲートウェイを再起動し、Telegramでボットに任意のメッセージを送信します。ペアリングを承認します:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

ペアリングコードは1時間で期限切れになります。これでTelegramのダイレクトメッセージからエージェントとチャットできるようになりました。

---

## 次のステップ

これでエージェントはスマートフォンからコマンドを受け取り、ローカルマシン上で実行できるようになりました。ここでは、さらに掘り下げる価値のある3つの方向性を紹介します。

1. **株式市場サマライザー**: OpenClawをスケジュール設定して、一定間隔で金融APIからデータを取得し、ローカルモデルでその日の値動きを要約して、選択したチャネル経由で毎朝スマートフォンにダイジェストをプッシュします。

2. **ファインチューニングモニター**: TelegramまたはDiscord経由でリモートからトレーニングジョブを開始し、エージェントにトレーニングログを追跡させ、損失値、GPU使用率、ディスク使用量を定期的にスマートフォンへ報告させます。実行が停止したりVRAMが急増したりした場合でも、マシンの前にいなくてもすぐに気づくことができます。

3. **ローカルVLMを使ったIOT**: 玄関先にカメラを向け、Lemonade上でビジョンモデルを実行し、OpenClawにオンデマンドまたはトリガーでフレームを分析させます。スマートフォンから「今日荷物は届いた？」と尋ねれば、自分のハードウェアから直接答えが返ってきます。

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