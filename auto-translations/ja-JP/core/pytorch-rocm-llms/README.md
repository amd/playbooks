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


ご自身のハードウェアで強力なAI言語モデルを実行したいとお考えですか？このガイドでその方法をご紹介します。
このチュートリアルでは、AMD ROCm™ ソフトウェアを活用したPyTorchを使用し、文書の要約、質問への回答、テキスト生成などが可能なモデルを、すべてローカル環境で実行します。

## このガイドで学べること

- PyTorchとROCmを使用して、gpt-oss-20bやqwen3.5-4Bなどのローカルでのモデル実行
- LLMを使ったドキュメント要約ツールの作成

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注**: VS Codeがインストールされていない場合は、Ryzen AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
Linuxでは、任意のディレクトリでターミナルを開き、以下のコマンドに従ってROCm+Pytorchがすでにインストールされたvenvを作成します。
<!-- @test:id=create-venv timeout=300 -->
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
**ユーザーにGPUデバイスへのアクセス権を付与します**（有効にするにはログアウトして再ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

Linuxでは、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
<!-- @test:id=create-venv timeout=300 -->
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
Windowsでは、任意のディレクトリでターミナルを開き、以下のコマンドに従ってROCm+Pytorchがすでにインストールされたvenvを作成します。
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windowsでは、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **ヒント**: Windowsユーザーは、一部のPowerShellコマンドを実行する前に、PowerShellの実行ポリシーを変更する必要がある場合があります（例：RemoteSignedまたはUnrestrictedに設定するなど）。

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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **注:** モデルの読み込みに失敗したり、メモリ不足になったりする場合は、`kernels`パッケージをインストールして最適化された量子化でモデルを読み込んでみてください。
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## サンプルスクリプトでクイックスタート

このプレイブックには、すぐに使えるスクリプトが含まれています。クリックしてプレビューし、作成した環境と同じディレクトリにダウンロードしてください。

| スクリプト | 説明 | 使用方法 |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | 基本的なLLMテキスト生成 | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Harmony対応の文書要約ツール | `python summarizer.py --file document.txt` |

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

両方のスクリプトは以下をサポートしています：
- `--model`フラグによるモデル選択
- 適切なモデルプロンプト作成のためのチャットテンプレートフォーマット（特に文書要約に便利）

## 最初のLLMを読み込んで実行する

同梱されている[run_llm.py](assets/run_llm.py)スクリプトは、PyTorchとAMD ROCmを使用してテキストを生成する方法を示しています。

> **注:** モデルを読み込むと、Hugging Face Transformersはまずローカルキャッシュ（Linuxでは`~/.cache/huggingface/hub`、Windowsでは`C:\Users\<user>\.cache\huggingface\hub`）を確認します。モデルがキャッシュされていない場合は、huggingface.coから自動的にダウンロードされます。初回実行時は、モデルサイズとネットワーク速度によっては数分かかる場合があります。

以下のスニペットは、モデルを使用し、質問をカスタマイズする方法を示しています。

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
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
    device_map="auto",
    disable_mmap=True
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


## ドキュメント要約ツールの作成

ローカルLLMの出力を生成できるようになったので、次はこれを応用して実用的な文書要約ツールを作成してみましょう。このセクションでは、[summarizer.py](assets/summarizer.py)スクリプトを使用して.txtファイルを読み込み、GPU上ですべてローカルで実行しながら簡潔な要約を自動生成します。

このスクリプトはそのまま動作するように設計されています。エディタでスクリプトを開いてコードを確認し、プロンプトをカスタマイズしたり、長さや温度などのパラメータを調整したりしてみてください。

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

## 生成パラメータについて学ぶ

| パラメータ | 制御対象 | 一般的な値 |
|-----------|------------------|----------------|
| `max_new_tokens` | LLMの出力の最大長 | 要約には50～500トークンを使用します（1トークンは約0.75英単語に相当）。 |
| `temperature` | 創造性。値が低いほど焦点が絞られ、高いほど予測不可能性が高まります | - **0.1～0.3**：焦点が絞られ、決定論的（要約に適している）<br> **0.5～0.7**：バランス型（一般用途）<br> **0.8～1.0**：創造的で多様（ブレインストーミング） |
| `top_p` | Nucleus Sampling - 値が低いほど、モデルの出力がより限定的になる | **0.1～0.5**：厳格で予測可能 <br> **0.9～0.95**：（標準的で自然な会話調） |


## 実際の活用例

- **研究論文の分析**：複雑な論文から重要な発見を抽出し、素早くレビュー
- **ニュース集約**：ニュース記事を要約し、簡潔な日次ダイジェストやハイライトを作成
- **議事録**：文字起こしを、実行可能な項目や簡潔な要約に凝縮
- **法的文書のレビュー**：長い法的文書から関連する条項や義務を素早く抽出
- **コードドキュメント**：簡潔なリポジトリの概要や関数の説明を生成
## 次のステップ

- **ファインチューニング**: 特定の分野や専門用語に合わせてモデルを適応させ、精度を向上させます(Fine-tuning Playbooksを参照)
- **RAGシステム**: LLMとドキュメント検索を組み合わせて、コンテキストを考慮した回答や検索を実現します
- **モデルの探求**: Llama 3、Phi-3、Qwenなどの新しいモデルを試して、より良い結果を追求します
- **本番環境へのデプロイ**: vLLMなどのツールを使用して、組織内でスケーラブルなLLMサービングを実現します

このシステムにより、高度な言語モデルをローカルで実行する力が手に入ります。さまざまなモデル、プロンプト、パラメータを試して、あなたのアプリケーションに最適な方法を見つけてください。