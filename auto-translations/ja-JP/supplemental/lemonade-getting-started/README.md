<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub がレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要

🍋 **Lemonade** は、大規模言語モデル（LLM）、画像生成モデル、音声モデルを自分のハードウェア上で直接実行できるオープンソースのローカル AI サーバーです。業界標準の **OpenAI API** を通じてモデルを公開するため、OpenAI と連携するアプリはすべて Lemonade でも即座に動作します。このプレイブックを終える頃には、Lemonade を使ってご自身のマシン上でモデルをローカル実行できるようになります。

## 学習内容

このプレイブックを終えると、以下のことができるようになります：

* **Lemonade Server をインストール**し、動作を確認する。
* **単一コマンドで LLM をダウンロードしてチャット**する。
* **Web UI を探索**し、ビジョン、音声認識、画像生成などのさまざまなモダリティを試す。
* **GPU バックエンドを切り替える**（Vulkan と AMD ROCm™ ソフトウェアの間）。
* **OpenAI 互換 API を使用して、ローカル LLM を活用した Python アプリを構築**する。
<!-- @device:halo_box,halo,stx,krk -->
* **AMD Neural Processing Unit（NPU）上でモデルを実行する**（AMD Ryzen™ AI ハードウェア上で Hybrid および FLM 実行モードを使用）。
<!-- @device:end -->

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

始める前に、以下を確認してください：

- **Windows 11** またはサポートされている **Linux** ディストリビューション（Ubuntu 24.04 以降、Fedora、Debian）を実行している PC
- ステップ 1〜7 で使用するランタイムモデル（`Gemma-4-E2B-it-GGUF`、約 3 GB）には **16 GB の RAM** を推奨。ステップ 6 の大規模コード生成モデル（`Qwen3.5-35B-A3B-GGUF`、約 20 GB）を使用する場合は **32 GB 以上**を推奨。
- **約 4〜30 GB の空きディスク容量**（ダウンロードするモデルによって異なります）。このガイドで最大のモデルは約 20 GB です。
- **Python 3.10〜3.13**（Python アプリのセクションで使用）
- インターネット接続（有線または無線）
<!-- @device:halo_box,halo,stx,krk -->
- [オプション] NPU 上でモデルを実行したい場合は、AMD XDNA 2 NPU（Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme）と、[Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) からインストールした最新ドライバーが必要です。
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

モデルを実行する前に、なぜこのような構成になっているのかを理解しておく価値があります。Lemonade は**ローカルモデルサーバー**です。AI モデルをメモリに読み込み、クラウド AI サービスと同様に HTTP 経由でアプリケーションに公開するプロセスです。

### なぜサーバーなのか？

| メリット | あなたにとっての意味 |
|---------|----------------------|
| **統合の簡素化** | アプリはハードウェア固有の C++ や Python ライブラリを扱う代わりに、1 つの HTTP API と通信します。 |
| **モデルの共有** | 読み込まれた単一のモデルが複数のアプリに同時にサービスを提供でき、RAM を消費する重複コピーが不要です。 |
| **クラウドからローカルへの移植性** | OpenAI のクラウド API 向けに書かれたコードは、URL を 1 つ変更するだけで Lemonade で動作します。 |
| **関心の分離** | モデル管理、ストリーミング、フォールトトレランスはサーバーが処理するため、開発者はアプリに集中できます。 |

### OpenAI API 標準

Lemonade は **OpenAI API** を実装しています。これは ChatGPT、Azure OpenAI、その他多数のサービスで使用されているのと同じインターフェースです。会話モデルはシンプルです：

| ロール | 話しているのは誰か |
|------|---------------|
| **system** | モデルへの指示（ペルソナ、制約、利用可能なツール） |
| **user** | 人間（またはアプリケーション）からモデルへのメッセージ |
| **assistant** | モデルが生成した応答 |

つまり、OpenAI をサポートするライブラリやアプリは、Lemonade Server が実行中に `http://localhost:13305/api/v1` を指定するだけで Lemonade と通信できます。

## メインアクティビティ — はじめてのローカル AI チャット

LLM をダウンロードして会話してみましょう。AI はすべてご自身のマシン上で実行されます。

### ステップ 1: モデルのダウンロードと実行

Lemonade にはキュレーションされたモデルライブラリが付属しています。まず、ビジョンサポートを含む有能でコンパクトなモデル **Gemma-4-E2B-it** から始めましょう。ターミナルを開いて次を実行します：

```
lemonade run Gemma-4-E2B-it-GGUF
```

この単一コマンドは 3 つのことを行います：

1. まだダウンロードされていない場合、Hugging Face からモデル（約 3 GB）を**ダウンロード**します。（時間がかかる場合があります）
2. ポート 13305 で Lemonade Server プロセスを**起動**します。
3. **Lemonade App を開き**、モデルとのチャットを開始できるようにします。


<!-- @os:windows -->
Windows では、Lemonade App が自動的に起動し、すぐにチャットを開始できます。`minimal.msi` パッケージをインストールした場合、アプリは含まれていません。チャットを開始するには、Web ブラウザを開いて `http://localhost:13305` にアクセスしてください。
<!-- @os:end -->

<!-- @os:linux -->
Linux では、ブラウザを開いて `http://localhost:13305` にアクセスし、Web アプリを利用してください。
<!-- @os:end -->

質問を入力してみてください：

```
What are three fun facts about lemons?
```

モデルはチャットウィンドウ内で直接応答します。**おめでとうございます！大規模言語モデルをローカルで実行しています。**

![ログが表示された Lemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade App のサーバーログペインでは、各応答後にモデルのパフォーマンスに関するテレメトリデータを確認できます。例えば：

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### ステップ 2: Web インターフェースとさまざまなモダリティを探索する

Lemonade には組み込みの Web インターフェースが含まれており、以下のことができます：

- **インタラクション**: 使い慣れたチャットウィンドウで読み込まれたモデルと対話する
- **モデルの閲覧**: Model Manager タブでモデルを参照する
- **新しいモデルのダウンロード**: ワンクリックで新しいモデルをダウンロードする

Web UI の **Model Manager** タブを使用して、Recipe 別またはカテゴリ別にモデルを参照しながら、さまざまなモダリティを切り替えてみてください：

1. **ビジョン:** すでに読み込まれている `Gemma-4-E2B-it-GGUF` モデルはビジョンをサポートしています。チャットボックスに画像を貼り付けて、モデルに説明を求めてみてください。
2. **画像生成:** Image カテゴリで、Model Manager から `SDXL-Turbo` などの画像モデルをダウンロードし、Lemonade Image Generator を使用してプロンプトを入力してローカルで画像を生成します。
3. **オーディオ:** Audio カテゴリで、音声テキスト変換ができる `Whisper-Tiny` などのオーディオモデルをダウンロードします。音声の録音を提供してローカルで文字起こしを行います。テキスト読み上げには、Speech カテゴリの `kokoro-v1` などのモデルをお試しください。

![Lemonade によるマルチモダリティ](../../dependencies/assets/multi_modality.png)

### ステップ 3: 異なるバックエンドでモデルを試す

Lemonade App でモデルにカーソルを合わせると、歯車アイコンが表示されます。これをクリックすると、希望するバックエンドの選択を含む、モデルのオプションを選択できます。

デフォルトでは、Lemonade は GPU アクセラレーションに Vulkan を使用します。サポートされている AMD ディスクリート GPU をお持ちの場合は、ROCm に切り替えることができます。

![Lemonade バックエンドの選択](../../dependencies/assets/lemonademodeloptions.png)

インストール済みのバックエンドを管理するには、最左列のバックエンドボタンをクリックします。

または、次のコマンドを使用してバックエンドを指定することもできます：

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

環境変数 `LEMONADE_LLAMACPP` に `vulkan`、`rocm`、または `cpu` の値を設定することで、デフォルトのバックエンドを設定することもできます。

---

## さらに深く — Python で AI 搭載アプリを構築する

ローカル AI サーバーの真の力は、あらゆるアプリケーションがわずか数行のコードで接続できることです。それを証明するために、小さくても機能的な**学習フラッシュカードジェネレーター**を構築しましょう。トピックを入力するとフラッシュカードが生成され、インタラクティブにクイズを行うことができます。

### ステップ 4: サーバーを起動する

Lemonade サーバーが実行中であることを確認します。通常、インストール後にバックグラウンドで自動的に起動します。確認するには、次を実行します：

```
lemonade status
```

`Server is running on port 13305` のようなメッセージが表示されるはずです。

サーバーが実行されていない場合は、Lemonade アプリを開いて起動します。デフォルトポート **13305** を使用します（トレイアイコンから確認または選択できます）。

### ステップ 5: OpenAI Python クライアントをインストールする

ターミナルで、venv を作成し、次のコマンドを使用して OpenAI Python クライアントをインストールします：
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

### ステップ 6: フラッシュカードアプリを構築する

コードを生成するために別のモデルをダウンロードしましょう：`Qwen3.5-35B-A3B-GGUF`。これは大型（約 20 GB）で高性能なモデルであり、RAM が 32 GB 以上のシステムに最適です。利用可能な RAM が少ない場合は、代わりに `Qwen3.5-9B-GGUF`（約 6 GB）をお試しください。

UI からダウンロードするか、次のコマンドを実行します：
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

以下のプロンプトを Lemonade Chat UI に入力して、シンプルなフラッシュカードアプリのコードを生成します。

Qwen3.5-35B-A3B-GGUF（コード作成が得意な大型モデル）を使用して Python アプリを生成し、アプリ自体は実行時に Gemma-4-E2B-it-GGUF（すでにダウンロード済みの小型モデル）を呼び出します。生成されたコードは、Python で実行するために任意のファイルにコピーできます。

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

> **ヒント**: 徹底したプロンプト作成と、リソースと速度を最適化するための 2 モデルシステムの使用により、標準的なエンジニアリングプラクティスに従っています。

便宜のために、[`flashcards.py`](assets/flashcards.py) にサンプル出力を用意しています。ご自由にディレクトリにダウンロードしてください。いずれの場合も、実行可能な Python ファイルが用意できているはずです。

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


### ステップ 7: 生成されたコードを実行する

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**表示される内容：**

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

約 150 行のコードで、ローカル LLM を搭載した完全に機能する学習ツールを構築しました。管理すべき API キーはなく、使用コストもなく、データがマシンの外に出ることもありません。

> **重要なポイント:** `client = OpenAI(base_url=...) ` の行が、このアプリを OpenAI のクラウドではなく Lemonade に結びつける*唯一*のものであることに注目してください。残りのコードは、OpenAI 互換サービスに対して記述するものと同一です。OpenAI Python ライブラリを使用したことがあれば、Lemonade でアプリを構築する方法はすでに知っているということです。

### これが示すもの

この小さなアプリは、いくつかの実際の統合パターンを実践しています：

| パターン | 登場箇所 |
|---------|-----------------|
| **システムプロンプト** | `"system"` メッセージが LLM に構造化 JSON を出力するよう指示する |
| **構造化出力** | アプリが LLM のレスポンスを JSON として解析してフラッシュカードを構築する |
| **ステートレスリクエスト** | 各 `generate_flashcards()` 呼び出しは独立している |
| **エラーハンドリング** | `try/except` が LLM の出力が有効な JSON でない場合を適切に処理する |

これらの同じパターンは、チャットボット、コードアシスタント、コンテンツジェネレーター、自動化ツールなど、あらゆるアプリケーションに拡張できます。

#### ボーナスチャレンジ

* さらなる挑戦として、[こちら](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)に提供されている例を参照して、フラッシュカードをユーザーに読み上げるようにアプリを更新してみてください。

---

<!-- @device:halo_box,halo,stx,krk -->
## NPU でのモデル実行（オプション）

Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme をお持ちの場合、デバイスには AI ワークロード専用に設計されたチップである**ニューラル プロセッシング ユニット（NPU）**が内蔵されています。NPU でモデルを実行すると、GPU を使用するよりも電力効率が高く、バックグラウンド AI タスク、長時間のセッション、バッテリー駆動での使用に最適です。

Lemonade は 3 つの NPU 実行モードをサポートしており、すべて同じ OpenAI API の背後で透過的に動作します：

| モード | 動作の仕組み | レシピ | モデル例 |
|------|-------------|--------|----------------|
| **ハイブリッド（NPU + iGPU）** | NPU がプロンプトを処理し、iGPU がトークンを生成 | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU のみ** | 推論全体が NPU 上で実行 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | NPU 上で FastFlowLM エンジンを使用し、AMD XDNA2 向けに最適化 | FLM (`flm`) | qwen3.5-4b-FLM |

### 要件

- **AMD Ryzen AI 300/400 シリーズまたは Z2 シリーズ**プロセッサ
- **FLM** モデルの場合：FLM ランタイムは Lemonade アプリ内からインストールできます。また、FLM モデルの実行時に Lemonade が FLM ランタイムを自動的にインストールします。FastFlowLM の詳細については、[こちら](https://fastflowlm.com/docs/)をご覧ください。


### ステップ 8：ハイブリッドモデルを実行する

ハイブリッドモデルは NPU と iGPU の間で処理を分担し、速度と効率のバランスを実現します。Lemonade アプリで `Ryzen AI LLM` リストからモデルを選択してください（例：`Qwen3-4B-Hybrid`）。または、次のコマンドを使用して実行することもできます：

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade は NPU を自動的に検出し、**Ryzen AI LLM** バックエンドをインストールします。

> **内部で何が起きているか？** メッセージを送信すると、NPU がプロンプト全体を並列処理します（これを「プリフィル」と呼びます）。次に、iGPU が引き継ぎ、1 トークンずつ応答を生成します（これを「デコード」と呼びます）。このハイブリッドアプローチは、各チップの強みを活かしています。

### ステップ 9：FLM モデルを実行する

FastFlowLM（FLM）モデルは AMD の XDNA2 NPU アーキテクチャ向けに特別に最適化されており、そのサイズに対して非常に高速です。例えば、`FastFlowLM NPU` リストから `qwen3.5-4b-FLM` を選択するか、次のコマンドを使用してください：

<!-- @os:windows -->
Windows で `FastFlowLM` を有効にするには：

* `Backends Manager` メニューを開きます。
* `FastFlowLM NPU` バックエンドカテゴリを見つけます。
* Install NPU をクリックします。
* インストールが完了すると、FFLM ドロップダウンメニューに約 36 個のデフォルトモデルが表示されます。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` アプリを初めて起動したとき、`FastFlowNPU` バックエンドはデフォルトで有効になっていません。
ローカルアプリがインストールページを開き、セットアップの手順を案内します。

Linux で `FastFlowLM` を有効にするには：

* `Lemonade` アプリを開きます。
* [公式 FLM](https://lemonade-server.ai/flm_npu_linux.html) ドキュメントにアクセスし、Linux ディストリビューションを選択して FLM のインストール手順に従います。
* インストールページの指示に従ってバックポートを有効にします。
* [タグページ](https://github.com/FastFlowLM/FastFlowLM/tags)から最新の `v0.9.x` リリースをダウンロードします。
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
* 推奨：`Lemonade App` を終了し、変更が検出されるよう再度開きます。
* 推奨：`Backends Manager` を開き、Install `FastFlowNPU` Backend をクリックします。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
インストールが正常に完了すると、**Lemonade Desktop App** 内の **Download Manager** で `flm:npu` が完了したことを確認できます。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
その後、利用可能な FFLM モデルを選択して NPU バックエンドの使用を開始できます。

特定のモデルについては、[モデルページ](https://fastflowlm.com/docs/models/qwen/)から目的のモデルをダウンロードし、ドキュメントに記載されているシェルコマンドを使用して検証してください。
```
flm run qwen3.5-4b-FLM
```
または 
```
lemonade run qwen3.5-4b-FLM
```

FLM モデルには最も人気のあるアーキテクチャ（Gemma 3、Qwen 3、Llama 3、DeepSeek R1）が含まれており、1 GB 未満から 13 GB 超まで幅広いサイズがあります。
Lemonade は NPU を自動的に検出し、**FastFlowLM NPU** バックエンドをインストールします。

<!-- @os:windows -->
> **ヒント：** NPU の最高のパフォーマンスを得るには、ターボモードを有効にしてください：
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### モデルの切り替え

ステップ 6 のフラッシュカードアプリは NPU モデルでも動作します。モデル名を変更するだけです：

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 次のステップ

ご自身のハードウェア上でローカル AI サーバーが動作しています。次に進む場所はこちらです：

1. **お気に入りのアプリを接続する**：Lemonade は [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)、[その他多数](https://lemonade-server.ai/marketplace)とすぐに連携できます。

2. **さらに多くのモデルを探す**：コーディング、推論、ビジョンなどに最適化されたモデルを見つけるために、完全な[モデルライブラリ](https://lemonade-server.ai/docs/server/server_models/)を探索してください。Lemonade アプリまたは `lemonade list` を使用して利用可能なモデルを確認できます。

3. **ROCm GPU アクセラレーションを解放する**：対応 AMD GPU をお持ちの場合は、ROCm バックエンドに切り替えてください：`lemonade config set llamacpp.backend=rocm`。[対応 AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations) をご確認ください。

4. **完全な API 仕様を読む**：Lemonade はチャット補完、埋め込み、音声文字起こし、画像生成、テキスト読み上げなどをサポートしています。すべてのエンドポイントについては [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) をご覧ください。

5. **貢献する**：Lemonade はオープンソースです。[コントリビューションガイド](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)を確認し、[Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) を探してみてください。