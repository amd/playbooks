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

🍋 **Lemonade** は、大規模言語モデル(LLM)、画像生成モデル、音声モデルをお使いのハードウェア上で直接実行できる、オープンソースのローカルAIサーバーです。業界標準の **OpenAI API** を通じてモデルを公開するため、OpenAIに対応したアプリケーションであれば、すぐにLemonadeと連携させることができます。このプレイブックを終える頃には、Lemonadeを使ってお使いのマシン上でモデルをローカルで実行できるようになっています。

## このプレイブックで学べること

このプレイブックを終える頃には、以下ができるようになります:

* **Lemonade Serverをインストール**し、正常に動作していることを確認する。
* 単一のコマンドで**LLMをダウンロードしてチャット**する。
* **Webユーザーインターフェースを探索**し、ビジョン、音声からテキストへの変換、画像生成などの異なるモダリティを試す。
* Vulkanと AMD ROCm™ ソフトウェアの間で**GPUバックエンドを切り替える**。
* OpenAI互換APIを使用して、ローカルLLMを利用した**Pythonアプリを構築する**。
<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AI ハードウェア上でHybridおよびFLM実行モードを使用して、**AMD Neural Processing Unit(NPU)上でモデルを実行する**。
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

- **Windows 11** を実行しているPC、またはサポートされている**Linux**ディストリビューション(Ubuntu 24.04+、Fedora、Debian)
- 手順1〜7で使用するランタイムモデル(`Gemma-4-E2B-it-GGUF`、約3GB)には**16GBのRAM**を推奨します。手順6のより大きなコード生成モデル(`Qwen3.5-35B-A3B-GGUF`、約20GB)を使用する場合は**32GB以上**を推奨します。
- ダウンロードするモデルによって異なりますが、**約4〜30GBの空きディスク容量**。このガイドで最も大きなモデルは約20GBです。
- **Python 3.10〜3.13**(Pythonアプリのセクションで使用)
- インターネット接続(有線または無線)
<!-- @device:halo_box,halo,stx,krk -->
- [オプション] NPU上でモデルを実行したい場合は、[Ryzen AI Softwareインストール手順](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers)から最新のドライバーをインストールした AMD XDNA 2 NPU(Ryzen AI 300/400/Max 300シリーズまたはZ2 Extreme)
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

## 基礎知識 — ローカルAIサーバーの仕組み

モデルを実行する前に、なぜこのような仕組みになっているのかを理解しておくとよいでしょう。Lemonadeは**ローカルモデルサーバー**であり、AIモデルをメモリにロードして、クラウドAIサービスと同様にHTTP経由でアプリケーションに公開するプロセスです。

### なぜサーバーなのか?

| メリット | あなたにとっての意味 |
|---------|----------------------|
| **統合の簡素化** | アプリはハードウェア固有のC++やPythonライブラリを扱う代わりに、単一のHTTP APIとやり取りします。 |
| **モデルの共有** | 1つのロード済みモデルで複数のアプリに同時にサービスを提供でき、重複したコピーがRAMを消費することがありません。 |
| **クラウドからローカルへの移植性** | OpenAIのクラウドAPI向けに書かれたコードは、URLを1つ変更するだけでLemonadeと連携できます。 |
| **関心の分離** | モデル管理、ストリーミング、耐障害性はサーバー側で処理されるため、開発者は自分のアプリに集中できます。 |

### OpenAI API標準

Lemonadeは**OpenAI API**を実装しています。これはChatGPT、Azure OpenAI、その他多数のサービスで使用されているのと同じインターフェースです。会話モデルはシンプルです:

| ロール | 発言者 |
|------|---------------|
| **system** | モデルへの指示(ペルソナ、制約、利用可能なツール) |
| **user** | 人間(またはアプリケーション)からモデルへのメッセージ |
| **assistant** | モデルによって生成された応答 |

これは、OpenAIをサポートするライブラリやアプリであれば、Lemonade Serverが実行中に `http://localhost:13305/api/v1` を指定するだけでLemonadeと通信できることを意味します。

## メイン活動 — 初めてのローカルAIチャット

それでは、LLMをダウンロードして会話をしてみましょう。AIはすべてお使いのマシン上でローカルに実行されます。

### 手順1: モデルのダウンロードと実行

Lemonadeにはキュレーションされたモデルライブラリが同梱されています。まずは、ビジョンサポートを含む優れたコンパクトなモデルである**Gemma-4-E2B-it**から始めましょう。ターミナルを開いて次を実行します:

```
lemonade run Gemma-4-E2B-it-GGUF
```

このコマンド1つで、次の3つのことが行われます:

1. モデル(約3GB)がまだダウンロードされていない場合、Hugging Faceから**ダウンロード**します。(時間がかかる場合があります)
2. ポート13305でLemonade Serverプロセスを**起動**します。
3. **Lemonade Appを開き**、モデルとのチャットを開始できるようにします。


<!-- @os:windows -->
Windowsでは、Lemonade Appが自動的に起動し、すぐにチャットを開始できます。`minimal.msi` パッケージをインストールした場合、アプリは含まれていません。チャットを開始するには、Webブラウザを開いて `http://localhost:13305` にアクセスしてください。
<!-- @os:end -->

<!-- @os:linux -->
Linuxでは、ブラウザを開いて `http://localhost:13305` にアクセスし、Webアプリにアクセスします。
<!-- @os:end -->

質問を入力してみましょう:

```
What are three fun facts about lemons?
```

モデルはチャットウィンドウ内で直接応答します。**おめでとうございます!大規模言語モデルをローカルで実行できました。**

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

### ステップ2: Web インターフェースと各種モダリティを試す

Lemonade には、以下のことができるビルトインの Web インターフェースが含まれています:

- 使い慣れたチャットウィンドウで、ロードされたモデルと**対話する**
- Model Manager タブで**モデルを閲覧する**
- ワンクリックで**新しいモデルをダウンロードする**

Web UI の **Model Manager** タブで、Recipe または Category ごとにモデルを閲覧しながら、さまざまなモダリティを切り替えてみましょう:

1. **Vision:** すでにロード済みの `Gemma-4-E2B-it-GGUF` モデルは vision に対応しています。チャットボックスに画像を貼り付け、モデルにその内容を説明させてみましょう。
2. **画像生成:** Image カテゴリで、Model Manager から `SDXL-Turbo` のような画像モデルをダウンロードし、Lemonade Image Generator を使ってプロンプトを入力し、ローカルで画像を生成してみましょう。
3. **音声:** Audio カテゴリで、`Whisper-Tiny` のような音声モデルをダウンロードすると、音声からテキストへの変換(speech-to-text)ができます。音声の録音を提供すると、ローカルで文字起こしされます。テキストから音声への変換(text-to-speech)には、Speech カテゴリの `kokoro-v1` などのモデルを試してみてください。

![Lemonade でのマルチモダリティ](../../dependencies/assets/multi_modality.png)

### ステップ3: 異なるバックエンドでモデルを試す

Lemonade App でモデルにカーソルを合わせると、歯車アイコンが表示されます。これをクリックすると、モデルのオプション(希望するバックエンドの選択を含む)を選択できます。

デフォルトでは、Lemonade は GPU アクセラレーションに Vulkan を使用します。サポートされている AMD ディスクリート GPU をお持ちの場合は、ROCm に切り替えることができます。

![Lemonade バックエンド選択](../../dependencies/assets/lemonademodeloptions.png)

インストール済みのバックエンドを管理するには、一番左の列にあるバックエンドボタンをクリックします。

または、次のコマンドを使ってバックエンドを指定することもできます:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

環境変数 `LEMONADE_LLAMACPP` に `vulkan`、`rocm`、`cpu` のいずれかの値を設定することで、デフォルトのバックエンドを設定することもできます。

---

## さらに深く — Python で AI 搭載アプリを構築する

ローカル AI サーバーの真の力は、わずか数行のコードでどんなアプリケーションからも接続できることにあります。それを証明するために、トピックを与えると、フラッシュカードを生成し、対話形式で自分自身をクイズできる、小さいながらも機能的な**学習フラッシュカードジェネレーター**を構築してみましょう。

### ステップ4: サーバーを起動する

Lemonade サーバーが動作していることを確認してください。通常、インストール後にバックグラウンドで自動的に起動します。確認するには、次を実行します:

```
lemonade status
```

次のようなメッセージが表示されるはずです: `Server is running on port 13305`。

サーバーが起動していない場合は、Lemonade アプリを開いて起動してください。デフォルトのポート **13305** を使用します(トレイアイコンから確認または選択できます)。

### ステップ5: OpenAI Python Client をインストールする

ターミナルで venv を作成し、次のコマンドを使って OpenAI Python Client をインストールします:
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

コード生成用に別のモデル `Qwen3.5-35B-A3B-GGUF` をダウンロードしましょう。これは大きく(約20 GB)高性能なモデルで、32 GB 以上の RAM を搭載したシステムに最適です。利用可能な RAM が少ない場合は、代わりに `Qwen3.5-9B-GGUF`(約6 GB)を試してください。

UI からダウンロードするか、以下を実行してください:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

以下のプロンプトを Lemonade Chat UI に入力して、シンプルなフラッシュカードアプリのコードを生成します。

Python アプリの生成には Qwen3.5-35B-A3B-GGUF(コード記述に優れた、より大きなモデル)を使用し、アプリ自体は実行時にすでにダウンロード済みの小さいモデルである Gemma-4-E2B-it-GGUF を呼び出します。生成されたコードは、お好きなファイルにコピーして Python で実行できます。

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

> **ヒント**: 綿密なプロンプト作成と、リソースと速度を最適化するための2モデルシステムの利用により、標準的なエンジニアリングのプラクティスに従っています。

参考として、サンプル出力を [`flashcards.py`](assets/flashcards.py) に用意しています。ぜひご自身のディレクトリにダウンロードしてください。いずれの方法でも、これで実行可能な Python ファイルが手に入るはずです。

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

**次のような画面が表示されるはずです:**

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

わずか約150行のコードで、ローカル LLM を活用した完全に機能する学習ツールを構築できました。管理すべき API キーもなく、利用コストもかからず、データが自分のマシンから外に出ることもありません。

> **重要なポイント:** `client = OpenAI(base_url=...) ` の行だけが、このアプリを OpenAI のクラウドではなく Lemonade に結びつけている*唯一*の部分であることに注目してください。それ以外のコードは、OpenAI 互換の任意のサービスに対して書くものと同一です。OpenAI の Python ライブラリを使ったことがある方であれば、すでに Lemonade でアプリを構築する方法を知っていることになります。

### これが示すもの

この小さなアプリは、いくつかの実際の統合パターンを実践しています:

| パターン | 登場箇所 |
|---------|-----------------|
| **システムプロンプト** | `"system"` メッセージが LLM に構造化された JSON を出力するよう指示します |
| **構造化出力** | アプリは LLM の応答を JSON としてパースし、フラッシュカードを構築します |
| **ステートレスなリクエスト** | 各 `generate_flashcards()` 呼び出しは独立しています |
| **エラーハンドリング** | `try/except` により、LLM の出力が有効な JSON でない場合を適切に処理します |

これらと同じパターンは、チャットボット、コードアシスタント、コンテンツジェネレーター、自動化ツールなど、あらゆるアプリケーションに応用できます。

#### ボーナスチャレンジ

* さらなる挑戦として、[こちら](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) にあるサンプルを参考に、フラッシュカードをユーザーに読み上げてもらう機能を追加するようアプリを更新してみましょう。

---

<!-- @device:halo_box,halo,stx,krk -->
## NPU での実行(オプション)

Ryzen AI 300/400/Max 300 シリーズまたは Z2 Extreme をお使いの場合、お使いのデバイスには **Neural Processing Unit (NPU)** が搭載されています。これは AI ワークロード専用に設計された専用チップです。NPU でモデルを実行すると GPU を使用するよりも電力効率が高いため、バックグラウンドの AI タスク、長時間のセッション、バッテリー駆動時の使用に最適です。

Lemonade は 3 つの NPU 実行モードをサポートしており、いずれも同じ OpenAI API の背後で透過的に動作します。

| モード | 動作方法 | レシピ | サンプルモデル |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU がプロンプトを処理し、iGPU がトークンを生成 | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU のみ** | 推論全体を NPU 上で実行 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | AMD XDNA2 向けに最適化された FastFlowLM エンジンを NPU 上で使用 | FLM (`flm`) | qwen3.5-4b-FLM |

### 要件

- **AMD Ryzen AI 300/400 シリーズまたは Z2 シリーズ**プロセッサ
- **FLM** モデルの場合:FLM ランタイムは Lemonade アプリ内からインストールできます。また、FLM モデルを実行すると Lemonade が自動的に FLM ランタイムをインストールします。FastFlowLM について詳しくは、[こちら](https://fastflowlm.com/docs/)をご覧ください。


### ステップ 8: Hybrid モデルを実行する

Hybrid モデルは NPU と iGPU に処理を分割することで、速度と効率のバランスが取れています。Lemonade App では、`Ryzen AI LLM` リストからモデル(例:`Qwen3-4B-Hybrid`)を選択するか、以下のコマンドで実行します。

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade はお使いの NPU を自動的に検出し、**Ryzen AI LLM** バックエンドをインストールします。

> **内部で何が起きているのか?** メッセージを送信すると、NPU がプロンプト全体を並列処理します(これを「プリフィル」と呼びます)。その後、iGPU が引き継いで応答をトークンごとに生成します(これを「デコード」と呼びます)。この Hybrid 方式は、それぞれのチップの強みを活かします。

### ステップ 9: FLM モデルを実行する

FastFlowLM(FLM)モデルは AMD の XDNA2 NPU アーキテクチャに特化して最適化されており、そのサイズの割に非常に高速です。例えば、`FastFlowLM NPU` リストから `qwen3.5-4b-FLM` を選択するか、以下のコマンドを使用します。

<!-- @os:windows -->
Windows で `FastFlowLM` を有効にするには:

* `Backends Manager` メニューを開きます。
* `FastFlowLM NPU` バックエンドカテゴリを見つけます。
* Install NPU をクリックします。
* インストールが完了すると、約 36 個のデフォルトモデルが FFLM ドロップダウンメニューから利用可能になります。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` アプリを初めて起動したとき、`FastFlowNPU` バックエンドはデフォルトでは有効になっていません。
ローカルアプリはセットアップを案内するためにインストールページを開きます。

Linux で `FastFlowLM` を有効にするには:

* `Lemonade` アプリを開きます。
* [公式 FLM](https://lemonade-server.ai/flm_npu_linux.html) ドキュメントを参照し、お使いの Linux ディストリビューションを選択して FLM のインストール手順に従ってください。
* インストールページの指示に従い、backports を有効にします。
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
* 推奨:`Lemonade App` を終了し、再度開いて変更が検出されるようにします。
* 推奨:`Backends Manager` を開き、`FastFlowNPU` Backend の Install をクリックします。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
インストールが成功すると、**Lemonade Desktop App** 内の **Download Manager** で `flm:npu` が完了したことを確認できます。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
その後、利用可能な FFLM モデルの中から任意のものを選択し、NPU バックエンドの使用を開始できます。

特定のモデルについては、[モデルページ](https://fastflowlm.com/docs/models/qwen/)から目的のモデルをダウンロードし、ドキュメントに記載されている Shell コマンドを使用して検証してください。
```
flm run qwen3.5-4b-FLM
```
または
```
lemonade run qwen3.5-4b-FLM
```

FLM モデルには、最も人気のあるアーキテクチャ(Gemma 3、Qwen 3、Llama 3、DeepSeek R1)の一部が含まれており、サイズは 1 GB 未満から 13 GB 超まで幅広くあります。
Lemonade はお使いの NPU を自動的に検出し、**FastFlowLM NPU** バックエンドをインストールします。

<!-- @os:windows -->
> **ヒント:** NPU のパフォーマンスを最大限に引き出すには、ターボモードを有効にしてください:
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

これで、お使いのハードウェア上でローカル AI サーバーが稼働しています。次に進むべき方向は以下の通りです。

1. **お気に入りのアプリと接続する**: Lemonade は [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)、そして[その他多数](https://lemonade-server.ai/marketplace)とすぐに連携できます。

2. **さらに多くのモデルを閲覧する**: [モデルライブラリ](https://lemonade-server.ai/docs/server/server_models/)全体を確認し、コーディング、推論、ビジョンなどに最適化されたモデルを見つけてください。Lemonade App または `lemonade list` を使用して、利用可能なモデルを確認できます。

3. **ROCm GPU アクセラレーションを利用する**: サポートされている AMD GPU をお使いの場合は、ROCm バックエンドに切り替えてください:`lemonade config set llamacpp.backend=rocm`。[サポートされている AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)をご覧ください。

4. **完全な API 仕様を読む**: Lemonade はチャット補完、埋め込み、音声文字起こし、画像生成、音声合成などをサポートしています。すべてのエンドポイントについては[サーバー仕様](https://lemonade-server.ai/docs/server/server_spec/)をご覧ください。

5. **貢献する**: Lemonade はオープンソースです。[貢献ガイド](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)を確認し、[Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)を探してみてください。

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