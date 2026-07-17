<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub でレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要

このプレイブックでは、AMD ハードウェア上で Unsloth を使用して言語モデルをローカルでファインチューニングする方法を説明します。

`unsloth/gemma-4-E4B-it` に対して LoRA アダプターを用いた短い教師あり微調整（SFT）の例を使用し、`mlabonne/FineTome-100k` データセットのサブセットを利用します。目的は、セットアップ、トレーニング、推論、ファインチューニング結果の保存をカバーするシンプルなエンドツーエンドのワークフローを提供することです。

この例は実用的で修正しやすいように設計されており、独自のデータセットやモデルの出発点として活用できます。

## 学習内容

- Unsloth 環境のセットアップ方法
- Unsloth を使用した SFT による LLM のファインチューニング方法
- ファインチューニング結果をローカルストレージに保存する方法

<!-- @device:halo,stx,krk -->
> **注意:** このプレイブックのファインチューニング手法には、少なくとも 24 GB の GPU メモリと 32 GB のシステム RAM が必要です。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意:** このプレイブックのファインチューニング手法には、少なくとも 24 GB の GPU メモリと 32 GB のシステム RAM が必要です。
<!-- @os:end -->

<!-- @os:linux -->
> **注意:** このプレイブックのファインチューニング手法には、少なくとも 24 GB の**専用** GPU メモリと 32 GB のシステム RAM が必要です。
<!-- @os:end -->
<!-- @device:end -->

## Unsloth を使う理由

Unsloth は、標準的なセットアップと比較してメモリ使用量を削減しトレーニングを高速化することで、ローカルハードウェア上での LLM ファインチューニングを容易にします。

このプレイブックでは、Unsloth を **LoRA ベースの SFT** と組み合わせて使用します。つまり、ベースモデルはほぼ凍結されたまま、はるかに小さなアダプターウェイトのセットがトレーニングされます。これはフルファインチューニングよりも軽量で反復が速いため、ローカル開発に適しています。

Unsloth は QLoRA や強化学習ワークフローを含む他のトレーニングアプローチもサポートしています。このプレイブックでは、まず最もシンプルな方法に焦点を当てます：ユーザーが実行・理解・拡張できる小さな LoRA ファインチューニングの例です。

## メモリ設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注意**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
ターミナルを開き、AMD ROCm™ ソフトウェアと PyTorch がすでにインストールされた venv を作成します：
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
**GPU デバイスへのユーザーアクセスを許可します**（有効にするにはログアウトして再度ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

ターミナルを開き、venv を作成します：
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
> **注意:** Windows には Python 3.13 が必要です。

<!-- @device:halo_box -->
PowerShell ターミナルを開き、仮想環境を作成します：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
PowerShell ターミナルを開き、仮想環境を作成します：
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

> **注意:** インポート時に、Unsloth はオプションの `bitsandbytes` アクセラレーションパスを検索する場合があります。一部の ROCm バージョンでは、`bitsandbytes library load error: Configured ROCm binary not found` というメッセージが表示されることがあります。このプレイブックでは `optim="adamw_torch"` を使用した標準的な LoRA ファインチューニングを使用しているため、`bitsandbytes` オプティマイザーや 4-bit QLoRA には依存していません。このメッセージは無視して問題ありません。

<!-- @os:windows -->
> **注意:** Windows ROCm では、Unsloth は起動時にいくつかの警告を表示します — 以下の[既知の警告](#known-warnings)を参照してください。これらはすべて無視しても問題なく、トレーニングは正常に動作します。
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

## Unsloth ファインチューニングスクリプトのダウンロード

各ステップを手動で実行する代わりに、このプレイブックではクリーンなエンドツーエンドのスクリプトを提供しています：[test_unsloth.py](assets/test_unsloth.py)。

スクリプトを実行するには、以下のコードを実行してください：

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

プレイブックの残りの部分では、スクリプトの各主要ステップを概念的に説明します。

## 仕組み

test_unsloth.py スクリプトは以下のステップを実行します：
* **モデルの読み込み**: FastModel を使用して unsloth/gemma-4-E4B-it を読み込みます。
* **データの準備**: データセット（例：FineTome-100k）を標準化し、Gemma-4 チャットテンプレートを適用します。
* **LoRA の適用**: 効率的なトレーニングのために、言語、アテンション、MLP モジュールにアダプターを追加します。
* **トレーニング**: レスポンスのみの損失マスキングを使用した SFTTrainer を使用します。
* **推論**: パフォーマンスを確認するためにクイック生成テストを実行します。
* **保存**: LoRA アダプターをローカルにエクスポートします。

## 主要な設定

以下の定数を変更して実行をカスタマイズできます：

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

モデルウェイトを読み込む際の Unsloth ウェルカムメッセージと出力の例：

![alt text](assets/welcome.png)

## データセットの準備

以下のサブセットを使用します：
```text
mlabonne/FineTome-100k
```
データセットは：
* チャット形式に変換されます
* Gemma-4 チャットテンプレートを使用して処理されます
* 重複する BOS トークンを除去するためにクリーニングされます

## モデルのトレーニング

スクリプトは以下のパラメーターで短いトレーニングデモを実行します：
- 約 50 ステップ
- 小さなバッチサイズ
- 勾配累積

トレーニング中は、次のようなログが表示されます：

![alt text](assets/training.png)


## 保存とデプロイ

### ローカル保存（LoRA）

スクリプトは LoRA アダプターを OUTPUT_DIR に自動的に保存します。
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

### マージされたモデルの保存（vLLM 用）

<!-- @os:windows -->
> **注意:** vLLM は Windows をサポートしていません。Windows でファインチューニングされたモデルをデプロイするには、llama.cpp を使用するか（以下の [GGUF のエクスポート](#export-gguf-for-llamacpp) を参照）、マージされたモデルを vLLM を実行している Linux マシンに転送してください。
<!-- @os:end -->

<!-- @os:linux -->
vLLM でデプロイするには、アダプターをフルモデルにマージします：
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

### GGUF のエクスポート（llama.cpp 用）

ローカル推論のために直接 GGUF に変換します：
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 既知の警告

これらの警告は、Windows ROCm 上で Unsloth が起動時に表示するものであり、すべて無視しても問題ありません：

| 警告 | 理由 | 無視しても安全？ |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes には Windows ROCm ビルドがありません | はい — このプレイブックは `adamw_torch` を使用しており、bnb は使用しません |
| `No ROCm platform found for torch.distributed` | Windows 上の ROCm は分散トレーニングをサポートしていません | はい — シングル GPU トレーニングには影響しません |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth が非 Linux ビルドにフラグを立てます | はい — Windows ROCm はシングル GPU SFT で動作します |
| `triton is not available` | Triton には Windows ビルドがありません | はい — Unsloth は PyTorch カーネルにフォールバックします |

これらの警告があってもトレーニングは正常に進行します。
<!-- @os:end -->

## 次のステップ
- Unsloth の直感的な GUI である [Unsloth Studio](https://unsloth.ai/docs/new/studio) を試してみましょう
- 独自の特定のデータセットでトレーニングする
- 異なるハイパーパラメーターでファインチューニングを試す
- vLLM または llama.cpp でデプロイする
- より少ないメモリのセットアップのために QLoRA を試す

## リソース

Unsloth とファインチューニングについて詳しく学ぶための追加リソースを以下に示します：

* [Unsloth ドキュメント](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth ファインチューニングガイド](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)