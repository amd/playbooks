<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# Lemonade Serverをバックエンドとして使用し、OpenClawを実行する

## 概要

[**OpenClaw**](https://openclaw.ai/)は、コードの記述と実行、ファイルの管理、複雑な多段階タスクの処理をユーザーに代わって行う自律型AIエージェントです。質問に答えるだけのチャットアシスタントとは異なり、OpenClawはシステム上で実際のアクションを実行します。そのため、要求の厳しいエージェントループに対応できる、高速かつ高性能なAIバックエンドが必要になります。

[**Lemonade Server**](https://lemonade-server.ai/)はそのバックエンドです。これは、お使いのハードウェア上で直接GenAIモデルを実行し、業界標準のOpenAI APIを通じて公開する、オープンソースのローカル推論サーバーです。

両者を組み合わせることで、完全にローカルなAIエージェントスタックが構築されます。Lemonadeがモデル推論を担当し、OpenClawがモデルの出力を実際のアクションへと変換するエージェントループを提供します。

> **続行する前に:** OpenClawは高度に自律的なAIエージェントです。AIエージェントにシステムへのアクセスを許可すると、予測不可能または意図しない結果が生じる可能性があります。リスクを理解し、自律的なソフトウェアがユーザーに代わって動作することに問題がない場合にのみ、続行してください。

---

## このプレイブックで学べること

このプレイブックを終えると、以下のことができるようになります。

- **Lemonade Server**について学ぶ
- **OpenClawをインストール**し、AIバックエンドとして**Lemonade Serverを指定**する。
- **OpenClawゲートウェイを起動**し、エージェントが動作準備できていることを確認する。
- **通信チャンネル**(DiscordまたはTelegram)を接続し、任意のデバイスからエージェントとチャットできるようにする。

---

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

<!-- @os:linux -->
- `apt-get`を備えた**Ubuntu 24.04以降**、または互換性のあるDebianベースのLinuxディストリビューションを実行しているPC
- 少なくとも**12GBのRAM**(より大きなモデルの場合は64GB以上推奨)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)(オプション、OpenClawをサンドボックス化する場合)
- モデルの重み用に**約10~30GBの空きディスク容量**
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11**を実行しているPC
- 少なくとも**12GBのRAM**(より大きなモデルの場合は64GB以上推奨)
- モデルの重み用に**約10~30GBの空きディスク容量**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)(オプション、OpenClawをサンドボックス化する場合)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 推奨モデルのプルとロード

このプレイブックで推奨されるモデルは、Unslothによる**Qwen3.6-35B-A3B-GGUF**です。これは263kトークンのコンテキストウィンドウを持つ強力なMoEモデルで、エージェントワークロードに適しています。このモデルはUD-Q4_K_XL量子化を使用しています。今すぐプルしてください。

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

このモデルのデフォルトのコンテキスト長は262,144トークンです。メモリ不足(OOM)エラーが発生した場合は、コンテキストウィンドウを縮小することを検討してください。ただし、Qwen3.6は拡張コンテキストを複雑なタスクに活用するため、思考能力を維持するためにも、コンテキスト長は少なくとも128Kトークンを保つことを推奨します。

> **ヒント: 思考を無効化してエージェントの応答を高速化する:** Qwen3.6-35B-A3Bはデフォルトで思考モードで動作し、各応答の前に遅延が追加されます。エージェントループでは、このオーバーヘッドが急速に積み重なります。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json)リポジトリには、思考を無効化する設定済みの構成ファイルが用意されています。これを使用するには、ファイルをダウンロードしてインポートしてください。
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

OpenClawはWSL内(推奨)で実行し、Windows上でネイティブに動作しているLemonadeに接続します。これにより、Lemonadeのウィンドウズ側でのGPUアクセラレーションを維持しながら、OpenClaw用のLinuxシェル環境を利用できます。

### WSLとUbuntuのインストール

PowerShellを管理者として開き、WSLカーネルをインストールします。

```powershell
wsl --install --no-distribution
```

次に、Ubuntuをインストールします。

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

WSLを終了して再起動します。

```powershell
exit
wsl --shutdown
wsl
```

### WindowsからWSLへのLemonadeのブリッジ

WSL2は仮想ネットワーク内で動作します。Windows上のLemonadeは`127.0.0.1`にバインドされますが、WSLから直接アクセスすることはできません。Windowsのポートプロキシを使用して、WSLゲートウェイIPからWindowsのlocalhostへトラフィックを転送します。

**WSLゲートウェイIPの確認**(WSL内で実行):

```bash
ip route show default | awk '{print $3}' | head -1
```

**ポートプロキシの追加**(PowerShellを管理者として実行し、`<WSL-Gateway-IP>`をご自身のWSLゲートウェイIPに置き換えてください):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> 注: `netsh: command not found`というエラーが発生した場合は、代わりに明示的な実行ファイル名`netsh.exe`を使用してみてください。

**ファイアウォールルールの追加**(同じ管理者権限のPowerShellで):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSLから確認**:

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

#### 再起動後もブリッジを正常に機能させ続ける

`netsh portproxy` のルールは再起動後も保持されますが、`wsl --shutdown` や再起動の後に WSL のゲートウェイ IP が変わることがあります。その場合、プロキシは古い IP を指したままとなり、WSL から Lemonade に到達できなくなります。これが発生した場合は、以下のいずれかの方法を使用してください。

**オプション1(推奨)— ブリッジを自動的に修復する。** これを毎回手動で行わずに済むように、起動時とサインイン時にブリッジをチェックし、ゲートウェイ IP が変化した場合にのみ再構築するスケジュールタスクを使用します。詳しくは[Lemonade WSL ブリッジ自動修復ガイド](assets/RepairLemonadeWslBridge.md)を参照してください。


**オプション2 — ブリッジを手動で修復する。** まず、WSL 内で次を実行して現在の WSL ゲートウェイ IP を取得します:

```bash
ip route show default | awk '{print $3}' | head -1
```

この値をコピーしておき、以下の `<new-WSL-Gateway-IP>` の代わりに使用します。

次に、**管理者権限の PowerShell**(管理者として実行)で、既存のルールを一覧表示し、古くなった Lemonade のルールだけを削除して、現在の IP で新しいルールを追加します:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

`show all` の出力において、古くなった Lemonade のルールは、接続先アドレスがポート `13305` の `127.0.0.1` となっているエントリです。そのリッスンアドレスが `<old-WSL-Gateway-IP>` となります。そのアドレスを指定して削除すれば、このルールのみが削除され、マシン上の他のポートプロキシルールには影響しません。

セットアップ時に追加したファイアウォールルールはポート `13305`(IP ではなく)にバインドされているため、そのまま機能し続け、再作成する必要はありません。

> **推奨事項:** ゲートウェイの問題を回避するため、次のシェル構成を強くお勧めします:
> - **Windows コマンド**は **PowerShell** で実行してください
> - **WSL ディストリビューションのコマンド**は**コマンドプロンプト**(**管理者**として実行)で実行してください

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

## OpenClaw のインストールと構成

### OpenClaw のインストール
<!-- @os:windows -->
> このセクションのコマンドは**WSL ターミナル**内で実行してください。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` フラグは対話形式のセットアップウィザードをスキップします。次のステップでモデルバックエンドを手動で構成するため、どのモデルとサーバーを使用するかを正確に制御できます。

新しいターミナルを開き、インストールを確認します:

```bash
openclaw --version
```

> **ヒント:** インストール後に `command not found` と表示される場合は、npm のグローバル bin ディレクトリを PATH に追加してください:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> これを恒久的に適用するには、上記の行を `~/.bashrc` または `~/.zshrc` ファイルに追加してください。

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


### OpenClaw で Lemonade を使用するよう構成する

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

このコマンドは、OpenClaw の構成を `~/.openclaw/openclaw.json` に書き込みます。

> **OpenClaw のコンテキストウィンドウサイズ設定:** OpenClaw の圧縮(compaction)は `contextTokens > contextWindow − reserveTokens` のときにトリガーされます。デフォルトの `reserveTokensFloor` は 20,000 トークンで、これは `reserveTokens` より小さい場合にそれを上書きする下限値(floor)です。そのため、約 37k 未満のモデルコンテキストでは無限圧縮ループが発生してしまいます。設定ファイル内で低い reserve 値を設定し、floor を無効化すれば、すべてのモデルに適用され、モデルごとの個別調整は不要になります:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` は *floor*(最低保証値)であり、reserve そのものではないため、floor だけを設定しても効果はありません。`reserveTokensFloor: 0` とすることでこのガードを無効化し、より低い `reserveTokens` の値が有効になります。
>
> **適用すべき場合:** モデルの実効コンテキストウィンドウが約 37k 未満の場合にこの設定を使用してください。モデル自体が小さい(例: 8k、16k、32k)場合や、意図的に低い値に制限している場合(例: 128k モデルを読み込みつつ Lemonade でコンテキストを 16k に設定している場合)が該当します。この設定を行わないと、OpenClaw は起動時に無限圧縮ループに陥ります。
>
> **フルコンテキストの大規模コンテキストモデルの場合:** この設定はまったく不要です。デフォルト設定で問題なく動作し、ウィンドウが埋まるかなり前に圧縮が働き始め、モデルには長い応答を生成するための十分な余地があります。もし適用する場合は、`reserveTokens: 4096` が応答の長さを約 4k トークンに制限することに注意してください。これにより、長いファイル生成や詳細な計画が途中で打ち切られる可能性があります。
>
> **追加する場所:** `compaction` ブロックは、`openclaw.json`(通常は `~/.openclaw/openclaw.json`)内の `agents.defaults` の中に配置します:
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
> 構成の残りの部分(gateway、channels、models など)はそのままで、`compaction` キーのみを追加すれば構いません。
### (推奨) Docker サンドボックスの有効化

OpenClaw では、エージェントによるすべてのファイル操作やコード操作を、ホスト上で直接実行するのではなく、隔離された Docker コンテナ経由で実行するように構成できます。これにより、意図しない操作が発生した場合の影響範囲がサンドボックス内に限定され、ホストのファイルシステムやネットワークには影響が及びません。

サンドボックスイメージを一度だけビルドします(Docker がインストールされている必要があります)。

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

以下を実行して、`~/.openclaw/openclaw.json` 内の既存の `agents.defaults` ブロックに `sandbox` キーを追加します:

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

サンドボックスコンテナは、デフォルトでは**ネットワークアクセスを一切持ちません**。バインドマウントやネットワークのオーバーライドについては、[サンドボックスに関するリファレンス](https://docs.openclaw.ai/gateway/sandboxing)を参照してください。

> #### トラブルシューティング: Docker の Permission Denied
> 
> Docker コマンドの実行時に「permission denied」が発生する場合:
> 
> **ステップ 1: ユーザーを docker グループに追加する**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **ステップ 2: それでもエラーが解消しない場合は、恒久的な修正を適用する**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> その後、システムを**再起動**してください。
> 
> **応急処置**(再起動すると元に戻ります):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) は、セルフホスト型の Web クローリングおよびコンテンツ抽出サービスを提供しており、こうした課題を回避し、OpenClaw 自動化の真価を最大限に引き出すことができます。

このセットアップでは、OpenClaw は Podman によって管理される一連の Docker コンテナとして実行されます。ライフサイクル管理を簡素化し、自動起動を実現するために、Firecrawl を基盤となる Podman Compose スタックを統括するユーザーレベルの `systemd` サービスとして登録します。これにより、コンテナを直接操作することなく、標準の `systemctl --user` コマンドを使用して、OpenClaw のゲートウェイを起動・停止したり、Firecrawl サービスの状態を確認したりできるようになります。

わかりやすくするために、この一連の手順を 4 つのステップに分けて説明します。

---

### 1. システムサービスの登録
systemd のユーザー構成ディレクトリに移動します:
```bash
cd ~/.config/systemd/user
```
`firecrawl.service` という名前の新しいファイルを作成し、開きます。
```bash
nano firecrawl.service
```
以下の構成をコピーして貼り付けます:
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
この時点では、サービスは定義されただけで、まだ `systemd` に登録されていません。
上記で作成したファイル名と完全に一致していることを確認したうえで、以下を実行します:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
成功すると、以下のような出力が表示されるはずです:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` には、自動起動するように設定されたサービスへのシンボリックリンクが格納されています。

### 2. Firecrawl の構成

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) は、スクレイピングやデータ処理の環境を完全に制御したいユーザーに最適ですが、その反面、追加のメンテナンスや構成作業が必要になるというトレードオフがあります。

まず、リポジトリをクローンするところから始めます:
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
### 3. Podman Compose を使った OpenClaw のデプロイ

先に進む前に、最新の OpenClaw Docker イメージを pull 済みであることを確認してください:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
それが完了したら、OpenClaw の Compose ファイル [openclaw-compose.yaml](assets/openclaw-compose.yaml) をダウンロードし、ルートの `/firecrawl` ディレクトリに配置します:

> `WorkingDirectory=${HOME}/firecrawl` で指定されている通り、`systemd` がサービスを正しく見つけて起動するためには、この配置規則が必須です。

> 必要に応じて、Firecrawl の追加サービスを組み込むことで、このスタックをいつでも拡張できます。利用可能なサービスの全一覧は、公式の [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) で確認できます。

### 4. Firecrawl 経由で OpenClaw サービスを起動する

制御を `systemd` に委ねる前に、スタックを手動で実行し、すべてが正しく動作することを確認します:
```bash
podman compose -f openclaw-compose.yaml up -d
```
すべてが正しく構成されていれば、OpenClaw コンテナが起動し、コマンドラインの出力は次のような内容になるはずです:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

確認できたら、先に進む前にスタックを停止しておきます:
```bash
podman compose -f openclaw-compose.yaml down
```
サービスを開始する前に、`firecrawl` ディレクトリとその `.env` ファイルに正しい所有者とパーミッションが設定されていることを確認する必要があります。
これは、サービスが起動時に認証情報を書き込むために不可欠です。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
すべての検証が完了したので、`systemd` 経由でサービスを開始します:
```bash
systemctl --user start firecrawl.service
```
[The OpenClaw Actions](https://docs.openclaw.ai/) はインタラクティブコンテナ内からアクセス可能で、Web ダッシュボードは同じホストおよびポート http://127.0.0.1:18789 で利用できます。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN` の取得

サービスが起動すると、ホームフォルダ内(~/.openclaw)に新しい `.openclaw` ディレクトリが作成されていることに気付くはずです。このディレクトリはデフォルトでロックされているため、ゲートウェイトークンを取得するにはロックを解除する必要があります。

1. ディレクトリへのアクセス権を付与します:
```bash
sudo chmod 777 ~/.openclaw/
```
2. ゲートウェイトークンを読み取ります:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
出力の中から `OPENCLAW_GATEWAY_TOKEN` の値を探します。

3. ブラウザでゲートウェイダッシュボード http://127.0.0.1:18789 を開きます。認証を求められたら、トークンを貼り付けてください。

サービスを停止するには、以下を実行します:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## OpenClaw ゲートウェイの起動

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

ダッシュボードを開くには、ゲートウェイがまだ実行中の状態で、2つ目のターミナルで次を実行します:

```bash
openclaw dashboard
```

ゲートウェイはループバックにバインドされているため、同じマシンから開いた場合、ダッシュボードは自動的に認証されます。ローカルアクセスにはトークンの入力もデバイスの承認も必要ありません。OpenClaw ダッシュボードに、Lemonade モデルがアクティブなバックエンドとして表示されるはずです。

> サンドボックス化を有効にしている場合は、ダッシュボードからエージェントに `run hostname` を依頼することで確認できます。マシンのホスト名ではなく短いコンテナ ID が表示されれば、サンドボックスは正しく機能しています。

**おめでとうございます。これで、完全にローカルで動作する AI エージェントスタックをゼロから構築できました。**

> **ゲートウェイトークンが必要ですか？** `openclaw dashboard --no-open` を実行すると、トークンが埋め込まれたダッシュボード URL が出力されます（クリップボードへのコピーも試みます）。あるいは、トークンは `~/.openclaw/openclaw.json` 内の `gateway.auth.token` にあります。

**別のデバイスからダッシュボードにアクセスする（SSH トンネル経由）**

OpenClaw がリモートマシン上で実行されている場合でも、SSH トンネルを介してローカルマシンからそのダッシュボードにアクセスできます。このトンネルはゲートウェイポート（`18789`）を転送するため、ローカルのブラウザは `127.0.0.1` 経由でリモートのゲートウェイと通信できます。

1. **ローカルマシン**から、一度リモートマシンに接続し、フィンガープリントのプロンプトを承認して、そのホストを known_hosts に追加します:

   ```bash
   ssh user@<host-ip>
   ```

2. 引き続き**ローカルマシン**で、SSH トンネルを開きます:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **注:** パスワードを入力した後、ターミナルには何も出力されず、ハングしているように見えます。これは想定どおりの動作です。`-N` フラグは SSH にリモートコマンドを実行しないよう指示するため、単にトンネルを開いたままにしているだけです。このターミナルは実行したままにしておいてください。

3. **ローカルマシン**でブラウザを開き、`http://127.0.0.1:18789` にアクセスします。

4. **リモートマシン**で、ゲートウェイトークンを出力し、それをブラウザに貼り付けてログインします:

   ```bash
   openclaw dashboard --no-open
   ```

   これにより、トークンが埋め込まれたダッシュボード URL が出力されます。そのトークンをコピーしてログインしてください。（トークンは `~/.openclaw/openclaw.json` 内の `gateway.auth.token` にも保存されています。）

> **リモートデバイスの承認:** 別のマシンやスマートフォンからダッシュボードを開くと、ブラウザにリクエスト ID が表示される場合があります。**リモートマシン**で、保留中のリクエストを一覧表示します:
> ```bash
> openclaw devices list
> ```
> 次に、該当するリクエストを承認します:
> ```bash
> openclaw devices approve <requestId>
> ```
> これはリモートまたは二次デバイスの場合にのみ必要です。同一マシンからのループバックアクセスは自動的に認証されます。詳細は [Remote Access](https://docs.openclaw.ai/gateway/remote) のドキュメントを参照してください。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## オプション: コミュニケーションチャンネルを接続する

ゲートウェイが実行されていれば、任意のデバイスからローカルエージェントにアクセスできます。ご自身の環境に合ったオプションを選んでください。OpenClaw は [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram)、その他のチャンネルをサポートしています。完全な一覧は [docs.openclaw.ai](https://docs.openclaw.ai) をご覧ください。

---

### オプション A: Discord

Discord では、ボットを追加するために**管理者権限を持つ**サーバーが必要です。サーバーを共有していても所有していない場合は、代わりにオプション B（Telegram）を使用してください。

#### Discord アカウントとサーバーを作成する

Discord アカウントをお持ちでない場合は、[discord.com](https://discord.com) で登録してください。また、自分が管理者であるサーバーも必要です。Discord のサイドバーにある **+** アイコンをクリックし、**Create My Own** を選択して作成してください。プライベートサーバーで問題ありません。

#### Discord アプリケーションとボットを作成する

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、**New Application** をクリックします。名前を付けます（例: "openclaw-bot"）。
2. サイドバーで **Bot** をクリックします。ボットのユーザー名を設定します。
3. 同じ Bot ページで下にスクロールし、**Privileged Gateway Intents** まで移動して、次を有効にします:
   - **Message Content Intent**（必須）
   - **Server Members Intent**（推奨）
4. 上にスクロールして戻り、**Reset Token** をクリックしてボットトークンを生成します。コピーしてください。

#### ボットをサーバーに追加する

1. サイドバーで **OAuth2/ URL Generator** をクリックします。
2. **Scopes** の下で `bot` と `applications.commands` を有効にします。
3. **Bot Permissions** の下で、次を有効にします: View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 生成された URL をコピーし、ブラウザに貼り付け、サーバーを選択して確定します。ボットがサーバーのメンバー一覧に表示されるはずです。

#### ID を収集する

Discord で開発者モードを有効にし（**User Settings/ Advanced/ Developer Mode**）、次を行います:
- サーバーアイコンを右クリック: **Copy Server ID**
- 自分のアバターを右クリック: **Copy User ID**

#### サーバーメンバーからの DM を許可する

サーバーアイコンを右クリック/ **Privacy Settings**/ **Direct Messages** をオンに切り替えます。これにより、ボットがあなたに DM を送れるようになり、ペアリングステップに必要です。

#### Discord 用に OpenClaw を設定する

ボットトークンを環境変数として保存し、Discord を有効化し、トークンを参照し、サーバーをアローリストに追加する単一のパッチファイルを作成します。上記で収集した ID を使って `<server_id>` と `<user_id>` を置き換えてください。

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

> **この設定をエージェントに依頼することに頼らないでください。** サンドボックス化が有効な場合、エージェントはサンドボックス内から `~/.openclaw/openclaw.json` に書き込むことができません。代わりに、ホスト上で上記の CLI コマンドを使用してください。

新しいチャンネル設定を反映させるため、ゲートウェイを再起動します:

```bash
openclaw gateway run --bind loopback --port 18789
```

数秒以内に、ゲートウェイの出力に `logged in to discord as <bot-name>` と表示されるはずです。
#### Discordアカウントをペアリングする

Discordでボットにダイレクトメッセージを送信してください。短いペアリングコードが返信されます。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClawを実行しているマシンで承認します：
```bash
openclaw pairing approve discord <CODE>
```

> ペアリングコードは1時間で有効期限が切れます。

これで、Discordから直接エージェントとチャットし、タスクをローカルハードウェアにオフロードできるようになりました。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### オプションB：Telegram

TelegramはほとんどのユーザーにとってDiscordよりもシンプルで、サーバーも管理者権限も不要です。

#### Telegramボットを作成する

1. Telegramを開き、**@BotFather**にメッセージを送ります。
2. `/newbot`を送信し、指示に従ってください。渡されたボットトークンを保存しておきます。

#### Telegram用にOpenClawを設定する

トークンを環境変数として保存します：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

`~/.openclaw/openclaw.json`にチャンネル設定を追加します（またはダッシュボード経由でパッチを適用します）：

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

ゲートウェイを再起動し、Telegramでボットに何かメッセージを送信します。ペアリングを承認します：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

ペアリングコードは1時間で有効期限が切れます。これで、TelegramのDM経由でエージェントとチャットできるようになりました。

---

## 次のステップ

これで、エージェントはスマートフォンからコマンドを受け取り、ローカルマシン上で動作できるようになりました。ここでは、さらに試してみる価値のある3つの方向性を紹介します。

1. **株式市場サマライザー**：OpenClawをスケジュール設定し、一定間隔で金融APIからデータを取得し、ローカルモデルでその日の値動きを要約して、選択したチャンネル経由で毎朝ダイジェストをスマートフォンに送信します。

2. **ファインチューニングモニター**：TelegramやDiscordからリモートでトレーニングジョブを開始し、エージェントにトレーニングログを追跡させ、定期的に損失値、GPU使用率、ディスク使用量をスマートフォンに報告させます。トレーニングが停滞したりVRAMが急増したりした場合、マシンの前にいなくてもすぐに気付くことができます。

3. **ローカルVLMを使ったIOT**：玄関にカメラを向け、Lemonade上でビジョンモデルを実行し、OpenClawにオンデマンドまたはトリガーでフレームを分析させます。スマートフォンから「今日は荷物が届いた？」と尋ねると、自分のハードウェアから直接答えが返ってきます。

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