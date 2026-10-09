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

🍋 **Lemonade** は、大規模言語モデル(LLM)、画像生成モデル、音声モデルを自分のハードウェア上で直接実行できる、オープンソースのローカル AI サーバーです。モデルは業界標準の **OpenAI API** を通じて公開されるため、OpenAI 対応のあらゆるアプリがすぐに Lemonade でも利用可能になります。このプレイブックの終わりまでに、Lemonade を使って自分のマシン上でモデルをローカルで実行できるようになります。

## 学習内容

このプレイブックを終える頃には、以下ができるようになります。

* **Lemonade Server をインストール**し、正常に動作していることを確認する。
* 1 つのコマンドで**LLM をダウンロードしてチャットする**。
* **Web UI を探索**し、ビジョン、音声テキスト変換、画像生成などさまざまなモダリティを試す。
* Vulkan と AMD ROCm™ ソフトウェアの間で**GPU バックエンドを切り替える**。
* OpenAI 互換 API を使ってローカル LLM を活用した**Python アプリを構築**する。
<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AI ハードウェア上で、Hybrid および FLM 実行モードを使用して**AMD Neural Processing Unit (NPU) 上でモデルを実行**する。
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

始める前に、以下を用意してください。

- **Windows 11** またはサポートされている **Linux** ディストリビューション(Ubuntu 24.04+、Fedora、Debian)を実行する PC
- ステップ 1〜7 で使用するランタイムモデル(`Gemma-4-E2B-it-GGUF`、約 3 GB)には **16 GB の RAM** を推奨します。ステップ 6 でより大規模なコード生成モデル(`Qwen3.5-35B-A3B-GGUF`、約 20 GB)を使用したい場合は **32 GB 以上**を推奨します。
- ダウンロードするモデルによって異なりますが、**約 4〜30 GB の空きディスク容量**。本ガイドで最大のモデルは約 20 GB です。
- **Python 3.10〜3.13**(Python アプリのセクションで使用)
- インターネット接続(有線または無線)
<!-- @device:halo_box,halo,stx,krk -->
- [オプション] NPU 上でモデルを実行したい場合は、[Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) から最新のドライバーをインストールした AMD XDNA 2 NPU(Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme)
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=300 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## コアコンセプト — ローカル AI サーバーの仕組み

モデルを実行する前に、なぜこのような構成になっているのかを理解しておくと役立ちます。Lemonade は**ローカルモデルサーバー**であり、AI モデルをメモリにロードし、クラウド AI サービスと同じように HTTP 経由でアプリケーションに公開するプロセスです。

### なぜサーバーなのか?

| メリット | あなたにとっての意味 |
|---------|----------------------|
| **統合の簡素化** | アプリはハードウェア固有の C++ や Python のライブラリを扱う代わりに、単一の HTTP API とやり取りします。 |
| **モデルの共有** | 1 つのロード済みモデルが複数のアプリに同時にサービスを提供できるため、重複したコピーが RAM を消費することがありません。 |
| **クラウドからローカルへの移植性** | OpenAI のクラウド API 向けに書かれたコードは、URL を 1 つ変更するだけで Lemonade でも動作します。 |
| **関心の分離** | モデル管理、ストリーミング、フォールトトレランスはサーバーが処理するため、開発者はアプリに集中できます。 |

### OpenAI API 標準

Lemonade は、ChatGPT、Azure OpenAI、その他多数のサービスで使用されているものと同じインターフェースである**OpenAI API** を実装しています。会話モデルはシンプルです。

| ロール | 話している相手 |
|------|---------------|
| **system** | モデルへの指示(ペルソナ、制約、利用可能なツール) |
| **user** | 人間(またはアプリケーション)からモデルへのメッセージ |
| **assistant** | モデルによって生成された応答 |

つまり、OpenAI をサポートするライブラリやアプリであれば、Lemonade Server の実行中に `http://localhost:13305/api/v1` を指定するだけで Lemonade と通信できます。

## メインアクティビティ — 初めてのローカル AI チャット

LLM をダウンロードし、AI を完全に自分のマシン上で実行しながら会話してみましょう。

### ステップ 1: モデルのダウンロードと実行

Lemonade には厳選されたモデルライブラリが付属しています。まずは、ビジョンサポートを含む高性能でコンパクトなモデルである **Gemma-4-E2B-it** から始めましょう。ターミナルを開いて以下を実行してください。

```
lemonade run Gemma-4-E2B-it-GGUF
```

この 1 つのコマンドで、次の 3 つのことが行われます。

1. モデル(約 3 GB)がまだダウンロードされていない場合、Hugging Face から**ダウンロード**します。(時間がかかる場合があります)
2. ポート 13305 で Lemonade Server プロセスを**開始**します。
3. モデルとのチャットを開始できるように Lemonade App を**開きます**。


<!-- @os:windows -->
Windows では、Lemonade App が自動的に起動し、すぐにチャットを開始できます。`minimal.msi` パッケージをインストールした場合、アプリは含まれていません。チャットを開始するには、Web ブラウザを開いて `http://localhost:13305` にアクセスしてください。
<!-- @os:end -->

<!-- @os:linux -->
Linux では、ブラウザを開いて `http://localhost:13305` にアクセスすると Web アプリにアクセスできます。
<!-- @os:end -->

質問を入力してみましょう。

```
What are three fun facts about lemons?
```

モデルはチャットウィンドウ内で直接応答します。**おめでとうございます! あなたは大規模言語モデルをローカルで実行しています。**

![ログを表示した Lemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade App の Server Logs ペインでは、各応答後にモデルのパフォーマンスに関するテレメトリデータを確認できます。例えば次のようになります。

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### ステップ2:Webインターフェースとさまざまなモダリティを試す

Lemonadeには、以下のことができる組み込みのWebインターフェースが用意されています。

- おなじみのチャットウィンドウでロードされたモデルと**対話する**
- Model Managerタブで**モデルを閲覧する**
- ワンクリックで**新しいモデルをダウンロードする**

WebUIの**Model Manager**タブを使って、RecipeまたはCategoryでモデルを閲覧しながら、さまざまなモダリティを切り替えてみましょう。

1. **Vision:** すでにロード済みの`Gemma-4-E2B-it-GGUF`モデルはvisionに対応しています。チャットボックスに画像を貼り付けて、モデルにその画像を説明させてみましょう。
2. **画像生成:** ImageカテゴリでModel Managerから`SDXL-Turbo`などの画像モデルをダウンロードし、Lemonade Image Generatorでプロンプトを入力してローカルで画像を生成します。
3. **音声:** Audioカテゴリで`Whisper-Tiny`などの音声モデルをダウンロードすると、音声からテキストへの変換ができます。音声の録音データを提供すると、ローカルで文字起こしできます。テキストから音声への変換については、Speechカテゴリにある`kokoro-v1`などのモデルを試してみてください。

![Lemonadeによるマルチモダリティ](../../dependencies/assets/multi_modality.png)

### ステップ3:別のバックエンドでモデルを試す

Lemonade Appでモデルにマウスオーバーすると、歯車アイコンが表示されます。このアイコンをクリックすると、使用したいバックエンドの選択など、モデルに関するオプションを選択できます。

デフォルトでは、LemonadeはGPUアクセラレーションにVulkanを使用します。対応するAMDディスクリートGPUをお持ちの場合は、ROCmに切り替えることができます。

![Lemonadeのバックエンド選択](../../dependencies/assets/lemonademodeloptions.png)

インストール済みのバックエンドを管理するには、一番左の列にあるバックエンドボタンをクリックします。

または、次のコマンドを使用してバックエンドを指定することもできます。

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

環境変数`LEMONADE_LLAMACPP`に`vulkan`、`rocm`、`cpu`のいずれかの値を設定することで、デフォルトのバックエンドを設定することもできます。

---

## さらに深く理解する — PythonでAI搭載アプリを構築する

ローカルAIサーバーの真の強みは、わずか数行のコードで任意のアプリケーションから接続できる点にあります。それを実証するために、トピックを与えるとフラッシュカードを生成し、対話形式で自己テストできる、小さくても機能的な**学習用フラッシュカードジェネレーター**を構築してみましょう。

### ステップ4:サーバーを起動する

Lemonadeサーバーが実行中であることを確認します。通常、インストール後にバックグラウンドで自動的に起動します。確認するには、次を実行します。

```
lemonade status
```

`Server is running on port 13305`のようなメッセージが表示されるはずです。

サーバーが実行されていない場合は、Lemonadeアプリを開いて起動してください。デフォルトのポート**13305**を使用します(トレイアイコンから確認または選択できます)。

### ステップ5:OpenAI Pythonクライアントをインストールする

ターミナルでvenvを作成し、次のコマンドを使用してOpenAI Pythonクライアントをインストールします。
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### ステップ6:フラッシュカードアプリを構築する

コード生成のために別のモデル`Qwen3.5-35B-A3B-GGUF`をダウンロードしましょう。これは大規模(約20GB)で高性能なモデルで、32GB以上のRAMを搭載したシステムに最適です。利用可能なRAMが少ない場合は、代わりに`Qwen3.5-9B-GGUF`(約6GB)を試してください。

UIからダウンロードするか、次を実行します。
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

シンプルなFlashcardアプリのコードを生成するために、次のプロンプトをLemonade Chat UIに入力してください。

Pythonアプリを生成するためにQwen3.5-35B-A3B-GGUF(コード記述に優れたより大規模なモデル)を使用し、アプリ自体は実行時にGemma-4-E2B-it-GGUF(すでにダウンロード済みの小規模モデル)を呼び出します。生成されたコードは、お好みのファイルにコピーしてPythonで実行できます。

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **ヒント**:徹底したプロンプト作成と、リソースと速度を最適化するための2モデルシステムの採用により、標準的なエンジニアリングのベストプラクティスに従っています。

便宜上、サンプル出力を[`flashcards.py`](assets/flashcards.py)として提供しています。お好みのディレクトリにダウンロードしてください。いずれにせよ、これで実行可能なPythonファイルが手に入ったはずです。

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### ステップ7:生成されたコードを実行する

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**次のような表示が確認できるはずです。**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

約150行のコードで、ローカルLLMを活用した完全に機能する学習ツールを構築できました。管理が必要なAPIキーも、利用料金も発生せず、データがマシンから外に出ることもありません。

> **重要なポイント:** `client = OpenAI(base_url=...) `の行だけが、このアプリをOpenAIのクラウドではなくLemonadeにつなげている*唯一*の部分であることに注目してください。それ以外のコードは、OpenAI互換の任意のサービスに対して書くものとまったく同じです。OpenAI Pythonライブラリを使ったことがあるなら、Lemonadeを使ったアプリの構築方法はすでに理解していることになります。

### これが示していること

この小さなアプリは、実際のいくつかの統合パターンを実践しています。

| パターン | 登場箇所 |
|---------|-----------------|
| **システムプロンプト** | `"system"`メッセージがLLMに構造化されたJSONを出力するよう指示する |
| **構造化された出力** | アプリがLLMの応答をJSONとして解析し、フラッシュカードを構築する |
| **ステートレスなリクエスト** | `generate_flashcards()`の各呼び出しは独立している |
| **エラーハンドリング** | `try/except`が、LLMの出力が有効なJSONでない場合を適切に処理する |

これらと同じパターンは、チャットボット、コードアシスタント、コンテンツ生成ツール、自動化ツールなど、あらゆるアプリケーションに応用できます。

#### ボーナスチャレンジ

* さらなるチャレンジとして、[こちら](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)で提供されている例を参考に、フラッシュカードをユーザーに読み上げる機能を追加してみてください。

---

<!-- @device:halo_box,halo,stx,krk -->
# NPUでモデルを実行する(オプション)

Ryzen AI 300/400/Max 300シリーズまたはZ2 Extremeをお使いの場合、デバイスにはAI専用に設計された専用チップである**ニューラル処理ユニット(NPU)**が搭載されています。NPUでモデルを実行することは、GPUを使用するよりも電力効率が高いため、バックグラウンドでのAIタスク、長時間のセッション、バッテリー駆動での使用に最適です。

Lemonadeは3つのNPU実行モードをサポートしており、いずれも同じOpenAI APIの背後で透過的に動作します。

| モード | 動作方法 | レシピ | モデル例 |
|------|-------------|--------|----------------|
| **ハイブリッド (NPU + iGPU)** | NPUがプロンプトを処理し、iGPUがトークンを生成 | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU専用** | 推論全体がNPU上で実行 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | AMD XDNA2向けに最適化された、NPU上のFastFlowLMエンジンを使用 | FLM (`flm`) | qwen3.5-4b-FLM |

### 要件

- **AMD Ryzen AI 300/400シリーズまたはZ2シリーズ**プロセッサ
- **FLM**モデルの場合: FLMランタイムはLemonadeアプリ内からインストールできます。また、FLMモデルを実行する際にLemonadeが自動的にFLMランタイムをインストールします。FastFlowLMの詳細については、[こちら](https://fastflowlm.com/docs/)を参照してください。


### ステップ8: ハイブリッドモデルを実行する

ハイブリッドモデルは、速度と効率のバランスを良くするためにNPUとiGPUの間で処理を分担します。Lemonadeアプリで、`Ryzen AI LLM`リストからモデル(例: `Qwen3-4B-Hybrid`)を選択するか、以下のコマンドを使用して実行します。

```
lemonade run Qwen3-4B-Hybrid
```

Lemonadeは自動的にNPUを検出し、**Ryzen AI LLM**バックエンドをインストールします。

> **内部で何が起きているのか?** メッセージを送信すると、NPUがプロンプト全体を並列処理します(これは「プリフィル」と呼ばれます)。その後、iGPUが引き継ぎ、応答を1トークンずつ生成します(これは「デコード」と呼ばれます)。このハイブリッドアプローチは、それぞれのチップの強みを活かします。

### ステップ9: FLMモデルを実行する

FastFlowLM (FLM) モデルは、AMDのXDNA2 NPUアーキテクチャに特化して最適化されており、そのサイズにしては非常に高速になり得ます。例えば、`FastFlowLM NPU`リストから`qwen3.5-4b-FLM`を選択するか、以下のコマンドを使用します。

<!-- @os:windows -->
Windowsで`FastFlowLM`を有効にするには:

* `Backends Manager`メニューを開きます。
* `FastFlowLM NPU`バックエンドのカテゴリを見つけます。
* Install NPUをクリックします。
* インストールが完了すると、約36個のデフォルトモデルがFFLMドロップダウンメニューで利用できるようになります。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade`アプリを初めて起動したとき、`FastFlowNPU`バックエンドはデフォルトでは有効になっていません。
ローカルアプリがインストールページを開き、セットアップを案内します。

Linuxで`FastFlowLM`を有効にするには:

* `Lemonade`アプリを開きます。
* [公式FLM](https://lemonade-server.ai/flm_npu_linux.html)ドキュメントにアクセスし、お使いのLinuxディストリビューションを選択してFLMのインストール手順に従います。
* インストールページの指示に従ってbackportsを有効にします。
* [タグページ](https://github.com/FastFlowLM/FastFlowLM/tags)から最新の`v0.9.x`リリースをダウンロードします。

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platformの場合は、必ずDebian 13を選択してください。
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* ダウンロードした`.deb`パッケージをインストールします。
* 推奨: `Lemonade App`を終了し、再度開いて変更が検出されるようにします。
* 推奨: `Backends Manager`を開き、`FastFlowNPU`バックエンドのInstallをクリックします。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
インストールが成功すると、**Lemonade Desktop App**内の**Download Manager**で`flm:npu`が完了したことが表示されるはずです。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
その後、利用可能なFFLMモデルのいずれかを選択し、NPUバックエンドの使用を開始できます。

特定のモデルについては、[モデルページ](https://fastflowlm.com/docs/models/qwen/)から希望するモデルをダウンロードし、ドキュメントに記載されているShellコマンドを使用して検証してください。
```
flm run qwen3.5-4b-FLM
```
または
```
lemonade run qwen3.5-4b-FLM
```
を使用します
FLMモデルには、最も人気のあるアーキテクチャ(Gemma 3、Qwen 3、Llama 3、DeepSeek R1)の一部が含まれており、サイズは1GB未満から13GB以上まで様々です。
Lemonadeは自動的にNPUを検出し、**FastFlowLM NPU**バックエンドをインストールします。

<!-- @os:windows -->
> **ヒント:** NPUのパフォーマンスを最大限に引き出すには、ターボモードを有効にしてください:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### モデルの切り替え

ステップ6のフラッシュカードアプリはNPUモデルでも動作します。モデル名を変更するだけです。

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 次のステップ

これで、ご自身のハードウェア上でローカルAIサーバーが稼働しています。次に進むべき内容は以下の通りです。

1. **お気に入りのアプリを接続する**: Lemonadeは[VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)、そして[その他多数](https://lemonade-server.ai/marketplace)とそのまま連携します。

2. **さらに多くのモデルを閲覧する**: コーディング、推論、ビジョンなどに最適化されたモデルを見つけるために、[モデルライブラリ](https://lemonade-server.ai/docs/server/server_models/)全体を探索してください。Lemonadeアプリまたは`lemonade list`を使用して、利用可能なモデルを確認できます。

3. **ROCm GPUアクセラレーションを有効にする**: サポートされているAMD GPUをお持ちの場合は、ROCmバックエンドに切り替えてください: `lemonade config set llamacpp.backend=rocm`。[サポートされているAMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)を参照してください。

4. **完全なAPI仕様を読む**: Lemonadeはチャット補完、エンベディング、音声文字起こし、画像生成、テキスト読み上げなどをサポートしています。各エンドポイントについては[サーバー仕様](https://lemonade-server.ai/docs/server/server_spec/)を参照してください。

5. **貢献する**: Lemonadeはオープンソースです。[貢献ガイド](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)を確認し、[Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)を探してみてください。

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