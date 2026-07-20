<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# <!-- @github-only -->
> [!IMPORTANT]
> このプレイブックでは、GitHubでは表示できない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks)にアクセスしてください。
<!-- @github-only:end -->

## 概要

🍋 **Lemonade** は、大規模言語モデル(LLM)、画像生成モデル、音声モデルを自分自身のハードウェア上で直接実行できるオープンソースのローカルAIサーバーです。業界標準の**OpenAI API**を通じてモデルを公開するため、OpenAIで動作するあらゆるアプリがLemonadeでもそのまま動作します。このプレイブックの終わりまでに、Lemonadeを使ってご自身のマシン上でモデルをローカル実行できるようになります。

## このプレイブックで学ぶこと

このプレイブックを終える頃には、以下ができるようになります:

* **Lemonade Server をインストール**し、正常に動作していることを確認する。
* 単一のコマンドで**LLMをダウンロードしてチャット**する。
* **Web UIを探索**し、ビジョン、音声認識、画像生成など様々なモダリティを試す。
* VulkanとAMD ROCm™ ソフトウェアの間で**GPUバックエンドを切り替える**。
* OpenAI互換APIを使用してローカルLLMを利用する**Pythonアプリを構築する**。
<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AIハードウェア上でHybridおよびFLM実行モードを使用して、**AMD Neural Processing Unit(NPU)でモデルを実行する**。
<!-- @device:end -->

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

始める前に、以下が揃っていることを確認してください:

- **Windows 11**を実行しているPC、またはサポートされている**Linux**ディストリビューション(Ubuntu 24.04+、Fedora、Debian)
- ステップ1〜7で使用するランタイムモデル(`Gemma-4-E2B-it-GGUF`、約3GB)には**16GBのRAM**が推奨されます。ステップ6でより大きなコード生成モデル(`Qwen3.5-35B-A3B-GGUF`、約20GB)を使用する場合は**32GB以上**を推奨します。
- ダウンロードするモデルによって異なりますが、**約4〜30GBの空きディスク容量**が必要です。このガイドで最も大きいモデルは約20GBです。
- **Python 3.10〜3.13**(Pythonアプリのセクションで使用)
- インターネット接続(有線または無線)
<!-- @device:halo_box,halo,stx,krk -->
- [任意] NPU上でモデルを実行したい場合は、[Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers)から最新のドライバーをインストールしたAMD XDNA 2 NPU(Ryzen AI 300/400/Max 300シリーズまたはZ2 Extreme)
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

## 基本概念 — ローカルAIサーバーの仕組み

モデルを実行する前に、なぜこのような構成になっているのかを理解しておくと良いでしょう。Lemonadeは**ローカルモデルサーバー**であり、AIモデルをメモリにロードし、クラウドAIサービスと同様にHTTP経由でアプリケーションに公開するプロセスです。

### なぜサーバーなのか?

| メリット | あなたにとっての意味 |
|---------|----------------------|
| **統合の簡素化** | アプリはハードウェア固有のC++やPythonライブラリを扱う代わりに、単一のHTTP APIと通信します。 |
| **モデルの共有** | 1つのロード済みモデルが複数のアプリに同時にサービスを提供でき、重複コピーがRAMを消費することがありません。 |
| **クラウドからローカルへの移植性** | OpenAIのクラウドAPI向けに書かれたコードは、URLを1つ変更するだけでLemonadeで動作します。 |
| **関心の分離** | モデル管理、ストリーミング、フォールトトレランスはサーバー側で処理されるため、開発者は自分のアプリに集中できます。 |

### OpenAI APIの標準

Lemonadeは**OpenAI API**を実装しています。これはChatGPT、Azure OpenAI、その他多数のサービスで使用されているのと同じインターフェースです。会話モデルはシンプルです:

| 役割 | 誰が話しているか |
|------|---------------|
| **system** | モデルへの指示(ペルソナ、制約、利用可能なツール) |
| **user** | 人間(またはアプリケーション)からモデルへのメッセージ |
| **assistant** | モデルによって生成された応答 |

つまり、OpenAIをサポートするライブラリやアプリであれば、Lemonade Serverが実行中に`http://localhost:13305/api/v1`を指定するだけでLemonadeと通信できます。

## メインアクティビティ — 初めてのローカルAIチャット

LLMをダウンロードして、AIを完全に自分のマシン上で実行しながら会話してみましょう。

### ステップ1: モデルのダウンロードと実行

Lemonadeには厳選されたモデルライブラリが同梱されています。まずは、ビジョンサポートを含む有能でコンパクトなモデルである**Gemma-4-E2B-it**から始めましょう。ターミナルを開いて、以下を実行します:

```
lemonade run Gemma-4-E2B-it-GGUF
```

この単一のコマンドは以下の3つのことを行います:

1. モデル(約3GB)がまだダウンロードされていない場合、Hugging Faceから**ダウンロード**します。(時間がかかる場合があります)
2. ポート13305でLemonade Serverプロセスを**起動**します。
3. モデルとのチャットをすぐに開始できるように、Lemonade Appを**開きます**。


<!-- @os:windows -->
Windowsでは、Lemonade Appが自動的に起動し、すぐにチャットを開始できます。`minimal.msi`パッケージをインストールした場合、アプリは含まれていません。チャットを開始するには、Webブラウザを開いて`http://localhost:13305`にアクセスしてください。
<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ブラウザを開いて`http://localhost:13305`にアクセスし、Webアプリにアクセスしてください。
<!-- @os:end -->

質問を入力してみてください:

```
What are three fun facts about lemons?
```

モデルはチャットウィンドウ内で直接応答します。**おめでとうございます!大規模言語モデルをローカルで実行できています。**

![ログが表示されたLemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade AppのServer Logsペインでは、各応答の後にモデルのパフォーマンスに関するテレメトリデータを確認できます。例:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### ステップ2: Webインターフェースとさまざまなモダリティを試す

Lemonadeには、以下のことができる組み込みのWebインターフェースが含まれています。

- おなじみのチャットウィンドウでロード済みモデルと**やり取り**する
- Model Managerタブで**モデルを閲覧**する
- ワンクリックで**新しいモデルをダウンロード**する

Web UIの**Model Manager**タブを使って、Recipe別またはCategory別にモデルを閲覧しながら、さまざまなモダリティを切り替えてみてください。

1. **ビジョン:** すでにロード済みの`Gemma-4-E2B-it-GGUF`モデルはビジョンをサポートしています。画像をチャットボックスに貼り付けて、モデルに説明してもらいましょう。
2. **画像生成:** Imageカテゴリで、Model Managerから`SDXL-Turbo`などの画像モデルをダウンロードし、Lemonade Image Generatorを使ってプロンプトを入力し、ローカルで画像を生成します。
3. **オーディオ:** Audioカテゴリで、`Whisper-Tiny`などのオーディオモデルをダウンロードすると、音声からテキストへの変換ができます。音声の録音を提供すると、ローカルで文字起こしされます。テキストから音声への変換には、Speechカテゴリにある`kokoro-v1`などのモデルを試してください。

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### ステップ3: 異なるバックエンドでモデルを試す

Lemonade Appでモデルにカーソルを合わせると、歯車アイコンが表示されます。これをクリックすると、モデルのオプション（希望するバックエンドの選択を含む）を選択できます。

デフォルトでは、LemonadeはGPUアクセラレーションにVulkanを使用します。サポートされているAMDディスクリートGPUをお持ちの場合は、ROCmに切り替えることができます。

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

インストール済みのバックエンドを管理するには、一番左の列にあるバックエンドボタンをクリックしてください。

または、次のコマンドを使ってバックエンドを指定することもできます。

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

環境変数`LEMONADE_LLAMACPP`に`vulkan`、`rocm`、`cpu`のいずれかの値を設定することで、デフォルトのバックエンドを設定することもできます。

---

## さらに深く — PythonでAI搭載アプリを構築する

ローカルAIサーバーの真の強みは、どんなアプリケーションでもわずか数行のコードで接続できることです。それを証明するために、小さいながらも実用的な**学習用フラッシュカードジェネレーター**を構築してみましょう。トピックを与えると、フラッシュカードが生成され、対話的に自分自身をクイズできます。

### ステップ4: サーバーを起動する

Lemonadeサーバーが実行されていることを確認してください。インストール後、通常はバックグラウンドで自動的に起動します。確認するには、次を実行します。

```
lemonade status
```

`Server is running on port 13305`のようなメッセージが表示されるはずです。

サーバーが実行されていない場合は、Lemonadeアプリを開いて起動してください。デフォルトのポート**13305**を使用します（トレイアイコンから確認または選択できます）。

### ステップ5: OpenAI Pythonクライアントをインストールする

ターミナルで、venvを作成し、次のコマンドを使ってOpenAI Pythonクライアントをインストールします。
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

コード生成用に別のモデル`Qwen3.5-35B-A3B-GGUF`をダウンロードしましょう。これは大規模（約20GB）で高性能なモデルであり、32GB以上のRAMを搭載したシステムに最適です。利用可能なRAMがそれより少ない場合は、代わりに`Qwen3.5-9B-GGUF`（約6GB）を試してください。

UIからダウンロードするか、次を実行してください。
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

シンプルなFlashcardアプリのコードを生成するために、次のプロンプトをLemonade Chat UIに入力してください。

Pythonアプリを生成するには（コードを書くのが得意な大規模モデルである）Qwen3.5-35B-A3B-GGUFを使用し、アプリ自体は実行時にすでにダウンロード済みの小規模モデルGemma-4-E2B-it-GGUFを呼び出します。生成されたコードは、Pythonで実行するために任意のファイルにコピーできます。

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

> **ヒント**: ここでは、綿密なプロンプト作成と、リソースと速度を最適化するための2モデルシステムを使用することで、標準的なエンジニアリングプラクティスに従っています。

便宜上、[`flashcards.py`](assets/flashcards.py)にサンプル出力を用意しています。お好きなディレクトリにダウンロードしてください。いずれにせよ、実行可能なPythonファイルが手元にあるはずです。

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

**表示される内容は以下の通りです。**

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

わずか150行程度のコードで、ローカルLLMを利用した完全に機能する学習ツールを構築できました。管理すべきAPIキーもなく、利用料もかからず、データがマシンの外に出ることもありません。

> **重要な洞察:** `client = OpenAI(base_url=...) `の行だけが、このアプリをOpenAIのクラウドではなくLemonadeに結び付けている*唯一*の要素であることに注目してください。それ以外のコードは、OpenAI互換の任意のサービスに対して書くコードとまったく同じです。OpenAI Pythonライブラリを使ったことがあれば、Lemonadeでアプリを構築する方法はすでに理解していることになります。

### これが示すこと

この小さなアプリは、いくつかの実際の統合パターンを実践しています。

| パターン | 出現箇所 |
|---------|-----------------|
| **システムプロンプト** | `"system"`メッセージがLLMに構造化されたJSONを出力するよう指示する |
| **構造化出力** | アプリがLLMの応答をJSONとして解析し、フラッシュカードを構築する |
| **ステートレスなリクエスト** | 各`generate_flashcards()`呼び出しは独立している |
| **エラーハンドリング** | `try/except`が、LLMの出力が有効なJSONでない場合を適切に処理する |

これらと同じパターンは、チャットボット、コードアシスタント、コンテンツジェネレーター、自動化ツールなど、あらゆるアプリケーションに応用できます。

#### ボーナスチャレンジ

* さらなる挑戦として、[こちら](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)で提供されている例を参考に、フラッシュカードをユーザーに音声で読み上げる機能を追加してみてください。

---

<!-- @device:halo_box,halo,stx,krk -->
## NPUでモデルを実行する(任意)

Ryzen AI 300/400/Max 300シリーズまたはZ2 Extremeをお使いの場合、お使いのデバイスにはAIワークロード専用に設計された専用チップである**ニューラルプロセッシングユニット(NPU)**が搭載されています。NPUでモデルを実行すると、GPUを使用する場合よりも電力効率が高くなるため、バックグラウンドのAIタスク、長時間のセッション、バッテリー駆動時の使用に最適です。

Lemonadeは3つのNPU実行モードをサポートしており、すべて同じOpenAI APIの裏側で透過的に動作します。

| モード | 動作方法 | レシピ | サンプルモデル |
|------|-------------|--------|----------------|
| **ハイブリッド(NPU + iGPU)** | NPUがプロンプトを処理し、iGPUがトークンを生成 | OGA(`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU専用** | 推論全体がNPU上で実行される | Ryzen AI LLM(`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | NPU上でFastFlowLMエンジンを使用し、AMD XDNA2に最適化 | FLM(`flm`) | qwen3.5-4b-FLM |

### 要件

- **AMD Ryzen AI 300/400シリーズまたはZ2シリーズ**プロセッサ
- **FLM**モデルの場合:FLMランタイムはLemonadeアプリ内からインストールできます。または、FLMモデルを実行する際にLemonadeが自動的にFLMランタイムをインストールします。FastFlowLMについて詳しくは[こちら](https://fastflowlm.com/docs/)をご覧ください。


### ステップ8:ハイブリッドモデルを実行する

ハイブリッドモデルはNPUとiGPUの間で作業を分割し、速度と効率のバランスを良くします。Lemonadeアプリでは、`Ryzen AI LLM`リストからモデルを選択します(例:`Qwen3-4B-Hybrid`)。または、次のコマンドを使用して実行します。

```
lemonade run Qwen3-4B-Hybrid
```

Lemonadeは自動的にお使いのNPUを検出し、**Ryzen AI LLM**バックエンドをインストールします。

> **裏側では何が起きているのか?** メッセージを送信すると、NPUがプロンプト全体を並列処理します(これを「prefill」と呼びます)。その後、iGPUが引き継ぎ、応答を1トークンずつ生成します(これを「decode」と呼びます)。このハイブリッドアプローチにより、それぞれのチップの強みが活かされます。

### ステップ9:FLMモデルを実行する

FastFlowLM(FLM)モデルはAMDのXDNA2 NPUアーキテクチャに特化して最適化されており、そのサイズの割に非常に高速です。例えば、`FastFlowLM NPU`リストから`qwen3.5-4b-FLM`を選択するか、次のコマンドを使用してください。

<!-- @os:windows -->
Windowsで`FastFlowLM`を有効にするには:

* `Backends Manager`メニューを開きます。
* `FastFlowLM NPU`バックエンドカテゴリを見つけます。
* Install NPUをクリックします。
* インストールが完了すると、FFLMドロップダウンメニューの下に約36のデフォルトモデルが利用可能になります。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade`アプリを初めて起動する際、`FastFlowNPU`バックエンドはデフォルトでは有効になっていません。
ローカルアプリがセットアップの手順を案内するインストールページを開きます。

Linuxで`FastFlowLM`を有効にするには:

* `Lemonade`アプリを開きます。
* [公式FLM](https://lemonade-server.ai/flm_npu_linux.html)ドキュメントにアクセスし、お使いのLinuxディストリビューションを選択してFLMのインストール手順に従います。
* インストールページの指示に従ってバックポートを有効にします。
* [tagsページ](https://github.com/FastFlowLM/FastFlowLM/tags)から最新の`v0.9.x`リリースをダウンロードします。'
<!-- @device:end -->

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
* 推奨:`Lemonade App`を終了して再度開き、変更が検出されるようにします。
* 推奨:`Backends Manager`を開き、`FastFlowNPU` Backendのインストールをクリックします。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
インストールが成功すると、**Lemonade Desktop App**内の**Download Manager**で`flm:npu`が完了したことが表示されます。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
その後、利用可能なFFLMモデルのいずれかを選択し、NPUバックエンドの使用を開始できます。

特定のモデルについては、[モデルページ](https://fastflowlm.com/docs/models/qwen/)から目的のモデルをダウンロードし、ドキュメントに記載されているShellコマンドを使用して検証してください。
```
flm run qwen3.5-4b-FLM
```
または
```
lemonade run qwen3.5-4b-FLM
```
を使用します。
FLMモデルには最も人気のあるアーキテクチャの一部(Gemma 3、Qwen 3、Llama 3、DeepSeek R1)が含まれており、1GB未満から13GB超まで幅広いサイズがあります。
Lemonadeは自動的にお使いのNPUを検出し、**FastFlowLM NPU**バックエンドをインストールします。

<!-- @os:windows -->
> **ヒント:** 最高のNPUパフォーマンスを得るには、ターボモードを有効にしてください。
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

これで、自分のハードウェア上でローカルAIサーバーが稼働するようになりました。次に進むべき方向は以下の通りです。

1. **お気に入りのアプリと接続する**:Lemonadeは[VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)、[その他多数](https://lemonade-server.ai/marketplace)とすぐに連携できます。

2. **さらに多くのモデルを閲覧する**:コーディング、推論、ビジョンなどに最適化されたモデルを見つけるために、[モデルライブラリ](https://lemonade-server.ai/docs/server/server_models/)全体をご覧ください。利用可能なモデルを確認するには、LemonadeアプリまたはLemonade Appまたは`lemonade list`を使用してください。

3. **ROCm GPUアクセラレーションを有効にする**:対応するAMD GPUをお持ちの場合は、ROCmバックエンドに切り替えてください:`lemonade config set llamacpp.backend=rocm`。詳しくは[対応AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)をご覧ください。

4. **完全なAPI仕様を読む**:Lemonadeはチャット補完、埋め込み、音声文字起こし、画像生成、テキスト読み上げなどに対応しています。すべてのエンドポイントについては[Server Spec](https://lemonade-server.ai/docs/server/server_spec/)をご覧ください。

5. **貢献する**:Lemonadeはオープンソースです。[コントリビューションガイド](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)をチェックし、[Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)を探してみてください。