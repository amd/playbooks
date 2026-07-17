<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub ではレンダリングできない特殊なタグを使用しています。コンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要


強力な AI 言語モデルを自分のハードウェアで実行したいですか？このガイドでその方法を説明します。
このチュートリアルでは、AMD ROCm™ ソフトウェアを搭載した PyTorch を使用して、ドキュメントの要約、質問への回答、テキスト生成などを行えるモデルをすべてローカルで実行します。

## 学習内容

- PyTorch と ROCm を使用して gpt-oss-20b や qwen3.5-4B などの LLM をローカルで実行する
- LLM を使用したドキュメント要約ツールを作成する

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注意**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux では、任意のディレクトリでターミナルを開き、以下のコマンドに従って ROCm+Pytorch がすでにインストールされた venv を作成します。
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPU デバイスへのユーザーアクセスを許可します**（有効にするにはログアウトして再度ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って ROCm+Pytorch がすでにインストールされた venv を作成します。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell 実行ポリシーを変更する必要がある場合があります（例：
> RemoteSigned または Unrestricted に設定する）。

<!-- @os:end -->

### 基本的な依存関係のインストール
<!-- @require:driver,pytorch -->

### 追加の依存関係のインストール

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## サンプルスクリプトによるクイックスタート

このプレイブックにはすぐに使えるスクリプトが含まれています。クリックしてプレビューし、作成した環境と同じディレクトリにダウンロードしてください。

| スクリプト | 説明 | 使用方法 |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | 基本的な LLM テキスト生成 | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Harmony サポート付きドキュメント要約ツール | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

両スクリプトは以下をサポートしています：
- `--model` フラグによるモデル選択
- 適切なモデルプロンプティングのためのチャットテンプレートフォーマット（特にドキュメント要約に有用）

## 最初の LLM の読み込みと実行

付属の [run_llm.py](assets/run_llm.py) スクリプトは、PyTorch と AMD ROCm を使用して LLM でテキストを生成する方法を示しています。

> **注意:** モデルを読み込む際、Hugging Face Transformers はまずローカルキャッシュ（Linux では `~/.cache/huggingface/hub`、Windows では `C:\Users\<user>\.cache\huggingface\hub`）を確認します。モデルがキャッシュされていない場合は、huggingface.co から自動的にダウンロードされます。初回実行時は、モデルのサイズとネットワーク速度によって数分かかる場合があります。

以下のスニペットは、モデルの使用方法と質問のカスタマイズ方法を示しています。

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

ダウンロードしたスクリプトを試してみましょう：

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## ドキュメント要約ツールの構築

ローカル LLM の出力を生成できたので、それを発展させて実用的なドキュメント要約ツールを構築できます。このセクションでは、[summarizer.py](assets/summarizer.py) スクリプトを使用して .txt ファイルを入力し、簡潔な要約を自動生成します。すべて GPU 上でローカルに実行されます。

このスクリプトはすぐに動作するよう設計されています。エディターでスクリプトを開いてコードを確認し、プロンプトをカスタマイズしたり、長さや温度などのパラメーターを調整したりしてください。

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### 使用例

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## 生成パラメーターについて学ぶ

| パラメーター | 制御する内容 | 一般的な値 |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM の出力の最大長 | 要約には 50〜500 トークンを使用します（1 トークンは英語の単語約 0.75 語に相当） |
| `temperature` | 創造性。低い値は集中した出力を生み、高い値はより予測不可能な出力をもたらします | - **0.1–0.3**: 集中した、決定論的な出力（要約に適している） <br> **0.5–0.7**: バランスの取れた出力（一般的な用途） <br> **0.8–1.0**: 創造的で多様な出力（ブレインストーミング） |
| `top_p` | 核サンプリング - 低い値はモデルをより狭い出力に制限します | **0.1-0.5**: 厳格で予測可能 <br> **0.9-0.95**: （標準的で自然な会話調） |


## 実世界での応用例

- **研究論文の分析**: 複雑な論文から主要な知見を抽出して迅速にレビュー
- **ニュースの集約**: ニュース記事を簡潔な日次ダイジェストやハイライトに要約
- **議事録**: トランスクリプトをアクションアイテムと簡潔な要約に凝縮
- **法的文書のレビュー**: 長い法的文書から関連する条項や義務を迅速に抽出
- **コードドキュメント**: リポジトリの概要と関数の説明を簡潔に生成

## 次のステップ

- **ファインチューニング**: 精度向上のためにモデルを特定の分野や専門用語に適応させる（ファインチューニングプレイブックを参照）
- **RAG システム**: コンテキストを考慮した回答と検索のために LLM とドキュメント検索を組み合わせる
- **モデルの探索**: Llama 3、Phi-3、Qwen などの新しいモデルを試してより良い結果を得る
- **本番環境へのデプロイ**: 組織内でスケーラブルな LLM サービングを行うために vLLM などのツールを使用する

お使いのシステムは、高度な言語モデルをローカルで実行する能力を提供します。さまざまなモデル、プロンプト、パラメーターを試して、アプリケーションに最適なものを見つけてください。