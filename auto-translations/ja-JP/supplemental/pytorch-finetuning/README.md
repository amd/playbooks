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

このチュートリアルでは、PyTorch と ROCm を使用して大規模言語モデル(LLM)をファインチューニングするための、ステップバイステップの例を提供します。標準的なファインチューニングから、メモリ効率の高い Parameter-Efficient Fine-Tuning(PEFT)戦略まで、いくつかの手法を取り上げているため、ニーズに合わせて簡単にモデルを調整できます。

**使用モデル**: google/gemma-3-4b-it  *(ゲート付きの場合は [HF 認証の有効化](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) を参照)*  
**ハードウェア**: ROCm 対応の AMD Radeon™ GPU  
**フレームワーク**: PyTorch + Hugging Face(Transformers、PEFT、Transformer Reinforcement Learning(TRL))

<!-- @device:halo,halo_box -->
> **注:** 
> - フル ファインチューニングには、少なくとも **64 GB のシステム RAM** が必要であり、そのうち少なくとも **32 GB は GPU が使用できる状態** である必要があります(この 32 GB は 64 GB の一部であり、追加分ではありません)。
> - 提供されているトレーニング スクリプト内のモデルを置き換えることで、**GPT-OSS-20B** を含む他のモデル アーキテクチャを試すこともできます。
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **注:** LoRA および QLoRA のファインチューニングには、少なくとも **32 GB のシステム RAM** が必要であり、そのうち少なくとも **16 GB は GPU が使用できる状態** である必要があります(この 16 GB は 32 GB の一部であり、追加分ではありません)。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRA のファインチューニングには、少なくとも **32 GB のシステム RAM** が必要であり、そのうち少なくとも **16 GB は GPU が使用できる状態** である必要があります(この 16 GB は 32 GB の一部であり、追加分ではありません)。
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** LoRA および QLoRA のファインチューニングには、少なくとも **16 GB の専用 GPU メモリ** と **32 GB のシステム RAM** を搭載したグラフィックス カードが必要です。
> - Linux では、トレーニングはグラフィックス カードの専用 VRAM 内で完全に実行されます。
> - VRAM が不足しても、共有 GPU メモリ(システム RAM)にフォールバックすることはありません。
> - 専用 VRAM が 16 GB 未満のカードは、システムに十分な RAM があっても、Linux 上でのトレーニング中にメモリ不足になります。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRA のファインチューニングには、少なくとも **16 GB の合計 GPU メモリ** と **32 GB のシステム RAM** が必要です。
> - Windows では、合計 GPU メモリは、グラフィックス カードの専用 VRAM と(システム RAM から借用される)共有 GPU メモリを合算したものです。
> - そのため、専用 VRAM が 16 GB 未満のカードでも、共有 GPU メモリで不足分を補うことで、このプレイブックを実行できます。
<!-- @os:end -->
<!-- @device:end -->

## このチュートリアルで学べること

- PyTorch と ROCm を使用して、LoRA、QLoRA、フル ファインチューニングで LLM をファインチューニングする方法
- ファインチューニング済みモデルを保存してデプロイする方法
- トレーニングを監視し、一般的な問題をデバッグする方法

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

#### 仮想環境を作成する

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
**ユーザーに GPU デバイスへのアクセス権を付与する**(有効にするには、一度ログアウトして再度ログインしてください):

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
**Windows:** ここではコア パッケージのみがテストおよびサポートされています。**bitsandbytes は Windows で十分にサポートされていない** ため、Windows 版のインストールでは bitsandbytes を省略しています。Windows では LoRA またはフル ファインチューニングを使用してください(QLoRA は bitsandbytes を必要とするため、Linux 向けです)。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF 認証を有効にする(ゲート付き / カスタム / 事前インストールされていないモデル)

この例では、**ゲート付き** モデルである **google/gemma-3-4b-it** を使用します。トレーニング スクリプトがこのモデルをダウンロードできるようにするには、Hugging Face 上でモデルの利用規約に同意した上で、認証を行う必要があります。

1. **ライセンスに同意する:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) を開き、サインイン(またはアカウントを作成)し、モデル ページで利用規約(例:「Agree and access repository」)に同意します。
2. **インストールしてログインする:** Hugging Face CLI をインストールし、標準的なログインを実行します:

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

**LoRA(Low-Rank Adaptation)** は、ベース モデルを凍結したまま、特定の層に追加される小さな「アダプター」行列のみをトレーニングします。

- **主な考え方**: 数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランクの更新(積が非常に少ないパラメータ数になる 2 つの小さな行列)を学習します。これにより、トレーニング対象パラメータ数と VRAM を大幅に削減しながら、フル ファインチューニングの品質の大部分を維持できます。

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

**QLoRA** は **4 ビット量子化** と **LoRA** を組み合わせた手法です。ベース モデルは 4 ビットでロードされ(大幅なメモリ節約)、LoRA アダプターのみがより高い精度でトレーニングされます。これにより、LoRA のパラメータ効率に加えて大幅に低い VRAM 使用量が得られますが、フル精度の LoRA と比較すると品質面でわずかなトレードオフがあります。4 ビット量子化は数値的な不安定性(損失のスパイクや NaN)を引き起こすことがあるため、十分な VRAM がある場合はユーザーが **LoRA** を好むことが多い点に注意してください。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注**: `openai/gpt-oss-20b` のような MXFP4 ベース モデルの場合、QLoRA ではなく **LoRA**(`train_lora.py`)を使用することを推奨します。QLoRA スクリプトの `bitsandbytes` 4 ビット パスは通常、MXFP4 の重みを BF16 に逆量子化するため、実行内容は標準的な LoRA と同様になります。ネイティブの MXFP4 を使用するには、ソースからビルドした `bitsandbytes` と、対応する Transformers/Triton/kernels スタックが必要です。詳細は [Transformers の MXFP4 ドキュメント](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4) を参照してください。

---
### 2. トレーニング方法の選択

| 方法 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linuxのみ） | 12-16GB | 最速 | 90-95% | メモリ使用量を抑えたい場合 |
| **LoRA** | 24-32GB | 高速 | 95-98% | バランスの取れたアプローチ |
| **Full** | 80GB以上 | 最も遅い | 100% | 最高品質 |

### 3. トレーニングの実行

**データセットとモデルが学習する内容**  
これらのスクリプトは、データセットをチャット形式の例に変換します。例えば、QLoRAスクリプトは**Abirate/english_quotes**を使用しており、各例は次のようなユーザー・アシスタントのペアになります。

- **User:** 「Give me a quote about: &lt;tag&gt;」
- **Assistant:** 「&lt;quote&gt; – &lt;author&gt;」

ファインチューニングによって、モデルはトピックに関する引用を求めるプロンプトに応答し、`<quote text> - <author>` という形式で返すことを学習します。LoRAおよびフルファインチューニングのスクリプトでは、**databricks/databricks-dolly-15k**（汎用的な指示・応答のペア）が使用されているため、正確なタスクはスクリプトによって異なります。ただし、基本的な考え方は同じで、選択したデータセットと形式にモデルを適応させることです。

以下は、利用可能なトレーニング方法の概要です。各方法はそれぞれのスクリプトへのリンクと、適切なアプローチを選ぶための簡単な説明を提供しています。

| スクリプト                           | 方法            | 説明                                                                                                         | 一般的なVRAM | 推奨対象                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ベースモデルを固定した状態で小さなアダプター行列をトレーニングします。3～5倍高速で、フル品質の約95～98%を実現します。                         | 24–32GB      | 上級ユーザー、複数のアダプター、より多くのVRAMが必要な場合    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linuxのみ)*             | **QLoRA**       | 4ビット量子化＋LoRAアダプターを使用します。メモリ使用量が最も少なく、最速で、品質のトレードオフはわずかです。`bitsandbytes`（Linuxのみ）が必要です。                            | 12–16GB      | ほとんどのユーザー、迅速な実験、限られたVRAMの場合      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **フルファインチューニング** | すべてのモデルパラメータを更新します。最高品質ですが、メモリと計算量の使用量が最も多くなります。                                    | 40GB以上        | 最高品質、研究用途、大容量VRAMを持つ場合           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** フルファインチューニング（`train_full_finetuning.py`）は、64GBを超えるシステムRAMを必要とする場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAまたはQLoRAの使用をご検討ください。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** フルファインチューニング（`train_full_finetuning.py`）は、64GBを超えるシステムRAMを必要とする場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAの使用をご検討ください。
<!-- @os:end -->
<!-- @device:end -->

好みの`Training method`を選択し、対応するスクリプトをダウンロードして、仮想環境を有効にした状態でコマンドを使用して実行してください。

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

### LoRA/QLoRAトレーニング後

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

### LoRAアダプターをベースモデルにマージする

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**注:**  
- モデルディレクトリ名（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）が、トレーニングで実際に出力されたフォルダと一致していることを確認してください。  
- QLoRAではなくLoRAを使用した場合は、パスを適宜置き換えてください。  
- 一部のGemmaモデルでは、`from_pretrained`に`trust_remote_code=True`を指定する必要があります。関連する警告が表示された場合は追加してください。

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

### 独自のデータセットの使用

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

**ローカルJSON/JSONLファイルのデータセット形式:**

この方法を使用する場合、解析エラーを避けるために、JSONファイルが正しく構造化されていることを確認してください。

以下のガイドラインに従う必要があります。
* **ファイルの形式:** JSONファイルは、適切な構造と構文を確保するために、統合開発環境（IDE）内でフォーマットする必要があります。
* **必須キー:** カスタムJSONファイルには、`instruction`および`response`のキーが含まれている必要があります。これらのキーは、メソッドが正しく機能するために不可欠です。
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
**Hugging Faceハブデータセットのデータセット形式**

Hugging Faceのデータセットを利用する場合、シームレスな統合を実現するために、データセットが正しく構造化されていることを確認してください。

以下のガイドラインに従ってください。
* **Instruction-Responseペア:** `instruction-response`のペアを含むデータセットに焦点を当ててください。この構造は、意図した機能を実現するために不可欠です。
* **カスタムキーの変更:** データセットが`instruction-response`の構造に準拠していない場合、`format_instruction()`関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応させることができます。

調整例: データセットの出力を調整する必要がある場合は、format_instruction()関数内のレスポンス部分を、要件に合わせて変更できます。
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSVファイルのデータセット形式**

CSVファイル形式を使用するスクリプトに対応するには、CSVファイルに`instruction`および`response`という名前の列が含まれていることを確認する必要があります。
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### トレーニングパラメータの調整

トレーニングスクリプトを編集し、目的に合わせて変数を変更してください: **学習率**（`LR`）、**エポック数**（`EPOCHS`）、**バッチサイズ**（`BATCH_SIZE`）、**勾配累積**（`GRAD_ACCUM_STEPS`）、およびLoRA/QLoRAの**ランク**（`LORA_R`）。より高速な実行にはエポック数を減らし、学習率（LR）を高く設定してください。より高品質な結果を得るには、エポック数を増やし、LRを低く設定してください。メモリ不足エラーが発生した場合は、バッチサイズまたはシーケンス長を減らしてください。
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

## モニタリングとデバッグ

### GPU メモリを監視する

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (オプション) Weights & Biases で実験を追跡する

実行結果とメトリクスを [Weights & Biases](https://wandb.ai) にログ記録するには:

```bash
pip install wandb
wandb login
```

トレーニング スクリプトでは、トレーナーの設定で `report_to="wandb"` を設定し、必要に応じて `run_name="your-experiment-name"` も設定します。Wandb を使用しない場合は、`report_to` をデフォルトのままにするか、`"none"` に設定してください。

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

**解決策:** メモリに余裕があればバッチサイズを増やす
```python
BATCH_SIZE = 8
```
## 次のステップ

ファインチューニングに成功したら、モデルをさらに活用するために、以下の次のステップを検討してください。

1. **評価**: 保留しておいたテストデータで十分に評価し、汎化性能を測定し、過学習を防ぎます。
2. **実験**: さまざまなハイパーパラメータの値を試し、精度、速度、メモリのトレードオフを最適化します。
3. **追跡**: 再現性のある研究のために、Weights & Biases であらゆる実験(および対応するメトリクス)を記録します。
4. **試行**: 独自のカスタム データセットでトレーニングを行い、ユース ケースに合わせてモデルを適応させます。
5. **デプロイ**: 互換性のあるハードウェア上で vLLM などの効率的なバックエンドを使用し、高速な推論のためにファインチューニング済みモデルをデプロイします。
6. **探求**: プロンプト エンジニアリング、混合精度、より長いシーケンス長などの高度な技術を試します。
7. **トレーニング**: 異なるタスクやドメイン向けに複数の LoRA アダプターをトレーニングし、必要に応じて切り替えます。

---