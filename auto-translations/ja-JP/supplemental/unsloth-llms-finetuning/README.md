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

このプレイブックでは、AMDハードウェア上でUnslothを使用してローカルで言語モデルをファインチューニングする方法を紹介します。

`unsloth/gemma-4-E4B-it`に対して、`mlabonne/FineTome-100k`データセットのサブセットを使用した、LoRAアダプタによる短いSupervised Fine-Tuning（SFT）の例を使用します。目標は、セットアップ、トレーニング、推論、そしてファインチューニング結果の保存をカバーする、シンプルなエンドツーエンドのワークフローを提供することです。

この例は実用的で修正しやすいように設計されているため、独自のデータセットやモデルのための出発点として利用できます。

## 学べること

- Unslothの環境のセットアップ方法
- UnslothでSFTを使用してLLMをファインチューニングする方法
- ファインチューニング結果をローカルストレージに保存する方法

<!-- @device:halo,stx,krk -->
> **注記：** このプレイブックのファインチューニング手法には、少なくとも**64 GBのシステムRAM**が必要で、そのうち少なくとも**24 GBがGPUで利用可能**である必要があります（この24 GBは64 GBの一部であり、64 GBに加えて追加で必要というわけではありません）。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注記：** このプレイブックのファインチューニング手法には、少なくとも**24 GBの合計GPUメモリ**と**32 GBのシステムRAM**が必要です。
> - Windowsでは、合計GPUメモリは、グラフィックカード専用のVRAMと（システムRAMから借用した）共有GPUメモリを合わせたものです。
> - そのため、専用VRAMが24 GB未満のカードでも、共有GPUメモリでその差を補うことで、このプレイブックを実行できます。
<!-- @os:end -->

<!-- @os:linux -->
> **注記：** このプレイブックのファインチューニング手法には、少なくとも**24 GBの専用GPUメモリ**と**32 GBのシステムRAM**を備えたグラフィックカードが必要です。
> - Linuxでは、トレーニングはグラフィックカードの専用VRAM内で完全に実行されます。
> - VRAMが不足しても、共有GPUメモリ（システムRAM）にフォールバックすることはありません。
> - 専用VRAMが24 GB未満のカードは、システムに十分なRAMがあっても、Linuxでのトレーニング中にメモリ不足になります。
<!-- @os:end -->
<!-- @device:end -->

## Unslothを使う理由

Unslothは、標準的なセットアップと比較してメモリ使用量を削減し、トレーニングを高速化することで、LLMのファインチューニングをローカルハードウェア上でより簡単に実行できるようにします。

このプレイブックでは、Unslothを**LoRAベースのSFT**と組み合わせて使用します。つまり、ベースモデルはほぼ凍結されたままで、はるかに少ない数のアダプタウェイトのセットがトレーニングされます。これは、完全なファインチューニングよりも軽量で反復がより速いため、ローカル開発に適した方法です。

Unslothは、QLoRAや強化学習ワークフローを含む他のトレーニング手法もサポートしています。このプレイブックでは、まず最もシンプルな道筋、つまりユーザーが実行、理解、拡張できる小規模なLoRAファインチューニングの例に焦点を当てます。

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注記**：VS Codeがインストールされていない場合は、Ryzen AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
ターミナルを開き、AMD ROCm™ソフトウェアとPyTorchがすでにインストールされたvenvを作成します：
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPUデバイスへのユーザーアクセスを許可します**（これを有効にするには、一度ログアウトして再度ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

ターミナルを開き、venvを作成します：
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **注記：** Windowsの場合はPython 3.13が必要です。

<!-- @device:halo_box -->
PowerShellターミナルを開き、仮想環境を作成します：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
PowerShellターミナルを開き、仮想環境を作成します：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### 基本的な依存関係のインストール
<!-- @require:driver -->

> **重要：** Unslothは、ROCm 10に付属するPyTorch 2.13ビルドをまだサポートしていません。このプレイブックでは、以下のコマンドを使用して**PyTorch 2.12を搭載したROCm 7.14**をインストールしてください。ROCm 10 / PyTorch 2.13パッケージは使用しないでください。

作成した仮想環境に**AMD ROCm™ソフトウェアサポート付きのPyTorchをインストール**します：

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

その他のデバイスについては、完全な手順について[ROCm 7.14 Documentation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html)を参照してください。

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### 追加の依存関係

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **注記：** インポート時、Unslothはオプションの`bitsandbytes`アクセラレーションパスを検出しようとすることがあります。一部のROCmバージョンでは、`bitsandbytes library load error: Configured ROCm binary not found`のようなメッセージが表示される場合があります。このプレイブックは`optim="adamw_torch"`を使用した標準的なLoRAファインチューニングを使用するため、`bitsandbytes`オプティマイザや4ビットQLoRAには依存していません。このメッセージは無視しても問題ありません。

<!-- @os:windows -->
> **注記：** Windows ROCmでは、Unslothは起動時にいくつかの警告を表示します — 下記の[Known Warnings](#known-warnings)を参照してください。これらはすべて無視して問題なく、トレーニングは正しく動作します。
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Unslothファインチューニングスクリプトのダウンロード

各ステップを手動で実行する代わりに、このプレイブックでは、クリーンでエンドツーエンドのスクリプトをここで提供します：[test_unsloth.py](assets/test_unsloth.py)。

次のコードを実行してスクリプトを実行します：

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

このプレイブックの残りの部分では、スクリプトの各主要ステップについて概念的に説明していきます。

## 仕組み

test_unsloth.pyスクリプトは、以下のステップを実行します：
* **モデルの読み込み**：FastModelを使用してunsloth/gemma-4-E4B-itを読み込みます。
* **データの準備**：データセット（例：FineTome-100k）を標準化し、Gemma-4のチャットテンプレートを適用します。
* **LoRAの適用**：効率的なトレーニングのため、言語、アテンション、MLPモジュールにアダプタを追加します。
* **トレーニング**：レスポンスのみの損失マスキングを使用してSFTTrainerを使用します。
* **推論**：性能を確認するためのクイック生成テストを実行します。
* **保存**：LoRAアダプタをローカルにエクスポートします。
## Key Configuration

実行をカスタマイズするために、以下の定数を変更できます。

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

モデルの重みを読み込む際の Unsloth ウェルカムメッセージと出力の例:

![alt text](assets/welcome.png)

## Prepare Dataset

以下のサブセットを使用します:
```text
mlabonne/FineTome-100k
```
このデータセットは以下の処理が行われています:
* チャット形式への変換
* Gemma-4 チャットテンプレートによる処理
* 重複した BOS トークンを削除するクリーンアップ

## Train the Model

このスクリプトは、以下のパラメータを使用して簡単なトレーニングデモを実行します。
- 約50ステップ
- 小さいバッチサイズ
- 勾配累積

トレーニング中は、以下のようなログが表示されます。

![alt text](assets/training.png)


## Saving and Deployment

### Local Saving (LoRA)

このスクリプトは、LoRA アダプターを自動的に OUTPUT_DIR に保存します。
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Save merged model (for vLLM) 

<!-- @os:windows -->
> **注:** vLLM は Windows をサポートしていません。Windows でファインチューニング済みモデルをデプロイするには、llama.cpp を使用するか(下記の[Export GGUF](#export-gguf-for-llamacpp)を参照)、マージ済みモデルを vLLM が動作する Linux マシンに転送してください。
<!-- @os:end -->

<!-- @os:linux -->
vLLM でのデプロイには、アダプターを完全なモデルにマージします:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Export GGUF (for llama.cpp)

ローカル推論のために直接 GGUF に変換します:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Known Warnings

以下の警告は、Windows ROCm 上で起動時に Unsloth が出力するものですが、すべて無視して問題ありません。

| 警告 | 理由 | 無視しても安全か? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes には Windows ROCm 向けビルドが存在しない | はい — このプレイブックは bnb ではなく `adamw_torch` を使用します |
| `No ROCm platform found for torch.distributed` | Windows 上の ROCm は分散トレーニングをサポートしていない | はい — 単一 GPU でのトレーニングには影響しません |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth が非 Linux ビルドを警告として表示する | はい — Windows ROCm はシングル GPU の SFT で動作します |
| `triton is not available` | Triton には Windows 向けビルドが存在しない | はい — Unsloth は PyTorch カーネルにフォールバックします |

これらの警告が表示されても、トレーニングは正しく進行します。
<!-- @os:end -->

## Next Steps
- Unsloth 向けの直感的な GUI である[Unsloth Studio](https://unsloth.ai/docs/new/studio)を試す
- 独自のデータセットでトレーニングする
- 異なるハイパーパラメータでファインチューニングを試す
- vLLM または llama.cpp でデプロイする
- より少ないメモリで済む構成として QLoRA を試す

## Resources

Unsloth やファインチューニングについてさらに詳しく学ぶための追加リソースを以下に示します。

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)