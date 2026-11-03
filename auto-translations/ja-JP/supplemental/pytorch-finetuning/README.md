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

このチュートリアルでは、PyTorchとROCmを使用して大規模言語モデル(LLM)をファインチューニングするためのステップバイステップの例を紹介します。標準的なファインチューニングから、メモリ効率の高いパラメータ効率的ファインチューニング(PEFT)戦略まで、いくつかの手法を取り上げているため、ニーズに合わせて簡単にモデルを適応させることができます。

**使用モデル**: google/gemma-3-4b-it *(ゲート付きの場合は[HF認証の有効化](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models)を参照)*  
**ハードウェア**: ROCm対応のAMD Radeon™ GPU  
**フレームワーク**: PyTorch + Hugging Face(Transformers、PEFT、Transformer Reinforcement Learning(TRL))

<!-- @device:halo,halo_box -->
> **注:** 
> - フル ファインチューニングには、少なくとも**64 GBのシステムRAM**が必要で、そのうち少なくとも**32 GBをGPUで使用可能**にする必要があります(この32 GBは64 GBの一部であり、64 GBに加えて必要というわけではありません)。
> - 提供されているトレーニングスクリプト内のモデルを置き換えることで、**GPT-OSS-20B**を含む他のモデルアーキテクチャを試すこともできます。
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **注:** LoRAおよびQLoRAファインチューニングには、少なくとも**32 GBのシステムRAM**が必要で、そのうち少なくとも**16 GBをGPUで使用可能**にする必要があります(この16 GBは32 GBの一部であり、32 GBに加えて必要というわけではありません)。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRAファインチューニングには、少なくとも**32 GBのシステムRAM**が必要で、そのうち少なくとも**16 GBをGPUで使用可能**にする必要があります(この16 GBは32 GBの一部であり、32 GBに加えて必要というわけではありません)。
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** LoRAおよびQLoRAファインチューニングには、少なくとも**16 GBの専用GPUメモリ**を搭載したグラフィックスカードと**32 GBのシステムRAM**が必要です。
> - Linuxでは、トレーニングはグラフィックスカードの専用VRAM内で完全に実行されます。
> - VRAMが不足した場合でも、共有GPUメモリ(システムRAM)へのフォールバックは行われません。
> - 専用VRAMが16 GB未満のカードは、システムに十分なRAMがあっても、Linuxでのトレーニング中にメモリ不足になります。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRAファインチューニングには、少なくとも**16 GBの合計GPUメモリ**と**32 GBのシステムRAM**が必要です。
> - Windowsでは、合計GPUメモリはグラフィックスカードの専用VRAMと共有GPUメモリ(システムRAMから借用)を合わせたものになります。
> - そのため、専用VRAMが16 GB未満のカードでも、共有GPUメモリを使用して不足分を補うことで、このプレイブックを実行できます。
<!-- @os:end -->
<!-- @device:end -->

## 学習内容

- PyTorchとROCmを使用して、LoRA、QLoRA、フルファインチューニングでLLMをファインチューニングする方法
- ファインチューニングしたモデルを保存してデプロイする方法
- トレーニングを監視し、一般的な問題をデバッグする方法

<!-- @device:halo_box,halo,stx,krk -->
## メモリ設定の構成

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注**: VS Codeがインストールされていない場合は、Ryzen AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

#### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPUデバイスへのユーザーアクセスを許可する**(これを有効にするには、一度ログアウトして再度ログインしてください):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### 基本的な依存関係のインストール
<!-- @require:pytorch -->

#### 追加の依存関係

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** ここではコアパッケージのみがテストおよびサポートされています。**bitsandbytesはWindowsでは十分にサポートされていない**ため、Windowsのインストールではこれを省略しています。Windowsでは、LoRAまたはフルファインチューニングを使用してください(QLoRAはbitsandbytesを必要とし、Linux向けを想定しています)。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF認証の有効化(ゲート付きまたはカスタム/事前インストールされていないモデル)

この例では、**ゲート付き**モデルである**google/gemma-3-4b-it**を使用します。トレーニングスクリプトがこのモデルをダウンロードできるようにするには、Hugging Face上でモデルの利用規約に同意し、その後認証を行う必要があります。

1. **ライセンスへの同意:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)を開いてサインイン(またはアカウントを作成)し、モデルページでライセンス/利用規約に同意します(例:「Agree and access repository」)。
2. **インストールとログイン:** Hugging Face CLIをインストールし、標準のログインを実行します:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## 手法について

### LoRAとは?

**LoRA (Low-Rank Adaptation)** は、ベースモデルを凍結したまま、特定のレイヤーに追加される小さな「アダプター」行列のみをトレーニングします。

- **重要な考え方**: 数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランク更新(積がはるかに少ないパラメータ数になる2つの小さな行列)を学習します。これにより、フルファインチューニングの品質のほとんどを維持しながら、トレーニング対象パラメータとVRAMを大幅に削減できます。

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRAとは?

**QLoRA**は、**4ビット量子化**と**LoRA**を組み合わせたものです。ベースモデルは4ビットでロードされ(メモリを大幅に節約)、LoRAアダプターのみがより高い精度でトレーニングされます。これにより、LoRAのパラメータ効率に加えて、はるかに低いVRAM使用量を実現できますが、フル精度のLoRAと比較すると品質面でわずかなトレードオフがあります。4ビット量子化は数値的な不安定性(損失のスパイクやNaN)を引き起こす可能性があるため、十分なVRAMがある場合はユーザーが**LoRA**を選ぶことが多いことに注意してください。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注**: `openai/gpt-oss-20b`のようなMXFP4ベースモデルの場合、QLoRAではなく**LoRA** (`train_lora.py`)の使用を推奨します。QLoRAスクリプトの`bitsandbytes` 4ビットパスは、通常MXFP4の重みをBF16に逆量子化するため、実行は標準的なLoRAのように動作します。ネイティブのMXFP4を使用するには、ソースからビルドされた`bitsandbytes`と、対応するTransformers/Triton/kernelsスタックが必要です。詳細は[TransformersのMXFP4ドキュメント](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)を参照してください。

---
### 2. トレーニング方法を選択する

| 方式 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linux のみ） | 12～16GB | 最速 | 90～95% | メモリ使用量を抑えたい場合 |
| **LoRA** | 24～32GB | 高速 | 95～98% | バランスの取れたアプローチ |
| **Full** | 80GB 以上 | 最も低速 | 100% | 最大限の品質 |

### 3. トレーニングを実行する

**データセットとモデルが学習する内容**  
このスクリプトはデータセットをチャット形式の例に変換します。例えば、QLoRA スクリプトでは **Abirate/english_quotes** を使用しており、各例は次のようなユーザーとアシスタントのペアになります。

- **ユーザー：** 「&lt;tag&gt; に関する引用を教えてください」
- **アシスタント：** 「&lt;quote&gt; － &lt;author&gt;」

ファインチューニングにより、モデルはあるトピックに関する引用を求めるプロンプトに応答し、`<quote text> - <author>` という形式で返すことを学習します。LoRA およびフルファインチューニングのスクリプトでは、**databricks/databricks-dolly-15k**（一般的な指示／応答のペア）を使用しているため、正確なタスクはスクリプトによって異なりますが、考え方は同じです。つまり、選択したデータセットと形式にモデルを適応させます。

以下は、利用可能なトレーニング方法の概要です。各方法にはスクリプトへのリンクがあり、適切な方式を選ぶための簡単な説明が付いています。

| スクリプト                           | 方式            | 説明                                                                                                         | 標準的な VRAM | 推奨対象                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ベースモデルを固定したまま小さなアダプター行列をトレーニングします。3～5 倍高速で、品質は約 95～98% です。                         | 24～32GB      | 上級ユーザー、複数アダプター利用、VRAM に余裕がある場合    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux のみ)*             | **QLoRA**       | 4 ビット量子化と LoRA アダプターを組み合わせています。メモリ使用量が最も少なく、最も高速ですが、わずかに品質が低下します。`bitsandbytes`（Linux のみ）が必要です。                            | 12～16GB      | ほとんどのユーザー、迅速な実験、VRAM が限られている場合      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **フルファインチューニング** | モデルのすべてのパラメーターを更新します。最大の品質が得られますが、メモリと計算量の使用も最大になります。                                    | 40GB 以上        | 最大品質を求める場合、研究用途、VRAM に余裕がある場合           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注：** フルファインチューニング（`train_full_finetuning.py`）には 64GB を超えるシステム RAM が必要になる場合があり、このデバイスでは実行できない可能性があります。代わりに LoRA または QLoRA の使用を検討してください。
<!-- @os:end -->

<!-- @os:windows -->
> **注：** フルファインチューニング（`train_full_finetuning.py`）には 64GB を超えるシステム RAM が必要になる場合があり、このデバイスでは実行できない可能性があります。代わりに LoRA の使用を検討してください。
<!-- @os:end -->
<!-- @device:end -->

希望する `Training method` を選択し、対応するスクリプトをダウンロードして、仮想環境を有効化した状態のまま次のコマンドを使用して実行してください。 

```python
python3 train_<method_name>.py.
```

## ファインチューニング済みモデルの使用

### フルファインチューニング後

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA/QLoRA トレーニング後

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA アダプターをベースモデルにマージする

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**注：**  
- モデルディレクトリ名（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）が、トレーニングによって実際に出力されたフォルダーと一致していることを確認してください。  
- QLoRA の代わりに LoRA を使用した場合は、パスを適宜置き換えてください。  
- 一部の Gemma モデルでは、`from_pretrained` に `trust_remote_code=True` を指定する必要があります。関連する警告が表示された場合は追加してください。

パディングトークンやデバイスなど、その他のカスタム設定については、トレーニングに使用したスクリプトを参照してください。

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## カスタマイズガイド

### 独自のデータセットを使用する

すべてのスクリプトは同じデータセット形式を使用します。読み込みセクションを次のように置き換えてください。

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**ローカルの JSON/JSONL ファイルのデータセット形式：**

この方法を使用する場合は、解析エラーを避けるために JSON ファイルが正しく構造化されていることを確認してください。 

以下のガイドラインに従う必要があります。
* **ファイルの整形：** JSON ファイルは、適切な構造と構文を確保するために、統合開発環境（IDE）内で整形してください。
* **必須キー：** カスタム JSON ファイルには、`instruction` と `response` というキーを含める必要があります。これらのキーは、この方法が正しく機能するために不可欠です。
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Hugging Face Hub のデータセットの形式**

Hugging Face のデータセットを使用する場合は、スムーズに統合できるようにデータセットが正しく構造化されていることを確認してください。 

以下のガイドラインに従ってください。
* **instruction-response のペア：** `instruction-response` のペアを含むデータセットを対象としてください。この構造は、意図した機能を実現するために不可欠です。
* **カスタムキーの変更：** データセットが `instruction-response` の構造に準拠していない場合は、`format_instruction()` 関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応できます。

調整例：データセットの出力を調整する必要がある場合は、format_instruction() 関数内の応答部分を変更することで、要件に合わせることができます。
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSV ファイルのデータセット形式**

CSV ファイル形式を使用するスクリプトに対応させるには、CSV ファイルに `instruction` と `response` という名前の列が含まれていることを確認する必要があります。 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### トレーニングパラメーターを調整する

トレーニングスクリプトを編集し、目的に合わせて変数を変更してください。**学習率**（`LR`）、**エポック数**（`EPOCHS`）、**バッチサイズ**（`BATCH_SIZE`）、**勾配累積**（`GRAD_ACCUM_STEPS`）、および LoRA/QLoRA の**ランク**（`LORA_R`）です。より高速に実行するにはエポック数を減らし、学習率（LR）を高くしてください。品質を高めるにはエポック数を増やし、LR を低くしてください。メモリ不足エラーが発生した場合は、バッチサイズまたはシーケンス長を減らしてください。
### メモリ最適化のヒント

メモリ不足エラーが発生した場合:

**1. バッチサイズを減らす:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. シーケンス長を減らす:**
```python
max_seq_length=256  # Instead of 512
```

**3. より積極的な量子化を使用する:**
```
Full → LoRA → QLoRA
```

**4. 勾配チェックポイントを有効にする(フル ファインチューニングのみ):**
```python
model.gradient_checkpointing_enable()
```

---

## 監視とデバッグ

### GPU メモリの監視

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (オプション) Weights & Biases で実験を追跡する

[Weights & Biases](https://wandb.ai) に実行結果とメトリクスを記録するには:

```bash
pip install wandb
wandb login
```

トレーニング スクリプトでは、トレーナーの設定で `report_to="wandb"` を設定し、必要に応じて `run_name="your-experiment-name"` も設定してください。Wandb を使用したくない場合は、`report_to` をデフォルトのままにするか、`"none"` に設定してください。

### よくある問題

#### メモリ不足 (OOM)

**解決策:** バッチサイズを減らす、および/または QLoRA を使用する
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### 損失が減少しない

**解決策:** 学習率を調整する
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### トレーニングが遅い

**解決策:** メモリに余裕がある場合はバッチサイズを増やす
```python
BATCH_SIZE = 8
```
## 次のステップ

ファインチューニングに成功したら、モデルをさらに活用するために、以下の次のステップを検討してください。

1. **評価**: ホールドアウトされたテスト データで十分に評価し、汎化性能を測定して過学習を回避します。
2. **実験**: 精度、速度、メモリのトレードオフを改善するために、さまざまなハイパーパラメータ値を試します。
3. **追跡**: 再現可能な研究のために、Weights & Biases を使用してすべての実験(および対応するメトリクス)を記録します。
4. **試行**: 独自のカスタム データセットでトレーニングを行い、ユースケースに合わせてモデルを適応させます。
5. **デプロイ**: vLLM などの効率的なバックエンドを使用し、互換性のあるハードウェア上でファインチューニング済みモデルを高速推論用にデプロイします。
6. **探求**: プロンプト エンジニアリング、混合精度、より長いシーケンス長など、高度な技術を探求します。
7. **トレーニング**: 異なるタスクやドメイン向けに複数の LoRA アダプターをトレーニングし、必要に応じて切り替えます。

---