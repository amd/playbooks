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

🍋 **Lemonade** は、大規模言語モデル (LLM)、画像生成モデル、音声モデルを自分のハードウェア上で直接実行できる、オープンソースのローカル AI サーバーです。業界標準の **OpenAI API** を通じてモデルを公開するため、OpenAI 対応のアプリであれば、すぐに Lemonade を利用できるようになります。このプレイブックの最後までに、あなたは Lemonade を使ってモデルを自分のマシン上でローカルに実行できるようになります。

## このプレイブックで学べること

このプレイブックを終えると、次のことができるようになります。

* **Lemonade Server をインストール**し、正常に動作していることを確認する。
* **1 つのコマンドで LLM をダウンロードし、チャット**する。
* **Web UI を探索**し、ビジョン、音声認識 (speech-to-text)、画像生成などのさまざまなモダリティを試す。
* Vulkan と AMD ROCm™ ソフトウェアの間で**GPU バックエンドを切り替える**。
* OpenAI 互換 API を利用して、ローカル LLM を活用した**Python アプリを構築する**。
<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AI ハードウェア上で、Hybrid および FLM の実行モードを使用して、**AMD Neural Processing Unit (NPU) 上でモデルを実行する**。
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## 必要なソフトウェアのインストール

始める前に、以下がそろっていることを確認してください。

- **Windows 11**、またはサポートされている **Linux** ディストリビューション (Ubuntu 24.04 以降、Fedora、Debian) を実行している PC
- ステップ 1〜7 で使用するランタイムモデル (`Gemma-4-E2B-it-GGUF`、約 3 GB) には **16 GB の RAM** を推奨します。ステップ 6 でより大きなコード生成モデル (`Qwen3.5-35B-A3B-GGUF`、約 20 GB) を使用したい場合は **32 GB 以上**を推奨します。
- ダウンロードするモデルによって異なりますが、**約 4〜30 GB の空きディスク容量**が必要です。本ガイドで最大のモデルは約 20 GB です。
- **Python 3.10〜3.13** (Python アプリのセクションで使用します)
- インターネット接続 (有線または無線)
<!-- @device:halo_box,halo,stx,krk -->
- [任意] モデルを NPU 上で実行したい場合は、[Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) から最新ドライバーをインストールした AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme)
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
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
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

## 基本概念 — ローカル AI サーバーの仕組み

モデルを実行する前に、なぜこのような構成になっているのかを理解しておくと役立ちます。Lemonade は**ローカルモデルサーバー**であり、クラウドの AI サービスと同じように、AI モデルをメモリにロードし、HTTP 経由でアプリケーションに公開するプロセスです。

### なぜサーバーなのか?

| メリット | あなたにとっての意味 |
|---------|----------------------|
| **統合の簡素化** | アプリはハードウェア固有の C++ や Python ライブラリを扱う代わりに、単一の HTTP API とやり取りします。 |
| **モデルの共有** | 1 つのロード済みモデルが複数のアプリに同時に対応でき、重複したコピーで RAM を浪費することがありません。 |
| **クラウドからローカルへの移植性** | OpenAI のクラウド API 向けに書かれたコードは、URL を 1 つ変更するだけで Lemonade でも動作します。 |
| **関心の分離** | モデル管理、ストリーミング、耐障害性はサーバー側が処理するため、開発者はアプリ自体に集中できます。 |

### OpenAI API 標準

Lemonade は、ChatGPT、Azure OpenAI、その他数十のサービスで使われているのと同じインターフェースである **OpenAI API** を実装しています。会話モデルはシンプルです。

| ロール | 発言者 |
|------|---------------|
| **system** | モデルへの指示 (人格、制約、利用可能なツールなど) |
| **user** | 人間 (またはアプリケーション) からモデルへのメッセージ |
| **assistant** | モデルによって生成された応答 |

つまり、OpenAI をサポートするライブラリやアプリであれば、Lemonade Server が実行中に `http://localhost:13305/api/v1` を指すように設定するだけで Lemonade と通信できます。

## メインアクティビティ — はじめてのローカル AI チャット

LLM をダウンロードし、AI を完全に自分のマシン上で実行しながら会話してみましょう。

### ステップ 1: モデルのダウンロードと実行

Lemonade には、厳選されたモデルライブラリが付属しています。まずは、ビジョンサポートを含む、高性能でコンパクトなモデルである **Gemma-4-E2B-it** から始めましょう。ターミナルを開いて、次を実行します。

```
lemonade run Gemma-4-E2B-it-GGUF
```

この 1 つのコマンドで、次の 3 つのことが行われます。

1. まだダウンロードされていない場合、Hugging Face からモデル (約 3 GB) を**ダウンロード**します。(多少時間がかかる場合があります)
2. ポート 13305 で Lemonade Server プロセスを**開始**します。
3. モデルとすぐにチャットを始められるように、**Lemonade App を開きます**。


<!-- @os:windows -->
Windows では、Lemonade App が自動的に起動し、すぐにチャットを開始できます。`minimal.msi` パッケージをインストールした場合、アプリは含まれていません。チャットを開始するには、Web ブラウザを開いて `http://localhost:13305` にアクセスしてください。
<!-- @os:end -->

<!-- @os:linux -->
Linux では、ブラウザを開いて `http://localhost:13305` にアクセスすると、Web アプリにアクセスできます。
<!-- @os:end -->

質問を入力してみましょう。

```
What are three fun facts about lemons?
```

モデルはチャットウィンドウ内に直接応答します。**おめでとうございます! あなたは今、ローカルで大規模言語モデルを実行しています。**

![Lemonade App with Logs displayed](../../dependencies/assets/ChatwithLogs.png)

Lemonade App の Server Logs ペインでは、各応答後にモデルのパフォーマンスに関するテレメトリデータを確認できます。例:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### ステップ2:Webインターフェースとさまざまなモダリティを試す

LemonadeにはWebインターフェースが組み込まれており、以下のことができます。

- おなじみのチャットウィンドウで、ロードしたモデルと**対話**する
- Model Managerタブで**モデルを閲覧**する
- **新しいモデルをダウンロード**する(ワンクリックで)

WebUIの**Model Manager**タブを使って、RecipeまたはCategoryごとにモデルを閲覧しながら、さまざまなモダリティを切り替えてみましょう。

1. **ビジョン:** すでにロード済みの`Gemma-4-E2B-it-GGUF`モデルはビジョンに対応しています。チャットボックスに画像を貼り付けて、モデルにその説明を依頼してみてください。
2. **画像生成:** Imageカテゴリで、Model Managerから`SDXL-Turbo`などの画像モデルをダウンロードし、Lemonade Image Generatorを使ってプロンプトを入力し、ローカルで画像を生成します。
3. **音声:** Audioカテゴリで、音声テキスト変換が可能な`Whisper-Tiny`などの音声モデルをダウンロードします。音声の録音を提供することで、ローカルで文字起こしができます。テキスト読み上げには、Speechカテゴリにある`kokoro-v1`などのモデルを試してみてください。

![Lemonadeによるマルチモダリティ](../../dependencies/assets/multi_modality.png)

### ステップ3:別のバックエンドでモデルを試す

Lemonadeアプリでモデルにマウスオーバーすると、歯車アイコンが表示されます。これをクリックすると、使用したいバックエンドの選択を含め、モデルのオプションを選択できます。

デフォルトでは、LemonadeはGPUアクセラレーションにVulkanを使用します。対応しているAMDディスクリートGPUをお持ちの場合は、ROCmに切り替えることができます。

![Lemonadeのバックエンド選択](../../dependencies/assets/lemonademodeloptions.png)

インストール済みのバックエンドを管理するには、一番左の列にあるバックエンドボタンをクリックしてください。

または、次のコマンドを使用してバックエンドを指定することもできます。

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

環境変数`LEMONADE_LLAMACPP`に`vulkan`、`rocm`、`cpu`のいずれかの値を設定することで、デフォルトのバックエンドを設定することもできます。

---

## さらに深く理解する — Pythonを使ったAI搭載アプリの構築

ローカルAIサーバーの真の強みは、どのアプリケーションもわずか数行のコードで接続できることにあります。これを実証するために、小さいながらも実用的な**学習用フラッシュカード生成アプリ**を構築してみましょう。トピックを指定すると、フラッシュカードが生成され、インタラクティブに自分自身をテストできます。

### ステップ4:サーバーを起動する

Lemonadeサーバーが実行中であることを確認してください。通常、インストール後にバックグラウンドで自動的に起動します。確認するには、以下を実行してください。

```
lemonade status
```

`Server is running on port 13305`のようなメッセージが表示されるはずです。

サーバーが実行されていない場合は、Lemonadeアプリを開いて起動してください。デフォルトのポート**13305**を使用してください(トレイアイコンから確認または選択できます)。

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

コード生成用に別のモデルをダウンロードしましょう:`Qwen3.5-35B-A3B-GGUF`。これは大きな(約20 GB)高性能モデルで、32 GB以上のRAMを搭載したシステムに最適です。利用可能なRAMがそれより少ない場合は、代わりに`Qwen3.5-9B-GGUF`(約6 GB)を試してください。

UIからダウンロードするか、次を実行してください。
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

以下のプロンプトをLemonade Chat UIに入力して、シンプルなFlashcardアプリのコードを生成してください。

Pythonアプリの生成にはQwen3.5-35B-A3B-GGUF(コード記述に優れた大きなモデル)を使用し、アプリ自体は実行時にGemma-4-E2B-it-GGUF(すでにダウンロード済みの小さなモデル)を呼び出します。生成されたコードは、任意のファイルにコピーしてPythonで実行できます。

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

> **ヒント**:綿密なプロンプト作成と2モデルシステムの採用により、リソースと速度を最適化するという標準的なエンジニアリングのプラクティスに従っています。

便宜上、サンプル出力を[`flashcards.py`](assets/flashcards.py)として提供しています。お好みのディレクトリにダウンロードしてください。いずれにしても、これで実行可能なPythonファイルが手に入ったはずです。

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

**次のような結果が表示されるはずです:**

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

わずか150行程度のコードで、ローカルLLMを活用した完全に機能する学習ツールを構築できました。管理が必要なAPIキーもなく、使用料もかからず、データが自分のマシンから外部に出ることもありません。

> **重要なポイント:** `client = OpenAI(base_url=...) `の行だけが、このアプリをOpenAIのクラウドではなくLemonadeに結び付けている*唯一*の部分であることに注目してください。それ以外のコードは、OpenAI互換のサービスに対して書くコードとまったく同じです。OpenAI Pythonライブラリを使ったことがあるなら、Lemonadeでアプリを構築する方法はすでにご存知のはずです。

### このデモが示すこと

この小さなアプリは、いくつかの現実的な統合パターンを実践しています。

| パターン | 登場箇所 |
|---------|-----------------|
| **システムプロンプト** | `"system"`メッセージがLLMに構造化されたJSONの出力を指示する |
| **構造化出力** | アプリがLLMの応答をJSONとして解析し、フラッシュカードを構築する |
| **ステートレスなリクエスト** | `generate_flashcards()`の各呼び出しは独立している |
| **エラー処理** | `try/except`が、LLMの出力が有効なJSONでない場合を適切に処理する |

これらと同じパターンは、チャットボット、コードアシスタント、コンテンツ生成ツール、自動化ツールなど、あらゆるアプリケーションに応用できます。

#### ボーナスチャレンジ

* さらなる挑戦として、[こちら](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)で提供されている例を参考に、フラッシュカードをユーザーに読み上げる機能を追加してみてください。

---

<!-- @device:halo_box,halo,stx,krk -->
## NPUでモデルを実行する(オプション)

Ryzen AI 300/400/Max 300シリーズまたはZ2 Extremeをお使いの場合、デバイスにはAI処理専用に設計された専用チップである**ニューラル処理ユニット(NPU)**が搭載されています。NPUでモデルを実行すると、GPUを使用する場合よりも電力効率が高くなるため、バックグラウンドでのAIタスク、長時間のセッション、バッテリー駆動時の使用に最適です。

Lemonadeは3つのNPU実行モードをサポートしており、いずれも同一のOpenAI API背後で透過的に動作します。

| モード | 動作の仕組み | レシピ | モデル例 |
|------|-------------|--------|----------------|
| **ハイブリッド(NPU + iGPU)** | NPUがプロンプトを処理し、iGPUがトークンを生成 | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU単独** | 推論全体がNPU上で実行される | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | AMD XDNA2向けに最適化されたFastFlowLMエンジンをNPU上で使用 | FLM (`flm`) | qwen3.5-4b-FLM |

### 要件

- **AMD Ryzen AI 300/400シリーズまたはZ2シリーズ**プロセッサ
- **FLM**モデル向け:FLMランタイムはLemonadeアプリ内からインストールできるほか、FLMモデルの実行時にLemonadeが自動的にFLMランタイムをインストールします。FastFlowLMについて詳しくは[こちら](https://fastflowlm.com/docs/)をご覧ください。


### ステップ8:ハイブリッドモデルを実行する

ハイブリッドモデルは、速度と効率のバランスを取るために、処理をNPUとiGPUに分担させます。Lemonadeアプリで`Ryzen AI LLM`リストからモデル(例:`Qwen3-4B-Hybrid`)を選択するか、以下のコマンドで実行します。

```
lemonade run Qwen3-4B-Hybrid
```

Lemonadeは自動的にNPUを検出し、**Ryzen AI LLM**バックエンドをインストールします。

> **内部で何が起きているのか?** メッセージを送信すると、NPUがプロンプト全体を並列処理します(これを「prefill」と呼びます)。その後、iGPUが引き継ぎ、応答を1トークンずつ生成します(これを「decode」と呼びます)。このハイブリッドアプローチは、それぞれのチップの強みを活かします。

### ステップ9:FLMモデルを実行する

FastFlowLM(FLM)モデルは、AMDのXDNA2 NPUアーキテクチャ向けに特別に最適化されており、そのサイズに対して非常に高速に動作します。例えば、`FastFlowLM NPU`リストから`qwen3.5-4b-FLM`を選択するか、以下のコマンドを使用します。

<!-- @os:windows -->
Windowsで`FastFlowLM`を有効にするには:

* `Backends Manager`メニューを開きます。
* `FastFlowLM NPU`バックエンドカテゴリを見つけます。
* Install NPUをクリックします。
* インストールが完了すると、約36個のデフォルトモデルがFFLMドロップダウンメニューに表示されます。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade`アプリを初めて起動したとき、`FastFlowNPU`バックエンドはデフォルトでは有効になっていません。
ローカルアプリがインストールページを開き、セットアップ手順を案内します。

Linuxで`FastFlowLM`を有効にするには:

* `Lemonade`アプリを開きます。
* [公式FLM](https://lemonade-server.ai/flm_npu_linux.html)ドキュメントにアクセスし、お使いのLinuxディストリビューションを選択してFLMのインストール手順に従います。
* インストールページの指示に従ってbackportsを有効にします。
* [tagsページ](https://github.com/FastFlowLM/FastFlowLM/tags)から最新の`v0.9.x`リリースをダウンロードします。

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
* 推奨:`Lemonade App`を終了してから再度開き、変更を検出させます。
* 推奨:`Backends Manager`を開き、`FastFlowNPU` Backendの「Install」をクリックします。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
インストールが正常に完了すると、**Lemonade Desktop App**内の**Download Manager**で`flm:npu`が完了していることが確認できます。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
その後、利用可能なFFLMモデルの中から任意のものを選択し、NPUバックエンドを使い始めることができます。

特定のモデルについては、[modelsページ](https://fastflowlm.com/docs/models/qwen/)から目的のモデルをダウンロードし、ドキュメントに記載されているShellコマンドを使用して検証してください。
```
flm run qwen3.5-4b-FLM
```
または
```
lemonade run qwen3.5-4b-FLM
```

FLMモデルには、最も人気のあるアーキテクチャ(Gemma 3、Qwen 3、Llama 3、DeepSeek R1)が含まれており、1GB未満から13GB超まで幅広いサイズがあります。
Lemonadeは自動的にNPUを検出し、**FastFlowLM NPU**バックエンドをインストールします。

<!-- @os:windows -->
> **ヒント:** NPUの性能を最大限に引き出すには、ターボモードを有効にしてください。
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### モデルの切り替え

ステップ6のフラッシュカードアプリは、NPUモデルでも動作します。モデル名を変更するだけです。

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 次のステップ

これで、自分自身のハードウェア上でローカルAIサーバーが稼働するようになりました。次に進むべき方向は以下の通りです。

1. **お気に入りのアプリと接続する**:Lemonadeは[VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)、[その他多数](https://lemonade-server.ai/marketplace)とすぐに連携できます。

2. **さらに多くのモデルを探す**:コーディング、推論、ビジョンなどに最適化されたモデルを見つけるために、[モデルライブラリ](https://lemonade-server.ai/docs/server/server_models/)全体を調べてみてください。利用可能なモデルを確認するには、LemonadeアプリまたはLemonadeアプリまたは`lemonade list`を使用します。

3. **ROCm GPUアクセラレーションを有効にする**:サポート対象のAMD GPUをお持ちの場合は、ROCmバックエンドに切り替えてください:`lemonade config set llamacpp.backend=rocm`。[サポートされているAMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)を参照してください。

4. **完全なAPI仕様を読む**:Lemonadeは、チャット補完、埋め込み、音声文字起こし、画像生成、音声合成などをサポートしています。すべてのエンドポイントについては、[Server Spec](https://lemonade-server.ai/docs/server/server_spec/)を参照してください。

5. **貢献する**:Lemonadeはオープンソースです。[貢献ガイド](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)を確認し、[Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)を探してみてください。

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