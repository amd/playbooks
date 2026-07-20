<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックには、GitHubでは正しくレンダリングできない特殊なタグが使用されています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要

このプレイブックでは、AMDハードウェア上でUnslothを使用してローカルで言語モデルをファインチューニングする方法を紹介します。

`mlabonne/FineTome-100k` データセットのサブセットを使用し、`unsloth/gemma-4-E4B-it` に対してLoRAアダプターを用いた短いSupervised Fine-Tuning(SFT)の例を実施します。目標は、セットアップ、トレーニング、推論、ファインチューニング結果の保存をカバーする、シンプルなエンドツーエンドのワークフローを提供することです。

この例は実用的で修正しやすいように設計されているため、独自のデータセットやモデルの出発点として利用できます。

## 学習内容

- Unsloth環境のセットアップ方法
- UnslothでSFTを使用してLLMをファインチューニングする方法
- ファインチューニング結果をローカルストレージに保存する方法

<!-- @device:halo,stx,krk -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも24GBのGPUメモリと32GBのシステムRAMが必要です。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも24GBのGPUメモリと32GBのシステムRAMが必要です。
<!-- @os:end -->

<!-- @os:linux -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも24GBの**専用**GPUメモリと32GBのシステムRAMが必要です。
<!-- @os:end -->
<!-- @device:end -->

## Unslothを選ぶ理由

Unslothは、標準的なセットアップと比較してメモリ使用量を削減し、トレーニングを高速化することで、ローカルハードウェアでのLLMファインチューニングをより簡単に実行できるようにします。

このプレイブックでは、Unslothを**LoRAベースのSFT**とともに使用します。つまり、ベースモデルはほぼ凍結されたままで、はるかに小規模なアダプター重みのセットがトレーニングされます。これはフルファインチューニングよりも軽量で、反復作業が速いため、ローカル開発に適しています。

Unslothは、QLoRAや強化学習ワークフローを含む他のトレーニング手法もサポートしています。このプレイブックでは、まず最もシンプルな方法、つまりユーザーが実行、理解、拡張できる小規模なLoRAファインチューニングの例に焦点を当てます。

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注**: VS Codeがインストールされていない場合は、Ryzen AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
ターミナルを開き、AMD ROCm™ソフトウェアとPyTorchがあらかじめインストールされたvenvを作成します:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ユーザーにGPUデバイスへのアクセス権を付与します**(これを有効にするには一度ログアウトして再度ログインしてください):

```bash
sudo usermod -aG render,video $LOGNAME
```

ターミナルを開き、venvを作成します:
<!-- @test:id=create-venv timeout=120 -->
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
> **注:** Windowsの場合、Python 3.13が必要です。

<!-- @device:halo_box -->
PowerShellターミナルを開き、仮想環境を作成します:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
PowerShellターミナルを開き、仮想環境を作成します:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### 基本依存関係のインストール
<!-- @require:pytorch,driver -->

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
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **注:** インポート中、Unslothはオプションの `bitsandbytes` アクセラレーションパスをプローブすることがあります。ROCmのバージョンによっては、`bitsandbytes library load error: Configured ROCm binary not found` のようなメッセージが表示されることがあります。このプレイブックでは `optim="adamw_torch"` を使用した標準的なLoRAファインチューニングを行うため、`bitsandbytes` オプティマイザーや4ビットQLoRAには依存していません。このメッセージは無視して問題ありません。

<!-- @os:windows -->
> **注:** Windows ROCmでは、Unslothは起動時にいくつかの警告を表示します — 以下の[既知の警告](#known-warnings)を参照してください。これらはすべて無視して問題なく、トレーニングは正常に動作します。
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

各ステップを手動で実行する代わりに、このプレイブックではクリーンなエンドツーエンドのスクリプトを提供しています: [test_unsloth.py](assets/test_unsloth.py)。

以下のコードを実行してスクリプトを実行します:

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

このプレイブックの残りの部分では、スクリプトの主要な各ステップを概念的に説明していきます。

## 仕組み

test_unsloth.pyスクリプトは以下のステップを実行します:
* **モデルの読み込み**: FastModelを使用してunsloth/gemma-4-E4B-itを読み込みます。
* **データの準備**: データセット(例:FineTome-100k)を標準化し、Gemma-4チャットテンプレートを適用します。
* **LoRAの適用**: 効率的なトレーニングのために、言語、アテンション、MLPモジュールにアダプターを追加します。
* **トレーニング**: レスポンスのみの損失マスキングを使用してSFTTrainerを利用します。
* **推論**: パフォーマンスを検証するためのクイック生成テストを実行します。
* **保存**: LoRAアダプターをローカルにエクスポートします。

## 主要な構成

以下の定数を変更して、実行をカスタマイズできます:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

モデルの重みを読み込む際のUnslothウェルカムメッセージと出力の例:

![alt text](assets/welcome.png)

## データセットの準備

以下のサブセットを使用します:
```text
mlabonne/FineTome-100k
```
データセットは以下の処理が行われます:
* チャット形式に変換
* Gemma-4チャットテンプレートを使用して処理
* 重複するBOSトークンを除去するようクリーンアップ

## モデルのトレーニング

このスクリプトは、以下のパラメータで短いトレーニングデモを実行します:
- 約50ステップ
- 小さいバッチサイズ
- 勾配累積

トレーニング中、以下のようなログが表示されます:

![alt text](assets/training.png)


## 保存とデプロイ

### ローカル保存(LoRA)

スクリプトは自動的にLoRAアダプターをOUTPUT_DIRに保存します。
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

### マージ済みモデルの保存(vLLM用)

<!-- @os:windows -->
> **注:** vLLMはWindowsをサポートしていません。Windowsでファインチューニング済みモデルをデプロイするには、llama.cpp(以下の[GGUFのエクスポート](#export-gguf-for-llamacpp)を参照)を使用するか、マージ済みモデルをvLLMを実行しているLinuxマシンに転送してください。
<!-- @os:end -->

<!-- @os:linux -->
vLLMでのデプロイ用に、アダプターをフルモデルにマージします:
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

### GGUFのエクスポート(llama.cpp用)

ローカル推論用に直接GGUFに変換します:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 既知の警告

これらの警告は、Windows ROCm 上で Unsloth の起動時に表示されますが、すべて無視して問題ありません。

| 警告 | 理由 | 無視して問題ないか |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes には Windows ROCm ビルドが存在しない | はい — 本プレイブックでは bnb ではなく `adamw_torch` を使用しています |
| `No ROCm platform found for torch.distributed` | Windows 版 ROCm には分散トレーニング機能がない | はい — シングル GPU でのトレーニングには影響ありません |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth が Linux 以外のビルドに対して警告を出す | はい — Windows ROCm はシングル GPU の SFT で動作します |
| `triton is not available` | Triton には Windows 版が存在しない | はい — Unsloth は PyTorch カーネルにフォールバックします |

これらの警告が表示されても、トレーニングは正常に進行します。
<!-- @os:end -->

## 次のステップ
- Unsloth 用の直感的な GUI である [Unsloth Studio](https://unsloth.ai/docs/new/studio) を試す
- 自分自身の特定のデータセットでトレーニングする
- 異なるハイパーパラメータでファインチューニングを試す
- vLLM または llama.cpp でデプロイする
- 低メモリ環境向けに QLoRA を試す

## リソース

Unsloth とファインチューニングについてさらに詳しく学ぶための追加リソースを以下に示します。

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)