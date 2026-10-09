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

このチュートリアルでは、PyTorch と ROCm を使用して大規模言語モデル (LLM) をファインチューニングする手順を、具体例を交えて段階的に説明します。標準的なファインチューニングから、メモリ効率に優れた Parameter-Efficient Fine-Tuning (PEFT) 戦略まで、複数の手法を取り上げているため、目的に応じてモデルを柔軟に適応させることができます。

**使用モデル**: google/gemma-3-4b-it (QLoRA スクリプト: openai/gpt-oss-20b)  *(ゲート付きモデルの場合は [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) を参照)*  
**ハードウェア**: ROCm 対応の AMD Radeon™ GPU  
**フレームワーク**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **注記:** 
> - フル ファインチューニングには、少なくとも **64 GB のシステム RAM** が必要であり、そのうち少なくとも **32 GB が GPU で使用可能** である必要があります (この 32 GB は 64 GB の一部であり、追加で必要になるわけではありません)。
> - 提供されているトレーニング スクリプト内のモデルを置き換えることで、**GPT-OSS-20B** を含む他のモデル アーキテクチャを試すこともできます。
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **注記:** LoRA および QLoRA のファインチューニングには、少なくとも **32 GB のシステム RAM** が必要であり、そのうち少なくとも **16 GB が GPU で使用可能** である必要があります (この 16 GB は 32 GB の一部であり、追加で必要になるわけではありません)。
<!-- @os:end -->

<!-- @os:windows -->
> **注記:** LoRA のファインチューニングには、少なくとも **32 GB のシステム RAM** が必要であり、そのうち少なくとも **16 GB が GPU で使用可能** である必要があります (この 16 GB は 32 GB の一部であり、追加で必要になるわけではありません)。
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注記:** LoRA および QLoRA のファインチューニングには、少なくとも **16 GB の専用 GPU メモリ** と **32 GB のシステム RAM** を備えたグラフィック カードが必要です。
> - Linux では、トレーニングはグラフィック カードの専用 VRAM 内のみで実行されます。
> - VRAM が不足しても、共有 GPU メモリ (システム RAM) へのフォールバックは行われません。
> - 専用 VRAM が 16 GB 未満のカードは、たとえシステムに十分な RAM があっても、Linux でのトレーニング中にメモリ不足になります。
<!-- @os:end -->

<!-- @os:windows -->
> **注記:** LoRA のファインチューニングには、少なくとも **合計 16 GB の GPU メモリ** と **32 GB のシステム RAM** が必要です。
> - Windows では、GPU の合計メモリは、グラフィック カードの専用 VRAM と (システム RAM から借用される) 共有 GPU メモリを合わせたものになります。
> - そのため、専用 VRAM が 16 GB 未満のカードでも、共有 GPU メモリで不足分を補うことで、この手順を実行できる場合があります。
<!-- @os:end -->
<!-- @device:end -->

## 学習内容

- PyTorch と ROCm を使用して、LoRA、QLoRA、フル ファインチューニングにより LLM をファインチューニングする方法
- ファインチューニングしたモデルを保存してデプロイする方法
- トレーニングを監視し、よくある問題をデバッグする方法

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注記**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

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
**ユーザーに GPU デバイスへのアクセス権を付与します** (有効にするには、一度ログアウトしてから再度ログインしてください):

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
**Windows:** ここではコア パッケージのみがテストおよびサポートされています。**bitsandbytes は Windows では十分にサポートされていない** ため、Windows 版のインストールではこれを省略しています。Windows では LoRA またはフル ファインチューニングを使用してください (QLoRA は bitsandbytes を必要とするため、Linux 向けです)。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF 認証を有効にする (ゲート付きまたはカスタム / 事前インストールされていないモデル)

この例では、**ゲート付き** モデルである **google/gemma-3-4b-it** を使用します。トレーニング スクリプトがこのモデルをダウンロードできるようにするには、Hugging Face 上でモデルの利用規約に同意したうえで認証を行う必要があります。

1. **ライセンスに同意する:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) を開いてサインイン (またはアカウントを作成) し、モデル ページでライセンス/利用規約に同意します (例: 「Agree and access repository」)。
2. **インストールしてログインする:** Hugging Face CLI をインストールし、標準のログインを実行します:

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

## 各手法について理解する

### LoRA とは？

**LoRA (Low-Rank Adaptation)** は、ベース モデルを凍結したまま、特定のレイヤーに追加される小さな「アダプター」行列のみをトレーニングする手法です。

- **主なアイデア**: 数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランクの更新 (積を取るとパラメータ数がはるかに少なくなる 2 つの小さな行列) を学習します。これにより、フル ファインチューニングの品質の大部分を維持しながら、トレーニング対象パラメータと VRAM を大幅に削減できます。

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRA とは？

**QLoRA** は、**4-bit 量子化** と **LoRA** を組み合わせた手法です。ベース モデルは 4-bit で読み込まれ (メモリを大幅に節約)、LoRA アダプターのみがより高い精度でトレーニングされます。これにより、LoRA のパラメータ効率に加えて、VRAM をさらに大幅に削減でき、フル精度の LoRA と比べてわずかな品質のトレードオフが生じます。なお、4-bit 量子化は数値的な不安定性 (損失のスパイクや NaN) を引き起こすことがあるため、十分な VRAM がある場合はユーザーが **LoRA** を選ぶことが多い点に注意してください。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注記**: `openai/gpt-oss-20b` のような MXFP4 ベース モデルの場合は、QLoRA ではなく **LoRA** (`train_lora.py`) の使用を推奨します。QLoRA スクリプトの `bitsandbytes` による 4-bit パスは、通常 MXFP4 の重みを BF16 に逆量子化するため、実行動作は標準的な LoRA と同様になります。ネイティブの MXFP4 を利用するには、ソースからビルドした `bitsandbytes` に加え、対応する Transformers/Triton/kernels のスタックが必要です。詳細は [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4) を参照してください。

---
### 2. 方法を選択

| 方法 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linux のみ） | 12-16GB | 最速 | 90-95% | メモリ使用量を抑えたい場合 |
| **LoRA** | 24-32GB | 高速 | 95-98% | バランスの取れたアプローチ |
| **フル** | 80GB+ | 最も遅い | 100% | 最大限の品質 |

### 3. トレーニングを実行

**データセットとモデルが学習する内容**  
これらのスクリプトは、データセットをチャット形式の例に変換します。たとえば、QLoRA スクリプトでは **Abirate/english_quotes** を使用し、各例は次のようなユーザー・アシスタントのペアになります。

- **ユーザー:** 「&lt;tag&gt;に関する引用をください」
- **アシスタント:** 「&lt;quote&gt; – &lt;author&gt;」

ファインチューニングにより、モデルはトピックに関する引用を求めるプロンプトに応答し、`<quote text> - <author>` という形式でそれを返すように学習します。LoRA およびフルファインチューニングのスクリプトは **databricks/databricks-dolly-15k**（一般的な指示・応答のペア）を使用するため、具体的なタスクはスクリプトによって異なりますが、基本的な考え方は同じです。選択したデータセットと形式にモデルを適応させるというものです。

以下は、利用可能なトレーニング方法の概要です。各方法はそれぞれのスクリプトへのリンクと、適切なアプローチを選ぶための簡単な説明を提供しています。

| スクリプト                           | 方法            | 説明                                                                                                         | 一般的な VRAM | 推奨用途                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | 小さなアダプター行列をトレーニングし、ベースモデルは固定します。3〜5倍高速で、フル品質の約95〜98%を達成します。                         | 24–32GB      | 上級ユーザー向け、複数のアダプター、より多くの VRAM が必要    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux のみ)*             | **QLoRA**       | 4ビット量子化 + LoRA アダプター。メモリ使用量が最も少なく、最速で、わずかな品質のトレードオフがあります。`bitsandbytes`（Linux のみ）が必要です。                            | 12–16GB      | ほとんどのユーザー向け、高速な実験、限られた VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **フルファインチューニング** | すべてのモデルパラメータを更新します。最大限の品質を実現しますが、メモリと計算リソースの使用量が最も多くなります。                                    | 40GB+        | 最大限の品質、研究用途、大容量の VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** フルファインチューニング(`train_full_finetuning.py`)には64GB以上のシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAまたはQLoRAの使用をご検討ください。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** フルファインチューニング(`train_full_finetuning.py`)には64GB以上のシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAの使用をご検討ください。
<!-- @os:end -->
<!-- @device:end -->

ご希望の`Training method`を選択し、該当するスクリプトをダウンロードして、仮想環境を有効化した状態でコマンドを使用して実行するだけです。

```python
python3 train_<method_name>.py.
```

## ファインチューニングしたモデルを使用する

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
- モデルディレクトリ名(`output-gemma-3-4b-it-full`、`output-gpt-oss-20b-qlora`)が、トレーニングによる実際の出力フォルダと一致していることを確認してください。  
- QLoRA の代わりに LoRA を使用した場合は、パスを適切に置き換えてください。  
- 一部の Gemma モデルでは、`from_pretrained`に`trust_remote_code=True`を指定する必要があります。関連する警告が表示された場合は追加してください。

その他のカスタム設定(パディングトークン、デバイスなど)については、トレーニングに使用したスクリプトを参照してください。

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

すべてのスクリプトは同じデータセット形式を使用します。読み込みセクションを置き換えてください。

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

この方法を使用する場合は、解析エラーを避けるために JSON ファイルが正しく構造化されていることを確認してください。

次のガイドラインに従う必要があります。
* **ファイルの形式:** JSON ファイルは、適切な構造と構文を確保するために、統合開発環境(IDE)内でフォーマットする必要があります。
* **必須キー:** カスタム JSON ファイルには、`instruction`と`response`というキーを含める必要があります。これらのキーは、この方法が正しく機能するために不可欠です。
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

Hugging Face のデータセットを利用する場合は、スムーズな統合を可能にするために、データセットが正しく構造化されていることを確認してください。

次のガイドラインに従ってください。
* **指示・応答のペア:** `instruction-response`のペアを含むデータセットに焦点を当ててください。この構造は、意図した機能にとって不可欠です。
* **カスタムキーの変更:** データセットが`instruction-response`構造に準拠していない場合は、`format_instruction()`関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応できます。

調整の例: データセットの出力を調整する必要がある場合は、要件に合わせて`format_instruction()`関数内の応答セクションを変更できます。
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

CSV ファイル形式を使用するスクリプトに対応するには、CSV ファイルに`instruction`と`response`という名前の列が含まれていることを確認する必要があります。
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### トレーニングパラメータを調整する

トレーニングスクリプトを編集し、目標に合わせて変数を変更してください。**学習率**(`LR`)、**エポック数**(`EPOCHS`)、**バッチサイズ**(`BATCH_SIZE`)、**勾配累積**(`GRAD_ACCUM_STEPS`)、LoRA/QLoRA の場合は**ランク**(`LORA_R`)です。より高速に実行するには、エポック数を減らし学習率(LR)を上げてください。より高い品質を求める場合は、エポック数を増やし LR を下げてください。メモリ不足エラーが発生した場合は、バッチサイズまたはシーケンス長を減らしてください。
### メモリ最適化のヒント

メモリ不足エラーが発生した場合は、以下をお試しください。

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

**4. 勾配チェックポイントを有効にする (フル ファインチューニングのみ):**
```python
model.gradient_checkpointing_enable()
```

---

## モニタリングとデバッグ

### GPU メモリの監視

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (オプション) Weights & Biases による実験のトラッキング

実行結果とメトリクスを[Weights & Biases](https://wandb.ai)に記録するには:

```bash
pip install wandb
wandb login
```

トレーニングスクリプトでは、トレーナーの設定において `report_to="wandb"` を設定し、必要に応じて `run_name="your-experiment-name"` も設定してください。Wandb を使用したくない場合は、`report_to` をデフォルトのままにするか、`"none"` に設定してください。

### よくある問題

#### メモリ不足 (OOM)

**解決策:** バッチサイズを減らすか、QLoRA を使用してください
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### 損失が減少しない

**解決策:** 学習率を調整してください
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### トレーニングが遅い

**解決策:** メモリに余裕がある場合はバッチサイズを増やしてください
```python
BATCH_SIZE = 8
```
## 次のステップ

ファインチューニングが正常に完了したら、モデルをさらに活用するために、以下の次のステップを検討してください。

1. **評価**: 汎化性能を測定し、過学習を避けるために、保留しておいたテストデータで十分に評価を行います。
2. **実験**: 精度、速度、メモリのトレードオフを改善するために、さまざまなハイパーパラメータの値を試します。
3. **トラッキング**: 再現性のある研究のために、Weights & Biases を使用してすべての実験(および対応するメトリクス)を記録します。
4. **トライ**: 独自のカスタムデータセットでトレーニングを行い、特定のユースケースに合わせてモデルを適応させます。
5. **デプロイ**: 互換性のあるハードウェア上で vLLM のような効率的なバックエンドを使用して、ファインチューニング済みのモデルを高速推論用にデプロイします。
6. **探求**: プロンプトエンジニアリング、混合精度、より長いシーケンス長など、高度な手法を探求します。
7. **トレーニング**: 異なるタスクやドメイン向けに複数の LoRA アダプターをトレーニングし、必要に応じて切り替えます。

---