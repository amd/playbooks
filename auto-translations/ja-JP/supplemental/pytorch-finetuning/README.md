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

このチュートリアルでは、PyTorchとROCmを使用して大規模言語モデル（LLM）をファインチューニングするためのステップバイステップの例を提供します。標準的なファインチューニングから、メモリ効率の良いパラメータ効率的ファインチューニング（PEFT）戦略まで、いくつかの手法をカバーしており、ニーズに合わせてモデルを簡単に適応させることができます。

**使用モデル**: google/gemma-3-4b-it  *(ゲート付きの場合は[HF認証の有効化](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models)を参照)*  
**ハードウェア**: ROCm対応のAMD Radeon™ GPU  
**フレームワーク**: PyTorch + Hugging Face（Transformers、PEFT、Transformer Reinforcement Learning（TRL））

<!-- @device:halo,halo_box -->
> **注:** 
> - フル ファインチューニングには、少なくとも**64 GBのシステムRAM**が必要で、そのうち少なくとも**32 GBがGPUで使用可能**である必要があります（この32 GBは64 GBの一部であり、追加で必要になるわけではありません）。
> - 提供されているトレーニングスクリプト内のモデルを置き換えることで、**GPT-OSS-20B**を含む他のモデルアーキテクチャを試すこともできます。
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **注:** LoRAおよびQLoRAファインチューニングには、少なくとも**32 GBのシステムRAM**が必要で、そのうち少なくとも**16 GBがGPUで使用可能**である必要があります（この16 GBは32 GBの一部であり、追加で必要になるわけではありません）。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRAファインチューニングには、少なくとも**32 GBのシステムRAM**が必要で、そのうち少なくとも**16 GBがGPUで使用可能**である必要があります（この16 GBは32 GBの一部であり、追加で必要になるわけではありません）。
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** LoRAおよびQLoRAファインチューニングには、少なくとも**16 GBの専用GPUメモリ**と**32 GBのシステムRAM**を搭載したグラフィックカードが必要です。
> - Linuxでは、トレーニングはグラフィックカードの専用VRAM内で完全に実行されます。
> - VRAMが不足しても、共有GPUメモリ（システムRAM）にフォールバックすることはありません。
> - 専用VRAMが16 GB未満のカードは、システムに十分なRAMがあっても、Linuxでのトレーニング中にメモリ不足になります。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** LoRAファインチューニングには、少なくとも**16 GBの合計GPUメモリ**と**32 GBのシステムRAM**が必要です。
> - Windowsでは、合計GPUメモリはグラフィックカードの専用VRAMと共有GPUメモリ（システムRAMから借用）を組み合わせたものです。
> - そのため、専用VRAMが16 GB未満のカードでも、共有GPUメモリを使用して不足分を補うことで、このプレイブックを実行できます。
<!-- @os:end -->
<!-- @device:end -->

## 学習内容

- PyTorchとROCmを使用して、LoRA、QLoRA、フル ファインチューニングによりLLMをファインチューニングする方法
- ファインチューニングしたモデルを保存およびデプロイする方法
- トレーニングを監視し、一般的な問題をデバッグする方法

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注**: VS Codeがインストールされていない場合は、Ryzen AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

#### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**ユーザーにGPUデバイスへのアクセス権を付与します**（これを有効にするには、ログアウトして再度ログインしてください）:

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
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
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** ここではコアパッケージのみがテストおよびサポートされています。**bitsandbytesはWindowsでは十分にサポートされていない**ため、Windows版のインストールには含まれていません。Windowsでは、LoRAまたはフル ファインチューニングを使用してください（QLoRAはbitsandbytesを必要とし、Linux向けです）。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF認証を有効にする（ゲート付きまたはカスタム／非プリインストールモデル）

この例では、**ゲート付き**モデルである**google/gemma-3-4b-it**を使用します。トレーニングスクリプトがこのモデルをダウンロードできるようにするには、Hugging Face上でモデルの利用規約に同意した上で認証を行う必要があります。

1. **ライセンスへの同意:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)を開き、サインイン（またはアカウントを作成）した後、モデルページでライセンス／利用規約に同意します（例:「Agree and access repository」）。
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

## 各手法について理解する

### LoRAとは？

**LoRA（Low-Rank Adaptation）**は、ベースモデルを凍結したまま、特定のレイヤーに追加される小さな「アダプター」行列のみを学習します。

- **重要な考え方**: 数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランクの更新（積がはるかに少ないパラメータを持つ2つの小さな行列）を学習します。これにより、フル ファインチューニングの品質のほとんどを維持しながら、学習可能なパラメータとVRAMを大幅に削減できます。

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRAとは？

**QLoRA**は、**4ビット量子化**と**LoRA**を組み合わせたものです。ベースモデルは4ビットで読み込まれ（メモリを大幅に節約）、LoRAアダプターのみがより高い精度でトレーニングされます。そのため、LoRAのパラメータ効率に加えて、はるかに低いVRAM使用量を実現できますが、フル精度のLoRAと比較すると品質面で若干のトレードオフがあります。4ビット量子化は数値的な不安定性（損失のスパイクやNaN）を引き起こす可能性があるため、VRAMが十分にある場合はユーザーが**LoRA**を選択することも多いことに注意してください。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注**: `openai/gpt-oss-20b`のようなMXFP4ベースモデルの場合、QLoRAではなく**LoRA**（`train_lora.py`）を使用することをお勧めします。QLoRAスクリプトの`bitsandbytes` 4ビットパスは、通常MXFP4の重みをBF16に逆量子化するため、実行時の動作は標準的なLoRAと同様になります。ネイティブのMXFP4を使用するには、ソースからビルドした`bitsandbytes`に加えて、対応するTransformers/Triton/kernelsスタックが必要です。詳細は[Transformers MXFP4ドキュメント](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)を参照してください。

---
### 2. トレーニング方法を選択する

| 方法 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linuxのみ） | 12-16GB | 最速 | 90-95% | 低メモリ使用量 |
| **LoRA** | 24-32GB | 高速 | 95-98% | バランスの取れたアプローチ |
| **Full** | 80GB+ | 最も遅い | 100% | 最大限の品質 |

### 3. トレーニングを実行する

**データセットとモデルが学習する内容**  
これらのスクリプトは、データセットをチャット形式の例に変換します。例えば、QLoRAスクリプトは**Abirate/english_quotes**を使用しており、各例は次のようなユーザー・アシスタントのペアになります。

- **User:** 「Give me a quote about: &lt;tag&gt;」
- **Assistant:** 「&lt;quote&gt; – &lt;author&gt;」

ファインチューニングにより、モデルはトピックに関する名言を求めるプロンプトに応答し、`<quote text> - <author>`という形式でそれらを返すことを学習します。LoRAおよびフルファインチューニングのスクリプトでは、**databricks/databricks-dolly-15k**（一般的な指示・応答のペア）を使用しているため、正確なタスクはスクリプトによって異なりますが、考え方は同じです。選択したデータセットと形式にモデルを適応させます。

以下は、利用可能なトレーニング方法の概要です。それぞれの方法はスクリプトへのリンクと、適切なアプローチを選ぶための簡単な説明を提供しています。

| スクリプト                           | 方法            | 説明                                                                                                         | 一般的なVRAM | 推奨用途                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ベースモデルを凍結したまま小さなアダプター行列をトレーニングします。3～5倍高速で、フル品質の約95～98%を実現します。                         | 24–32GB      | 上級ユーザー向け。複数のアダプター使用時、より多くのVRAMがある場合    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linuxのみ)*             | **QLoRA**       | 4ビット量子化＋LoRAアダプター。最も少ないメモリ使用量で最速。わずかな品質のトレードオフがあります。`bitsandbytes`が必要です（Linuxのみ）。                            | 12–16GB      | ほとんどのユーザー向け。高速な実験、限られたVRAMの場合      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **フルファインチューニング** | すべてのモデルパラメータを更新します。最大限の品質を提供しますが、メモリと計算量の使用量が最も高くなります。                                    | 40GB+        | 最大限の品質が必要な場合。研究用途、大容量のVRAMがある場合           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注:** フルファインチューニング（`train_full_finetuning.py`）には64GBを超えるシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAまたはQLoRAの使用を検討してください。
<!-- @os:end -->

<!-- @os:windows -->
> **注:** フルファインチューニング（`train_full_finetuning.py`）には64GBを超えるシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAの使用を検討してください。
<!-- @os:end -->
<!-- @device:end -->

希望する`Training method`を選択し、対応するスクリプトをダウンロードして、仮想環境をアクティブにしたまま以下のコマンドを使用して実行します。

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
- モデルディレクトリ名（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）が、トレーニングによって実際に出力されたフォルダと一致していることを確認してください。  
- QLoRAではなくLoRAを使用した場合は、パスを適宜置き換えてください。  
- 一部のGemmaモデルでは、`from_pretrained`に`trust_remote_code=True`を指定する必要があります。関連する警告が表示された場合は追加してください。

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
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

**ローカルJSON/JSONLファイルのデータセット形式:**

この方法を使用する場合、解析エラーを避けるためにJSONファイルが正しく構造化されていることを確認してください。 

以下のガイドラインに従う必要があります。
* **ファイル形式:** JSONファイルは、適切な構造と構文を確保するために、統合開発環境（IDE）内でフォーマットする必要があります。
* **必須キー:** カスタムJSONファイルには`instruction`および`response`キーが含まれている必要があります。これらのキーは、この方法が正しく機能するために不可欠です。
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
**Hugging Face Hubデータセットのデータセット形式**

Hugging Faceのデータセットを利用する場合、シームレスな統合を促進するために、データセットが正しく構造化されていることを確認してください。 

以下のガイドラインに従う必要があります。
* **指示・応答ペア:** `instruction-response`ペアを含むデータセットに焦点を当ててください。この構造は、意図した機能にとって不可欠です。
* **カスタムキーの変更:** データセットが`instruction-response`構造に準拠していない場合、`format_instruction()`関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応できます。

調整例: データセットの出力を調整する必要がある場合は、要件に合わせて`format_instruction()`関数内の応答セクションを変更できます。
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

CSVファイル形式を使用するスクリプトに対応させるには、CSVファイルに`instruction`および`response`という名前の列が含まれていることを確認する必要があります。 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### トレーニングパラメータを調整する

トレーニングスクリプトを編集し、目的に合わせて変数を変更します。**学習率**（`LR`）、**エポック数**（`EPOCHS`）、**バッチサイズ**（`BATCH_SIZE`）、**勾配累積**（`GRAD_ACCUM_STEPS`）、そしてLoRA/QLoRAの場合は**ランク**（`LORA_R`）です。より高速な実行には、エポック数を少なく、学習率（LR）を高く設定してください。より高い品質を得るには、エポック数を多く、LRを低く設定してください。メモリ不足エラーが発生した場合は、バッチサイズまたはシーケンス長を減らしてください。
### メモリ最適化のヒント

メモリ不足エラーが発生した場合:

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

### GPU メモリの監視

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (オプション) Weights & Biases による実験の追跡

[Weights & Biases](https://wandb.ai) にランとメトリクスをログするには:

```bash
pip install wandb
wandb login
```

トレーニングスクリプトでは、トレーナー設定内で `report_to="wandb"` を設定し、必要に応じて `run_name="your-experiment-name"` も設定してください。Wandb を使用したくない場合は、`report_to` をデフォルトのままにするか `"none"` に設定してください。

### よくある問題

#### メモリ不足 (OOM)

**解決策:** バッチサイズを減らす、または QLoRA を使用する
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

ファインチューニングに成功したら、モデルをさらに活用するために以下の次のステップを検討してください:

1. ホールドアウトのテストデータで十分に**評価**を行い、汎化性能を測定し、過学習を回避します。
2. 精度、速度、メモリのトレードオフを改善するために、さまざまなハイパーパラメータ値を試して**実験**します。
3. 再現可能な研究のために、Weights & Biases ですべての実験(および対応するメトリクス)を**追跡**します。
4. 独自のカスタムデータセットでトレーニングを**試し**、ユースケースに合わせてモデルを特化させます。
5. vLLM などの効率的なバックエンドを使用して、互換性のあるハードウェア上で高速な推論のためにファインチューニング済みモデルを**デプロイ**します。
6. プロンプトエンジニアリング、混合精度、より長いシーケンス長などの高度な技術を**探求**します。
7. 異なるタスクやドメイン向けに複数の LoRA アダプターを**トレーニング**し、必要に応じて切り替えます。

---