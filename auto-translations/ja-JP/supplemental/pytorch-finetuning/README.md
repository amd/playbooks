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

このチュートリアルでは、PyTorch と ROCm を使用して大規模言語モデル (LLM) をファインチューニングするためのステップバイステップの例を紹介します。標準的なファインチューニングから、メモリ効率に優れたパラメータ効率的ファインチューニング (PEFT) 戦略まで、複数の手法を取り上げているため、ニーズに合わせてモデルを簡単に適応させることができます。

**使用モデル**: google/gemma-3-4b-it (QLoRA スクリプト: openai/gpt-oss-20b) *(ゲーテッドモデルの場合は [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) を参照)*
**ハードウェア**: ROCm 対応の AMD Radeon™ GPU
**フレームワーク**: PyTorch + Hugging Face (Transformers、PEFT、Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **注:**
> - フル ファインチューニングには、少なくとも **64 GB のシステム RAM** が必要であり、そのうち少なくとも **32 GB は GPU で利用可能** である必要があります (この 32 GB は 64 GB の一部であり、追加で必要というわけではありません)。
> - 提供されているトレーニング スクリプトでモデルを置き換えることで、**GPT-OSS-20B** を含む他のモデル アーキテクチャを試すこともできます。
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **注:** LoRA および QLoRA のファインチューニングには、少なくとも **32 GB のシステム RAM** が必要であり、そのうち少なくとも **16 GB は GPU で利用可能** である必要があります (この 16 GB は 32 GB の一部であり、追加で必要というわけではありません)。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRA のファインチューニングには、少なくとも **32 GB のシステム RAM** が必要であり、そのうち少なくとも **16 GB は GPU で利用可能** である必要があります (この 16 GB は 32 GB の一部であり、追加で必要というわけではありません)。
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** LoRA および QLoRA のファインチューニングには、少なくとも **16 GB の専用 GPU メモリ** と **32 GB のシステム RAM** を搭載したグラフィックス カードが必要です。
> - Linux では、トレーニングはグラフィックス カードの専用 VRAM 内で完全に実行されます。
> - VRAM が不足しても、共有 GPU メモリ (システム RAM) にフォールバックすることはありません。
> - 専用 VRAM が 16 GB 未満のカードは、システムに十分な RAM があっても、Linux でのトレーニング中にメモリ不足になります。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRA のファインチューニングには、少なくとも **16 GB の合計 GPU メモリ** と **32 GB のシステム RAM** が必要です。
> - Windows では、合計 GPU メモリは、グラフィックス カードの専用 VRAM と (システム RAM から借用される) 共有 GPU メモリを合わせたものになります。
> - そのため、専用 VRAM が 16 GB 未満のカードでも、共有 GPU メモリを使って差分を補うことで、このプレイブックを実行できます。
<!-- @os:end -->
<!-- @device:end -->

## このチュートリアルで学べること

- PyTorch と ROCm を使用して、LoRA、QLoRA、およびフル ファインチューニングで LLM をファインチューニングする方法
- ファインチューニング済みモデルを保存してデプロイする方法
- トレーニングを監視し、一般的な問題をデバッグする方法

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェア更新の確認
> **注**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

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
**ユーザーに GPU デバイスへのアクセス権を付与します** (これを有効にするには一度ログアウトして再度ログインする必要があります):

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
**Windows:** ここではコア パッケージのみがテストおよびサポートされています。**bitsandbytes は Windows ではあまりサポートされていない** ため、Windows 版インストールにはこれが含まれていません。Windows では LoRA またはフル ファインチューニングを使用してください (QLoRA には bitsandbytes が必要であり、Linux 向けです)。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF 認証の有効化 (ゲーテッド モデルやカスタム / 事前インストールされていないモデルの場合)

この例では、**ゲーテッド** モデルである **google/gemma-3-4b-it** を使用します。Hugging Face でこのモデルの利用規約に同意し、トレーニング スクリプトがモデルをダウンロードできるように認証を行う必要があります。

1. **ライセンスへの同意:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) を開き、サインイン (またはアカウントを作成) して、モデル ページでライセンス / 利用規約に同意します (例: 「Agree and access repository」)。
2. **インストールとログイン:** Hugging Face CLI をインストールし、標準のログインを実行します。

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

## 各手法の理解

### LoRA とは?

**LoRA (Low-Rank Adaptation)** はベース モデルを凍結したまま、特定の層に追加される小さな「アダプター」行列のみをトレーニングします。

- **主なアイデア**: 数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランクの更新 (積のパラメータ数がはるかに少ない 2 つの小さな行列) を学習します。これにより、フル ファインチューニングの品質のほとんどを維持しながら、トレーニング可能なパラメータと VRAM を大幅に削減できます。

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRA とは?

**QLoRA** は **4 ビット量子化** と **LoRA** を組み合わせたものです。ベース モデルは 4 ビットでロードされ (大幅なメモリ節約)、LoRA アダプターのみがより高い精度でトレーニングされます。これにより、LoRA のパラメータ効率に加えて、VRAM を大幅に削減できますが、フル精度の LoRA と比較するとわずかな品質のトレードオフが生じます。4 ビット量子化は数値的な不安定性 (損失のスパイクや NaN) を引き起こす可能性があるため、十分な VRAM が利用可能な場合、ユーザーは **LoRA** を好むことが多い点に注意してください。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注**: `openai/gpt-oss-20b` のような MXFP4 ベース モデルの場合、QLoRA ではなく **LoRA** (`train_lora.py`) の使用を推奨します。QLoRA スクリプトの `bitsandbytes` の 4 ビット パスは、通常 MXFP4 の重みを BF16 に逆量子化するため、実行は標準の LoRA と同様に動作します。ネイティブの MXFP4 を使用するには、ソースからビルドした `bitsandbytes` に加え、対応する Transformers/Triton/kernels スタックが必要です。詳細は [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4) を参照してください。

---
### 2. 方法を選択する

| 方法 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linux のみ） | 12-16GB | 最速 | 90-95% | メモリ使用量を抑えたい場合 |
| **LoRA** | 24-32GB | 高速 | 95-98% | バランスの取れたアプローチ |
| **Full** | 80GB+ | 最も遅い | 100% | 最高品質を求める場合 |

### 3. トレーニングの実行

**データセットとモデルが学習する内容**  
これらのスクリプトは、データセットをチャット形式の例に変換します。例えば、QLoRA スクリプトは **Abirate/english_quotes** を使用し、各サンプルは次のようなユーザー・アシスタントのペアになります。

- **ユーザー:** 「&lt;tag&gt; についての名言を教えてください」
- **アシスタント:** 「&lt;quote&gt; – &lt;author&gt;」

ファインチューニングにより、モデルはあるトピックについての名言を求めるプロンプトに応答し、`<quote text> - <author>` という形式で返すように学習します。LoRA およびフルファインチューニングのスクリプトは **databricks/databricks-dolly-15k**（一般的な指示・応答のペア）を使用するため、スクリプトによって正確なタスクは異なりますが、考え方は同じです。選択したデータセットと形式にモデルを適応させることです。

以下に、利用可能なトレーニング方法の概要を示します。それぞれの方法には対応するスクリプトへのリンクがあり、適切なアプローチを選ぶための簡単な説明が付いています。

| スクリプト                           | 方法            | 説明                                                                                                         | 一般的な VRAM | 推奨対象                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ベースモデルを凍結したまま、小さなアダプター行列をトレーニングします。3～5倍高速で、フル品質の約95～98%を実現します。                         | 24–32GB      | 上級ユーザー向け、複数のアダプターを使用する場合、VRAM に余裕がある場合    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux のみ)*             | **QLoRA**       | 4ビット量子化 + LoRA アダプター。メモリ使用量が最小で最速、品質への影響はわずかです。`bitsandbytes`（Linux のみ）が必要です。                            | 12–16GB      | ほとんどのユーザー向け、高速な実験、VRAM が限られている場合      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **フルファインチューニング** | すべてのモデルパラメータを更新します。最高品質を実現しますが、メモリと計算リソースの使用量も最大になります。                                    | 40GB+        | 最高品質を求める場合、研究用途、VRAM に余裕がある場合           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** フルファインチューニング（`train_full_finetuning.py`）には64GB以上のシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAまたはQLoRAの使用をご検討ください。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** フルファインチューニング（`train_full_finetuning.py`）には64GB以上のシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAの使用をご検討ください。
<!-- @os:end -->
<!-- @device:end -->

お好みの `Training method` を選択し、対応するスクリプトをダウンロードして、仮想環境を有効化したまま以下のコマンドを使用して実行してください。

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
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

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

**注:**  
- モデルディレクトリ名（`output-gemma-3-4b-it-full`、`output-gpt-oss-20b-qlora`）が、トレーニングで実際に出力されたフォルダ名と一致していることを確認してください。  
- QLoRA の代わりに LoRA を使用した場合は、パスを適宜置き換えてください。  
- 一部の Gemma モデルでは、`from_pretrained` に `trust_remote_code=True` を指定する必要があります。関連する警告が表示された場合は追加してください。

その他のカスタム設定（パディングトークン、デバイスなど）については、トレーニングに使用したスクリプトを参照してください。

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

すべてのスクリプトは同じデータセット形式を使用します。読み込みセクションを以下のように置き換えてください。

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

**ローカル JSON/JSONL ファイルのデータセット形式:**

この方法を使用する場合、解析エラーを避けるために JSON ファイルが正しく構造化されていることを確認してください。

以下のガイドラインに従う必要があります。
* **ファイルの整形:** JSON ファイルは、適切な構造と構文を確保するために、統合開発環境（IDE）内で整形する必要があります。
* **必須キー:** カスタム JSON ファイルには `instruction` と `response` のキーを含める必要があります。これらのキーは、この方法が正しく機能するために不可欠です。
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
**Hugging Face Hub データセットのデータセット形式**

Hugging Face のデータセットを利用する場合は、スムーズに統合できるよう、データセットが正しく構造化されていることを確認してください。

以下のガイドラインに従ってください。
* **Instruction-Response ペア:** `instruction-response` ペアを含むデータセットを使用してください。この構造は、意図した機能にとって不可欠です。
* **カスタムキーの変更:** データセットが `instruction-response` 構造に準拠していない場合は、`format_instruction()` 関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応できます。

調整の例: データセットの出力を調整する必要がある場合は、format_instruction() 関数内の応答セクションを変更して、要件に合わせることができます。
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

### トレーニングパラメータの調整

トレーニングスクリプトを編集し、目的に合わせて変数を変更してください。**学習率**（`LR`）、**エポック数**（`EPOCHS`）、**バッチサイズ**（`BATCH_SIZE`）、**勾配累積**（`GRAD_ACCUM_STEPS`）、および LoRA/QLoRA の**ランク**（`LORA_R`）です。実行を高速化するには、エポック数を減らし、学習率（LR）を高く設定してください。品質を向上させるには、エポック数を増やし、LR を低く設定してください。メモリ不足エラーが発生した場合は、バッチサイズまたはシーケンス長を減らしてください。
### メモリ最適化のヒント

メモリ不足エラーが発生した場合は、以下を試してください。

**1. バッチサイズを減らす:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. シーケンス長を短くする:**
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

## モニタリングとデバッグ

### GPU メモリを監視する

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (オプション)Weights & Biases で実験を追跡する

実行とメトリクスを [Weights & Biases](https://wandb.ai) にログ記録するには:

```bash
pip install wandb
wandb login
```

トレーニング スクリプトでは、トレーナー構成の中で `report_to="wandb"` を設定し、必要に応じて `run_name="your-experiment-name"` も設定します。Wandb を使用しない場合は、`report_to` をデフォルトのままにするか、`"none"` に設定してください。

### よくある問題

#### メモリ不足(OOM)

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

1. **評価する**:ホールドアウト テストデータで十分に評価し、汎化性能を測定して過学習を回避します。
2. **実験する**:さまざまなハイパーパラメータの値を試し、精度、速度、メモリのトレードオフを改善します。
3. **追跡する**:再現性のある研究のために、すべての実験(および対応するメトリクス)を Weights & Biases で追跡します。
4. **試す**:独自のカスタム データセットでトレーニングを行い、ユースケースに合わせてモデルを適応させます。
5. **デプロイする**:互換性のあるハードウェア上で vLLM などの効率的なバックエンドを使用し、高速推論のためにファインチューニング済みモデルをデプロイします。
6. **探求する**:プロンプト エンジニアリング、混合精度、より長いシーケンス長などの高度な手法を探求します。
7. **トレーニングする**:異なるタスクやドメイン向けに複数の LoRA アダプターをトレーニングし、必要に応じて切り替えます。

---