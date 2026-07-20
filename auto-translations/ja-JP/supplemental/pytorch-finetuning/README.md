<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> このプレイブックには、GitHub ではレンダリングできない特殊なタグが使用されています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) にアクセスしてください。
<!-- @github-only:end -->

## 概要

このチュートリアルでは、PyTorch と ROCm を使用して大規模言語モデル（LLM）をファインチューニングするための手順を段階的に紹介します。標準的なファインチューニングから、メモリ効率の高い Parameter-Efficient Fine-Tuning（PEFT）戦略まで、いくつかの手法を取り上げているため、モデルをニーズに合わせて簡単に適応させることができます。

**使用モデル**：google/gemma-3-4b-it  *（ゲートされている場合は [HF 認証を有効にする](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) を参照）*  
**ハードウェア**：ROCm に対応した AMD Radeon™ GPU  
**フレームワーク**：PyTorch + Hugging Face（Transformers、PEFT、Transformer Reinforcement Learning（TRL））

<!-- @device:halo,halo_box -->
> **注：** 提供されているトレーニングスクリプト内のモデルを置き換えることで、**GPT-OSS-20B** を含む他のモデルアーキテクチャも試すことができます。
> フルファインチューニングには、少なくとも 32 GB の GPU メモリと 64 GB のシステム RAM が必要です。
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **注：** LoRA および QLoRA によるファインチューニングには、少なくとも 16 GB の GPU メモリと 32 GB のシステム RAM が必要です。
<!-- @device:end -->

## このチュートリアルで学べること

- PyTorch と ROCm を使用して、LoRA、QLoRA、フルファインチューニングにより LLM をファインチューニングする方法
- ファインチューニング済みモデルを保存してデプロイする方法
- トレーニングを監視し、よくある問題をデバッグする方法

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注**：VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

#### 仮想環境を作成する

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
**ユーザーに GPU デバイスへのアクセス権を付与します**（これを有効にするには、一度ログアウトして再度ログインしてください）：

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

#### 基本的な依存関係をインストールする
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
**Windows：** ここではコアパッケージのみがテストおよびサポートされています。**bitsandbytes は Windows ではあまりサポートされていない**ため、Windows 版のインストールでは省略されています。Windows では LoRA またはフルファインチューニングを使用してください（QLoRA は bitsandbytes を必要とし、Linux を対象としています）。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF 認証を有効にする（ゲートされたモデルまたはカスタム／事前インストールされていないモデル）

この例では、**ゲートされた**モデルである **google/gemma-3-4b-it** を使用します。トレーニングスクリプトがこのモデルをダウンロードできるようにするには、Hugging Face 上でモデルの利用規約に同意した上で認証を行う必要があります。

1. **ライセンスに同意する：** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) を開き、サインイン（またはアカウントを作成）し、モデルページでライセンス／利用規約に同意します（例：「Agree and access repository」）。
2. **インストールしてログインする：** Hugging Face CLI をインストールし、標準のログインを実行します：

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

## 各手法を理解する

### LoRA とは？

**LoRA（Low-Rank Adaptation）** は、ベースモデルを固定したまま、特定のレイヤーに追加される小さな「アダプター」行列のみをトレーニングします。

- **キーとなる考え方**：数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランクな更新（積を取るとパラメータ数がはるかに少なくなる2つの小さな行列）を学習します。これにより、フルファインチューニングの品質の大部分を維持しながら、トレーニング可能なパラメータ数と VRAM を大幅に削減できます。

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

**QLoRA** は、**4ビット量子化** と **LoRA** を組み合わせたものです。ベースモデルは 4 ビットで読み込まれ（メモリの大幅な節約になります）、LoRA アダプターのみがより高い精度でトレーニングされます。これにより、LoRA のパラメータ効率に加えて、はるかに低い VRAM 使用量が得られますが、フル精度の LoRA と比較すると若干の品質のトレードオフがあります。4ビット量子化は数値的な不安定性（損失のスパイクや NaN）を引き起こす可能性があるため、十分な VRAM がある場合はユーザーが **LoRA** を選ぶことが多い点に注意してください。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注**：`openai/gpt-oss-20b` のような MXFP4 ベースモデルの場合、QLoRA ではなく **LoRA**（`train_lora.py`）を使用することをお勧めします。QLoRA スクリプトの `bitsandbytes` 4ビットパスは通常、MXFP4 の重みを BF16 に逆量子化するため、実行は標準的な LoRA と同様の動作になります。ネイティブの MXFP4 を利用するには、ソースからビルドした `bitsandbytes` と、対応する Transformers／Triton／kernels スタックが必要です。詳細は [Transformers MXFP4 のドキュメント](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4) を参照してください。

---

### 2. 手法を選択する

| 手法 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linux のみ） | 12〜16GB | 最速 | 90〜95% | メモリ使用量を抑えたい場合 |
| **LoRA** | 24〜32GB | 高速 | 95〜98% | バランスの取れたアプローチ |
| **Full** | 80GB 以上 | 最も低速 | 100% | 最高品質を求める場合 |
### 3. トレーニングを実行する

**データセットとモデルが学習する内容**
これらのスクリプトは、データセットをチャット形式の例に変換します。例えば、QLoRA スクリプトは **Abirate/english_quotes** を使用しており、各例は次のようなユーザーとアシスタントのペアになります。

- **User:** 「Give me a quote about: &lt;tag&gt;」
- **Assistant:** 「&lt;quote&gt; – &lt;author&gt;」

ファインチューニングにより、モデルはあるトピックに関する引用を求めるプロンプトに応答し、`<quote text> - <author>` という形式で返すことを学習します。LoRA と完全ファインチューニングのスクリプトは **databricks/databricks-dolly-15k**（一般的な指示・応答のペア）を使用するため、正確なタスクはスクリプトによって異なりますが、考え方は同じです。選択したデータセットと形式にモデルを適応させます。

以下は、利用可能なトレーニング手法の概要です。各手法には該当スクリプトへのリンクがあり、適切な手法を選ぶための簡単な説明が付いています。

| Script                           | Method            | Description                                                                                                         | Typical VRAM | Recommended For                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | 小さなアダプター行列をトレーニングし、ベースモデルは凍結します。3〜5倍高速で、フル品質の約95〜98%を実現します。                         | 24–32GB      | 上級ユーザー向け。複数のアダプターを使用する場合や、VRAM に余裕がある場合    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux only)*             | **QLoRA**       | 4ビット量子化と LoRA アダプターを組み合わせた手法です。メモリ使用量が最も少なく、最速で、品質の低下もわずかです。`bitsandbytes`（Linux のみ）が必要です。                            | 12–16GB      | ほとんどのユーザー向け。高速な実験や、VRAM が限られている場合      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | すべてのモデルパラメータを更新します。品質は最大ですが、メモリと計算コストが最も高くなります。                                    | 40GB+        | 最高品質が求められる場合。研究用途。大容量 VRAM が利用可能な場合           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Note:** 完全ファインチューニング（`train_full_finetuning.py`）には64GB以上のシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAまたはQLoRAの使用をご検討ください。
<!-- @os:end -->

<!-- @os:windows -->
> **Note:** 完全ファインチューニング（`train_full_finetuning.py`）には64GB以上のシステムRAMが必要になる場合があり、このデバイスでは実行できない可能性があります。代わりにLoRAの使用をご検討ください。
<!-- @os:end -->
<!-- @device:end -->

任意の `Training method` を選択し、対応するスクリプトをダウンロードして、仮想環境を有効にしたまま次のコマンドで実行してください。

```python
python3 train_<method_name>.py.
```

## ファインチューニング済みモデルの使用

### 完全ファインチューニング後

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

**Note:**
- モデルディレクトリ名（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）が、トレーニングによって実際に生成された出力フォルダと一致していることを確認してください。
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

すべてのスクリプトは同じデータセット形式を使用します。読み込み部分を次のように置き換えてください。

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

この方法を使用する場合、パースエラーを避けるために JSON ファイルが正しく構造化されていることを確認してください。

以下のガイドラインに従う必要があります。
* **ファイル形式:** JSON ファイルは、適切な構造と構文を確保するために、統合開発環境（IDE）内でフォーマットする必要があります。
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

Hugging Face のデータセットを利用する場合、スムーズに統合できるよう、データセットが正しく構造化されていることを確認してください。

以下のガイドラインに従ってください。
* **Instruction-Response ペア:** `instruction-response` ペアを含むデータセットを使用してください。この構造は、意図した機能を実現するために不可欠です。
* **カスタムキーの変更:** データセットが `instruction-response` の構造に従っていない場合は、`format_instruction()` 関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応できます。

調整例: データセットの出力を調整する必要がある場合は、要件に合わせて format_instruction() 関数内の応答部分を変更できます。
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

トレーニングスクリプトを編集し、目的に合わせて変数を変更してください。**学習率**（`LR`）、**エポック数**（`EPOCHS`）、**バッチサイズ**（`BATCH_SIZE`）、**勾配累積**（`GRAD_ACCUM_STEPS`）、そして LoRA/QLoRA の場合は**ランク**（`LORA_R`）です。より高速に実行するにはエポック数を減らし学習率（LR）を上げ、品質を重視する場合はエポック数を増やし LR を下げてください。メモリ不足エラーが発生した場合は、バッチサイズまたはシーケンス長を減らしてください。

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

**4. 勾配チェックポインティングを有効にする（完全ファインチューニングのみ）:**
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

### (オプション) Weights & Biasesで実験をトラッキングする

実行結果とメトリクスを[Weights & Biases](https://wandb.ai)に記録するには:

```bash
pip install wandb
wandb login
```

トレーニングスクリプトでは、トレーナーの設定内で`report_to="wandb"`を設定し、必要に応じて`run_name="your-experiment-name"`も設定してください。Wandbを使用しない場合は、`report_to`をデフォルトのままにするか、`"none"`に設定してください。

### よくある問題

#### メモリ不足 (OOM)

**解決策:** バッチサイズを減らす、および/またはQLoRAを使用する
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

ファインチューニングが成功したら、モデルをさらに活用するために、以下の次のステップを検討してください。

1. **評価**: 未使用のテストデータで十分に評価を行い、汎化性能を測定し、過学習を回避します。
2. **実験**: 精度、速度、メモリのトレードオフを改善するために、さまざまなハイパーパラメータ値を試します。
3. **トラッキング**: 再現性のある研究のために、Weights & Biasesですべての実験(および対応するメトリクス)を記録します。
4. **試行**: 独自のカスタムデータセットでトレーニングを行い、ユースケースに合わせてモデルを適応させます。
5. **デプロイ**: 互換性のあるハードウェア上でvLLMなどの効率的なバックエンドを使用して、ファインチューニング済みモデルを高速な推論のためにデプロイします。
6. **探求**: プロンプトエンジニアリング、混合精度、より長いシーケンス長など、高度な手法を試します。
7. **トレーニング**: 異なるタスクやドメイン向けに複数のLoRAアダプターをトレーニングし、必要に応じて切り替えます。

---