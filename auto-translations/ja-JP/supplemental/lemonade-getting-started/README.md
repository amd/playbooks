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

🍋 **Lemonade** は、大規模言語モデル(LLM)、画像生成モデル、音声モデルを自分のハードウェア上で直接実行できるオープンソースのローカル AI サーバーです。業界標準の **OpenAI API** を通じてモデルを公開するため、OpenAI に対応したアプリであればそのまま Lemonade でも動作します。このプレイブックを終える頃には、Lemonade を使って自分のマシン上でモデルをローカル実行できるようになっています。

## このプレイブックで学べること

このプレイブックを完了すると、以下のことができるようになります:

* **Lemonade Server をインストール**し、正常に動作していることを確認する。
* 1 つのコマンドで **LLM をダウンロードしてチャット**する。
* **Web UI を探索**し、ビジョン、音声からテキストへの変換、画像生成などのさまざまなモダリティを試す。
* Vulkan と AMD ROCm™ ソフトウェアの間で**GPU バックエンドを切り替える**。
* OpenAI 互換 API を利用して、ローカル LLM を利用した **Python アプリを構築する**。
<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AI ハードウェア上で、Hybrid および FLM 実行モードを使用して **AMD Neural Processing Unit(NPU)上でモデルを実行する**。
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

始める前に、以下がそろっていることを確認してください:

- **Windows 11**、またはサポートされている **Linux** ディストリビューション(Ubuntu 24.04 以降、Fedora、Debian)を実行している PC
- 手順 1~7(`Gemma-4-E2B-it-GGUF`、約 3 GB)で使用するランタイムモデルには **16 GB の RAM** を推奨します。手順 6(`Qwen3.5-35B-A3B-GGUF`、約 20 GB)でより大きなコード生成モデルを使用したい場合は、**32 GB 以上**を推奨します。
- ダウンロードするモデルによって異なりますが、**約 4~30 GB の空きディスク容量**。このガイドで最も大きいモデルは約 20 GB です。
- **Python 3.10~3.13**(Python アプリのセクションで使用)
- インターネット接続(有線または無線)
<!-- @device:halo_box,halo,stx,krk -->
- [任意] NPU 上でモデルを実行したい場合は、[Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) から最新のドライバーをインストールした AMD XDNA 2 NPU(Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme)
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

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

## 中核となる概念 — ローカル AI サーバーの仕組み

モデルを実行する前に、なぜこのような仕組みになっているのかを理解しておく価値があります。Lemonade は**ローカルモデルサーバー**であり、AI モデルをメモリにロードし、クラウド AI サービスと同様に HTTP 経由でアプリケーションに公開するプロセスです。

### なぜサーバーなのか?

| メリット | あなたにとっての意味 |
|---------|----------------------|
| **統合の簡素化** | アプリはハードウェア固有の C++ や Python ライブラリを扱う代わりに、単一の HTTP API とやり取りします。 |
| **モデルの共有** | 1 つのロード済みモデルが複数のアプリに同時にサービスを提供でき、重複したコピーが RAM を消費することがありません。 |
| **クラウドからローカルへの移植性** | OpenAI のクラウド API 向けに書かれたコードは、URL を 1 つ変更するだけで Lemonade でも動作します。 |
| **関心の分離** | モデル管理、ストリーミング、フォールトトレランスはサーバー側で処理されるため、開発者はアプリ自体に集中できます。 |

### OpenAI API 標準

Lemonade は **OpenAI API** を実装しています。これは ChatGPT、Azure OpenAI、その他多数のサービスで使用されているのと同じインターフェースです。会話モデルはシンプルです:

| ロール | 発言者 |
|------|---------------|
| **system** | モデルへの指示(ペルソナ、制約、利用可能なツール) |
| **user** | 人間(またはアプリケーション)からモデルへのメッセージ |
| **assistant** | モデルによって生成された応答 |

つまり、OpenAI をサポートするライブラリやアプリであれば、Lemonade Server の実行中に `http://localhost:13305/api/v1` を指すように設定するだけで Lemonade と通信できます。

## メインアクティビティ — 初めてのローカル AI チャット

それでは LLM をダウンロードし、AI をすべて自分のマシン上で実行しながら会話してみましょう。

### 手順 1: モデルのダウンロードと実行

Lemonade には厳選されたモデルライブラリが付属しています。まずは、ビジョンサポートを含む、高性能かつコンパクトなモデルである **Gemma-4-E2B-it** から始めましょう。ターミナルを開いて以下を実行します:

```
lemonade run Gemma-4-E2B-it-GGUF
```

この 1 つのコマンドは次の 3 つのことを行います:

1. モデル(約 3 GB)がまだダウンロードされていない場合、Hugging Face から**ダウンロード**します。(時間がかかる場合があります)
2. ポート 13305 で Lemonade Server プロセスを**起動**します。
3. モデルとすぐにチャットを始められるように、**Lemonade App を開きます**。


<!-- @os:windows -->
Windows では、Lemonade App が自動的に起動し、すぐにチャットを開始できます。`minimal.msi` パッケージをインストールした場合、アプリは含まれていません。チャットを開始するには、Web ブラウザを開いて `http://localhost:13305` にアクセスしてください。
<!-- @os:end -->

<!-- @os:linux -->
Linux では、ブラウザを開いて `http://localhost:13305` にアクセスし、Web アプリにアクセスします。
<!-- @os:end -->

質問を入力してみてください:

```
What are three fun facts about lemons?
```

モデルはチャットウィンドウ内で直接応答します。**おめでとうございます!大規模言語モデルをローカルで実行しています。**

![ログを表示した Lemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade App の Server Logs ペインでは、各応答の後にモデルのパフォーマンスに関するテレメトリデータを確認できます。例:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### ステップ2: Webインターフェースとさまざまなモダリティを試す

Lemonadeには組み込みのWebインターフェースが搭載されており、以下のことができます。

- おなじみのチャットウィンドウで、ロードされたモデルと**対話する**
- Model Managerタブで**モデルを閲覧する**
- ワンクリックで**新しいモデルをダウンロードする**

Web UIの**Model Manager**タブを使って、RecipeまたはCategoryでモデルを閲覧しながら、さまざまなモダリティを切り替えてみましょう。

1. **Vision:** すでにロード済みの`Gemma-4-E2B-it-GGUF`モデルはvisionに対応しています。チャットボックスに画像を貼り付けて、モデルにその画像を説明させてみましょう。
2. **画像生成:** ImageカテゴリでModel Managerから`SDXL-Turbo`のような画像モデルをダウンロードし、Lemonade Image Generatorを使ってプロンプトを入力し、ローカルで画像を生成しましょう。
3. **音声:** Audioカテゴリで`Whisper-Tiny`のような音声モデルをダウンロードすると、音声からテキストへの変換ができます。音声の録音データを与えると、ローカルで文字起こしされます。テキストから音声への変換には、Speechカテゴリの`kokoro-v1`などのモデルを試してみてください。

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### ステップ3: 異なるバックエンドでモデルを試す

Lemonade Appでモデルの上にカーソルを合わせると、歯車アイコンが表示されます。これをクリックすると、目的のバックエンドの選択を含む、モデルに関するオプションを選択できます。

デフォルトでは、LemonadeはGPUアクセラレーションにVulkanを使用します。対応しているAMDディスクリートGPUをお持ちの場合は、ROCmに切り替えることができます。

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

インストール済みのバックエンドを管理するには、一番左の列にあるバックエンドボタンをクリックします。

または、以下のコマンドを使用してバックエンドを指定することもできます。

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

環境変数`LEMONADE_LLAMACPP`を使って、デフォルトのバックエンドを設定することもできます。値には`vulkan`、`rocm`、`cpu`のいずれかを指定します。

---

## さらに深く — Pythonを使ってAI搭載アプリを構築する

ローカルAIサーバーの真の力は、どんなアプリケーションでも、わずか数行のコードでそれに接続できるという点にあります。これを実証するために、小さいながらも実際に機能する**学習用フラッシュカード生成ツール**を作ってみましょう。トピックを入力すると、フラッシュカードが生成され、対話形式で自分の理解度をテストできます。

### ステップ4: サーバーを起動する

Lemonadeサーバーが稼働していることを確認しましょう。インストール後、通常はバックグラウンドで自動的に起動します。確認するには、次を実行します。

```
lemonade status
```

`Server is running on port 13305`のようなメッセージが表示されるはずです。

サーバーが動作していない場合は、Lemonadeアプリを開いて起動してください。デフォルトのポート**13305**を使用します（トレイアイコンから確認または選択できます）。

### ステップ5: OpenAI Python Clientをインストールする

ターミナルでvenvを作成し、次のコマンドを使ってOpenAI Python Clientをインストールします。
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

### ステップ6: フラッシュカードアプリを構築する

コード生成用に別のモデル`Qwen3.5-35B-A3B-GGUF`をダウンロードしましょう。これは大きな（約20GB）高性能モデルで、32GB以上のRAMを搭載したシステムに最適です。利用可能なRAMがそれより少ない場合は、代わりに`Qwen3.5-9B-GGUF`（約6GB）を試してください。

UIからダウンロードするか、以下を実行してください。
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

シンプルなFlashcardアプリのコードを生成するために、以下のプロンプトをLemonade Chat UIに入力してください。

Pythonアプリを生成するにはQwen3.5-35B-A3B-GGUF（コード作成が得意なより大きなモデル）を使用し、アプリ自体は実行時にGemma-4-E2B-it-GGUF（すでにダウンロード済みの小さなモデル）を呼び出します。生成されたコードは、任意のファイルにコピーしてPythonで実行できます。

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

> **ヒント**: 綿密なプロンプト作成と、リソースと速度を最適化するための2モデル方式を採用することで、標準的なエンジニアリングのプラクティスに従っています。

参考として、サンプル出力を[`flashcards.py`](assets/flashcards.py)として提供しています。お好きなディレクトリにダウンロードしてご利用ください。いずれの方法でも、これで実行可能なPythonファイルが手に入るはずです。

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


### ステップ7: 生成されたコードを実行する

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

約150行のコードで、ローカルLLMを活用した本格的な学習ツールが完成しました。管理するAPIキーもなく、利用料金も発生せず、データが一切あなたのマシンから出ることもありません。

> **重要なポイント:** `client = OpenAI(base_url=...) `という行だけが、このアプリをOpenAIのクラウドではなくLemonadeに結び付けている*唯一*の部分であることに注目してください。それ以外のコードは、任意のOpenAI互換サービスに対して書くコードとまったく同じです。OpenAI Pythonライブラリを使ったことがあれば、Lemonadeでアプリを構築する方法はすでに理解していることになります。

### これが示していること

この小さなアプリは、実際の統合パターンをいくつか実践しています。

| パターン | 登場箇所 |
|---------|-----------------|
| **システムプロンプト** | `"system"`メッセージがLLMに構造化されたJSONを出力するよう指示します |
| **構造化出力** | アプリはLLMのレスポンスをJSONとしてパースし、フラッシュカードを構築します |
| **ステートレスなリクエスト** | 各`generate_flashcards()`呼び出しは独立しています |
| **エラー処理** | `try/except`により、LLMの出力が有効なJSONでない場合にも適切に対処します |

これらと同様のパターンは、チャットボット、コードアシスタント、コンテンツ生成ツール、自動化ツールなど、あらゆるアプリケーションに応用できます。

#### ボーナスチャレンジ

* さらなる挑戦として、[こちら](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)で提供されている例を参考に、フラッシュカードをユーザーに読み上げる機能を追加するようアプリを更新してみてください。

---

<!-- @device:halo_box,halo,stx,krk -->
## NPU での実行(オプション)

Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme をお使いの場合、お使いのデバイスには**Neural Processing Unit(NPU)** が内蔵されています。これは AI ワークロード専用に設計された専用チップです。NPU 上でモデルを実行すると、GPU を使用する場合よりも電力効率が高くなるため、バックグラウンドでの AI タスク、長時間のセッション、バッテリー駆動時の利用に最適です。

Lemonade は 3 種類の NPU 実行モードをサポートしており、いずれも同じ OpenAI API の背後で透過的に動作します。

| モード | 動作方法 | レシピ | モデル例 |
|------|-------------|--------|----------------|
| **Hybrid(NPU + iGPU)** | NPU がプロンプトを処理し、iGPU がトークンを生成 | OGA(`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU のみ** | 推論全体を NPU 上で実行 | Ryzen AI LLM(`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | AMD XDNA2 向けに最適化された、NPU 上で動作する FastFlowLM エンジンを使用 | FLM(`flm`) | qwen3.5-4b-FLM |

### 要件

- **AMD Ryzen AI 300/400 シリーズまたは Z2 シリーズ**プロセッサー
- **FLM** モデルの場合:FLM ランタイムは Lemonade アプリ内からインストールできます。また、FLM モデルの実行時に Lemonade が自動的に FLM ランタイムをインストールします。FastFlowLM の詳細については、[こちら](https://fastflowlm.com/docs/)をご覧ください。


### ステップ 8:Hybrid モデルを実行する

Hybrid モデルは、速度と効率の良好なバランスを実現するために、NPU と iGPU の間で処理を分担します。Lemonade App で `Ryzen AI LLM` リストからモデルを選択します(例:`Qwen3-4B-Hybrid`)。または、次のコマンドを使用して実行します。

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade はお使いの NPU を自動的に検出し、**Ryzen AI LLM** バックエンドをインストールします。

> **内部で何が起きているのか?** メッセージを送信すると、NPU がプロンプト全体を並列に処理します(これを「プリフィル」と呼びます)。その後、iGPU が引き継ぎ、応答を 1 トークンずつ生成します(これを「デコード」と呼びます)。この Hybrid アプローチにより、それぞれのチップの強みを活かすことができます。

### ステップ 9:FLM モデルを実行する

FastFlowLM(FLM)モデルは、AMD の XDNA2 NPU アーキテクチャ向けに特別に最適化されており、そのサイズの割に非常に高速に動作します。たとえば、`FastFlowLM NPU` リストから `qwen3.5-4b-FLM` を選択するか、次のコマンドを使用します。

<!-- @os:windows -->
Windows で `FastFlowLM` を有効にするには:

* `Backends Manager` メニューを開きます。
* `FastFlowLM NPU` バックエンドカテゴリを見つけます。
* Install NPU をクリックします。
* インストールが完了すると、約 36 個のデフォルトモデルが FFLM ドロップダウンメニューに表示されます。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` アプリを初めて起動したとき、`FastFlowNPU` バックエンドはデフォルトでは有効になっていません。
ローカルアプリがインストールページを開き、セットアップの手順を案内します。

Linux で `FastFlowLM` を有効にするには:

* `Lemonade` アプリを開きます。
* [公式 FLM](https://lemonade-server.ai/flm_npu_linux.html) のドキュメントにアクセスし、お使いの Linux ディストリビューションを選択して FLM のインストール手順に従います。
* インストールページの案内に従って backports を有効にします。
* [tags ページ](https://github.com/FastFlowLM/FastFlowLM/tags)から最新の `v0.9.x` リリースをダウンロードします。'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platform の場合は、必ず Debian 13 を選択してください。
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* ダウンロードした `.deb` パッケージをインストールします。
* 推奨:`Lemonade App` を終了し、再度開いて変更が検出されるようにしてください。
* 推奨:`Backends Manager` を開き、`FastFlowNPU` Backend の Install をクリックします。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
インストールが正常に完了すると、**Lemonade Desktop App** 内の**ダウンロードマネージャー**で `flm:npu` が完了したことを確認できます。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
その後、利用可能な FFLM モデルの中から任意のものを選択し、NPU バックエンドを使い始めることができます。

特定のモデルについては、[モデルページ](https://fastflowlm.com/docs/models/qwen/)から目的のモデルをダウンロードし、ドキュメントに記載されている Shell コマンドを使用して検証してください。
```
flm run qwen3.5-4b-FLM
```
または
```
lemonade run qwen3.5-4b-FLM
```
経由で行います。
FLM モデルには、最も人気のあるアーキテクチャ(Gemma 3、Qwen 3、Llama 3、DeepSeek R1)がいくつか含まれており、サイズは 1 GB 未満から 13 GB 超まで幅広くあります。
Lemonade はお使いの NPU を自動的に検出し、**FastFlowLM NPU** バックエンドをインストールします。

<!-- @os:windows -->
> **ヒント:** NPU の性能を最大限に引き出すには、ターボモードを有効にしてください。
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### モデルの切り替え

ステップ 6 のフラッシュカードアプリは NPU モデルでも動作します。モデル名を変更するだけです。

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 次のステップ

これで、お使いのハードウェア上でローカル AI サーバーが稼働するようになりました。次に進む先をいくつかご紹介します。

1. **お気に入りのアプリと連携する**:Lemonade は、[VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)、[その他多数](https://lemonade-server.ai/marketplace)とすぐに連携して動作します。

2. **さらに多くのモデルを探す**:コーディング、推論、視覚(ビジョン)などに最適化されたモデルを探すには、[モデルライブラリ](https://lemonade-server.ai/docs/server/server_models/)全体をご覧ください。利用可能なモデルを確認するには、Lemonade App または `lemonade list` を使用してください。

3. **ROCm GPU アクセラレーションを利用する**:サポートされている AMD GPU をお持ちの場合は、ROCm バックエンドに切り替えます:`lemonade config set llamacpp.backend=rocm`。[サポートされている AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)をご覧ください。

4. **API 仕様全体を確認する**:Lemonade はチャット補完、埋め込み(embeddings)、音声文字起こし、画像生成、音声合成(text-to-speech)などをサポートしています。すべてのエンドポイントについては [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) をご覧ください。

5. **貢献する**:Lemonade はオープンソースです。[コントリビューションガイド](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)を確認し、[Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)を探してみてください。

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