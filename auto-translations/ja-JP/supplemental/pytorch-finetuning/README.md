<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub ではレンダリングできない特殊タグを使用しています。コンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要

このチュートリアルでは、PyTorch と ROCm を使用して大規模言語モデル（LLM）をファインチューニングするためのステップバイステップの例を提供します。標準的なファインチューニングからメモリ効率の高いパラメータ効率ファインチューニング（PEFT）戦略まで、さまざまな手法を取り上げており、ニーズに合わせてモデルを簡単に適応させることができます。

**使用モデル**: google/gemma-3-4b-it  *（ゲートモデルの場合は [HF 認証を有効にする](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) を参照）*  
**ハードウェア**: ROCm 対応の AMD Radeon™ GPU  
**フレームワーク**: PyTorch + Hugging Face（Transformers、PEFT、Transformer Reinforcement Learning（TRL））

<!-- @device:halo,halo_box -->
> **注意:** 提供されているトレーニングスクリプトのモデルを置き換えることで、**GPT-OSS-20B** を含む他のモデルアーキテクチャも試すことができます。
> フルファインチューニングには、少なくとも 32 GB の GPU メモリと 64 GB のシステム RAM が必要です。
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **注意:** LoRA および QLoRA ファインチューニングには、少なくとも 16 GB の GPU メモリと 32 GB のシステム RAM が必要です。
<!-- @device:end -->

## 学習内容

- PyTorch と ROCm を使用して LoRA、QLoRA、およびフルファインチューニングで LLM をファインチューニングする方法
- ファインチューニングしたモデルを保存してデプロイする方法
- トレーニングを監視し、一般的な問題をデバッグする方法

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注意**: VS Code がインストールされていない場合は、Ryzen AI Developer Center でインストールできます。

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
**GPU デバイスへのユーザーアクセスを許可する**（有効にするにはログアウトして再度ログインしてください）:

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
**Windows:** ここではコアパッケージのみがテストおよびサポートされています。**bitsandbytes は Windows では十分にサポートされていない**ため、Windows インストールでは省略されています。Windows では LoRA またはフルファインチューニングを使用してください（QLoRA は bitsandbytes を必要とし、Linux 向けです）。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF 認証を有効にする（ゲートモデルまたはカスタム / 非プリインストールモデル）

この例では **google/gemma-3-4b-it** を使用します。これは**ゲート**モデルです。Hugging Face でモデルの利用規約に同意し、トレーニングスクリプトがダウンロードできるように認証を行う必要があります。

1. **ライセンスに同意する:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) を開き、サインイン（またはアカウントを作成）して、モデルページのライセンス/利用規約に同意します（例: 「Agree and access repository」）。
2. **インストールとログイン:** Hugging Face CLI をインストールし、標準のログインを実行します:

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

## 手法の理解

### LoRA とは？

**LoRA（Low-Rank Adaptation）** はベースモデルを凍結したまま、特定のレイヤーに追加される小さな「アダプター」行列のみをトレーニングします。

- **核心的なアイデア**: 数百万のパラメータを持つ巨大な重み行列を更新する代わりに、低ランクの更新（積がはるかに少ないパラメータを持つ 2 つの小さな行列）を学習します。これにより、フルファインチューニングの品質をほぼ維持しながら、トレーニング可能なパラメータと VRAM を大幅に削減できます。

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

**QLoRA** は **4 ビット量子化**と **LoRA** を組み合わせたものです。ベースモデルは 4 ビットでロードされ（大幅なメモリ節約）、LoRA アダプターのみが高精度でトレーニングされます。これにより、LoRA のパラメータ効率に加えて VRAM を大幅に削減できますが、フル精度の LoRA と比較してわずかな品質のトレードオフがあります。4 ビット量子化は数値的な不安定性（損失スパイクや NaN）を引き起こす可能性があるため、十分な VRAM がある場合はユーザーが **LoRA** を好む場合が多いです。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注意**: `openai/gpt-oss-20b` のような MXFP4 ベースモデルには、QLoRA の代わりに **LoRA**（`train_lora.py`）の使用を推奨します。QLoRA スクリプトの `bitsandbytes` 4 ビットパスは通常、MXFP4 の重みを BF16 に逆量子化するため、実行は標準的な LoRA と同様に動作します。ネイティブ MXFP4 には、ソースからビルドされた `bitsandbytes` と対応する Transformers/Triton/カーネルスタックが必要です。[Transformers MXFP4 ドキュメント](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)を参照してください。

---

### 2. 手法を選択する

| 手法 | メモリ | 速度 | 品質 | 最適な用途 |
|--------|--------|-------|---------|----------|
| **QLoRA**（Linux のみ） | 12〜16GB | 最速 | 90〜95% | 低メモリ使用量 |
| **LoRA** | 24〜32GB | 高速 | 95〜98% | バランスの取れたアプローチ |
| **フル** | 80GB 以上 | 最低速 | 100% | 最高品質 |

### 3. トレーニングを実行する

**データセットとモデルが学習する内容**  
スクリプトはデータセットをチャット例に変換します。たとえば、QLoRA スクリプトは **Abirate/english_quotes** を使用します。各例は次のようなユーザーとアシスタントのペアになります:

- **ユーザー:** 「&lt;タグ&gt; についての引用を教えてください」
- **アシスタント:** 「&lt;引用&gt; – &lt;著者&gt;」

ファインチューニングにより、モデルはトピックに関する引用を求めるプロンプトに応答し、`<引用テキスト> - <著者>` の形式で返すことを学習します。LoRA とフルファインチューニングのスクリプトは **databricks/databricks-dolly-15k**（一般的な指示/応答ペア）を使用するため、正確なタスクはスクリプトによって異なります。基本的な考え方は同じで、選択したデータセットと形式にモデルを適応させます。

以下は利用可能なトレーニング手法の概要です。各手法はそのスクリプトにリンクされており、適切なアプローチを選択するための簡単な説明が記載されています。

| スクリプト | 手法 | 説明 | 典型的な VRAM | 推奨対象 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | ベースモデルを凍結しながら小さなアダプター行列をトレーニング。3〜5 倍高速、フル品質の約 95〜98%。 | 24〜32GB | 上級ユーザー、複数のアダプター、より多くの VRAM |
| [`train_qlora.py`](assets/train_qlora.py) *（Linux のみ）* | **QLoRA** | 4 ビット量子化 + LoRA アダプター。最低メモリ使用量、最速、わずかな品質のトレードオフ。`bitsandbytes` が必要（Linux のみ）。 | 12〜16GB | ほとんどのユーザー、高速な実験、限られた VRAM |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **フルファインチューニング** | すべてのモデルパラメータを更新。最高品質、最高のメモリとコンピューティング使用量。 | 40GB 以上 | 最高品質、研究、大容量 VRAM |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注意:** フルファインチューニング（`train_full_finetuning.py`）は 64GB 以上のシステム RAM を必要とする場合があり、このデバイスでは実行できない可能性があります。代わりに LoRA または QLoRA の使用を検討してください。
<!-- @os:end -->

<!-- @os:windows -->
> **注意:** フルファインチューニング（`train_full_finetuning.py`）は 64GB 以上のシステム RAM を必要とする場合があり、このデバイスでは実行できない可能性があります。代わりに LoRA の使用を検討してください。
<!-- @os:end -->
<!-- @device:end -->

仮想環境をアクティブにした状態で、希望する `トレーニング手法` を選択し、対応するスクリプトをダウンロードして次のコマンドで実行します:

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

**注意:**  
- モデルディレクトリ名（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）がトレーニングの実際の出力フォルダと一致していることを確認してください。  
- QLoRA の代わりに LoRA を使用した場合は、パスを適宜置き換えてください。  
- 一部の Gemma モデルでは `from_pretrained` で `trust_remote_code=True` を指定する必要があります。関連する警告が表示された場合は追加してください。

パディングトークン、デバイスなどのカスタム設定については、トレーニングに使用したスクリプトを参照してください。

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

すべてのスクリプトは同じデータセット形式を使用します。読み込みセクションを置き換えてください:

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

以下のガイドラインに従う必要があります:
* **ファイルのフォーマット:** JSON ファイルは、適切な構造と構文を確保するために統合開発環境（IDE）内でフォーマットする必要があります。
* **必須キー:** カスタム JSON ファイルには `instruction` と `response` のキーが含まれている必要があります。これらのキーはメソッドが正しく機能するために不可欠です。
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

Hugging Face のデータセットを利用する場合は、シームレスな統合を促進するためにデータセットが正しく構造化されていることを確認してください。

以下のガイドラインに従ってください:
* **指示と応答のペア:** `instruction-response` ペアを含むデータセットに焦点を当ててください。この構造は意図した機能に不可欠です。
* **カスタムキーの変更:** データセットが `instruction-response` 構造に準拠していない場合は、`format_instruction()` 関数を変更するオプションがあります。これにより、必要に応じて特定のキーに対応できます。

調整の例: データセットの出力を調整する必要がある場合は、`format_instruction()` 関数内の応答セクションを要件に合わせて変更できます。
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

CSV ファイル形式を使用するスクリプトに対応するには、CSV ファイルに `instruction` と `response` という名前の列が含まれていることを確認する必要があります。
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### トレーニングパラメータを調整する

トレーニングスクリプトを編集し、目標に合わせて変数を変更します: **学習率**（`LR`）、**エポック数**（`EPOCHS`）、**バッチサイズ**（`BATCH_SIZE`）、**勾配累積**（`GRAD_ACCUM_STEPS`）、LoRA/QLoRA の場合は**ランク**（`LORA_R`）。高速な実行にはエポック数を減らして学習率（LR）を高くし、より良い品質にはエポック数を増やして LR を低くします。メモリ不足エラーが発生した場合はバッチサイズまたはシーケンス長を減らしてください。

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

**4. 勾配チェックポイントを有効にする（フルファインチューニングのみ）:**
```python
model.gradient_checkpointing_enable()
```

---

## 監視とデバッグ

### GPU メモリを監視する

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### （オプション）Weights & Biases で実験を追跡する

実行とメトリクスを [Weights & Biases](https://wandb.ai) に記録するには:

```bash
pip install wandb
wandb login
```

トレーニングスクリプトで、トレーナー設定の `report_to="wandb"` を設定し、オプションで `run_name="your-experiment-name"` を設定します。Wandb を使用しない場合は、`report_to` をデフォルトのままにするか、`"none"` に設定してください。

### 一般的な問題

#### メモリ不足（OOM）

**解決策:** バッチサイズを減らすか、QLoRA を使用する
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

**解決策:** メモリが許す場合はバッチサイズを増やす
```python
BATCH_SIZE = 8
```
## 次のステップ

ファインチューニングが正常に完了したら、モデルをさらに活用するために以下の次のステップを検討してください:

1. **評価:** 汎化性能を測定し過学習を避けるために、保留されたテストデータで徹底的に評価する。
2. **実験:** 精度、速度、メモリのトレードオフを改善するために、さまざまなハイパーパラメータ値を試す。
3. **追跡:** 再現可能な研究のために、すべての実験（および対応するメトリクス）を Weights & Biases で追跡する。
4. **試行:** 独自のカスタムデータセットでトレーニングして、ユースケースに特化したモデルに適応させる。
5. **デプロイ:** 互換性のあるハードウェアで vLLM などの効率的なバックエンドを使用して、ファインチューニングしたモデルを高速推論のためにデプロイする。
6. **探索:** プロンプトエンジニアリング、混合精度、より長いシーケンス長などの高度な手法を探索する。
7. **トレーニング:** 異なるタスクやドメイン向けに複数の LoRA アダプターをトレーニングし、必要に応じて切り替える。

---