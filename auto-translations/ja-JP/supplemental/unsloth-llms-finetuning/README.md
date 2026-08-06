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

このプレイブックでは、AMD ハードウェア上で Unsloth を使用してローカルで言語モデルをファインチューニングする方法を説明します。

このプレイブックでは、`mlabonne/FineTome-100k` データセットのサブセットを使用し、`unsloth/gemma-4-E4B-it` に対して LoRA アダプターを用いた短い Supervised Fine-Tuning (SFT) の例を紹介します。目的は、セットアップ、トレーニング、推論、ファインチューニング結果の保存までをカバーする、シンプルなエンドツーエンドのワークフローを示すことです。

この例は実用的で変更しやすいように設計されているため、独自のデータセットやモデルに取り組む際の出発点として活用できます。

## このプレイブックで学べること

- Unsloth 環境のセットアップ方法
- Unsloth を使用して LLM を SFT でファインチューニングする方法
- ファインチューニング結果をローカルストレージに保存する方法

<!-- @device:halo,stx,krk -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも **64 GB のシステム RAM** が必要で、そのうち少なくとも **24 GB を GPU が利用できる状態** である必要があります(この 24 GB はシステム RAM の 64 GB の一部であり、それに加えて必要というわけではありません)。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも **24 GB の GPU メモリ総量** と **32 GB のシステム RAM** が必要です。
> - Windows では、GPU メモリ総量はグラフィックスカード専用の VRAM と(システム RAM から借用される)共有 GPU メモリを合わせたものになります。
> - そのため、専用 VRAM が 24 GB 未満のカードでも、共有 GPU メモリを使って不足分を補うことで、このプレイブックを実行できます。
<!-- @os:end -->

<!-- @os:linux -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも **24 GB の専用 GPU メモリ** を持つグラフィックスカードと **32 GB のシステム RAM** が必要です。
> - Linux では、トレーニングはすべてグラフィックスカードの専用 VRAM 内で実行されます。
> - VRAM が不足しても、共有 GPU メモリ(システム RAM)へのフォールバックは行われません。
> - 専用 VRAM が 24 GB 未満のカードは、システムに十分な RAM があっても、Linux 上でのトレーニング中にメモリ不足になります。
<!-- @os:end -->
<!-- @device:end -->

## なぜ Unsloth なのか

Unsloth は、メモリ使用量を削減し、標準的なセットアップと比較してトレーニングを高速化することで、ローカルハードウェア上での LLM ファインチューニングを容易にします。

このプレイブックでは、Unsloth を **LoRA ベースの SFT** と組み合わせて使用します。つまり、ベースモデルはほぼ凍結されたままで、はるかに小規模なアダプターの重みのセットがトレーニングされます。これはフルファインチューニングよりも軽量で反復しやすいため、ローカル開発に適しています。

Unsloth は、QLoRA や強化学習ワークフローを含む他のトレーニング手法もサポートしています。このプレイブックでは、まず最もシンプルな方法を取り上げます。それは、ユーザーが実行、理解、拡張できる小規模な LoRA ファインチューニングの例です。

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **注**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
ターミナルを開き、AMD ROCm™ ソフトウェアと PyTorch がすでにインストールされた venv を作成します:
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
**ユーザーに GPU デバイスへのアクセス権を付与します**(有効にするにはログアウトして再度ログインしてください):

```bash
sudo usermod -aG render,video $LOGNAME
```

ターミナルを開き、venv を作成します:
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
> **注:** Windows では Python 3.13 が必要です。

<!-- @device:halo_box -->
PowerShell ターミナルを開き、仮想環境を作成します:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
PowerShell ターミナルを開き、仮想環境を作成します:
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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **注:** インポート時、Unsloth はオプションの `bitsandbytes` アクセラレーションパスをプローブすることがあります。一部の ROCm バージョンでは、`bitsandbytes library load error: Configured ROCm binary not found` のようなメッセージが表示される場合があります。このプレイブックでは `optim="adamw_torch"` を使用した標準的な LoRA ファインチューニングを行うため、`bitsandbytes` オプティマイザーや 4-bit QLoRA には依存していません。このメッセージは無視して問題ありません。

<!-- @os:windows -->
> **注:** Windows 上の ROCm では、Unsloth は起動時にいくつかの警告を表示します — 下記の [既知の警告](#known-warnings) を参照してください。これらはすべて無視して問題なく、トレーニングは正常に動作します。
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

各ステップを手動で実行する代わりに、このプレイブックでは、クリーンでエンドツーエンドのスクリプトをここに用意しています: [test_unsloth.py](assets/test_unsloth.py)。

次のコードを実行してスクリプトを実行します:

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

test_unsloth.py スクリプトは以下のステップを実行します:
* **モデルの読み込み**: FastModel を使用して unsloth/gemma-4-E4B-it を読み込みます。
* **データの準備**: データセット(例: FineTome-100k)を標準化し、Gemma-4 チャットテンプレートを適用します。
* **LoRA の適用**: 効率的なトレーニングのために、言語、アテンション、MLP モジュールにアダプターを追加します。
* **トレーニング**: レスポンスのみの損失マスキングを使用して SFTTrainer を利用します。
* **推論**: パフォーマンスを確認するために、簡単な生成テストを実行します。
* **保存**: LoRA アダプターをローカルにエクスポートします。

## 主要な設定

実行をカスタマイズするために、以下の定数を変更できます:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

モデルの重みを読み込む際の Unsloth のウェルカムメッセージと出力の例:

![alt text](assets/welcome.png)

## データセットの準備

以下のサブセットを使用します:
```text
mlabonne/FineTome-100k
```
データセットは以下のように処理されます:
* チャット形式に変換
* Gemma-4 チャットテンプレートを使用して処理
* 重複した BOS トークンを削除するようにクリーニング

## モデルのトレーニング

このスクリプトは、以下のパラメーターで短いトレーニングデモを実行します:
- 約 50 ステップ
- 小さいバッチサイズ
- 勾配累積

トレーニング中は、以下のようなログが表示されます:

![alt text](assets/training.png)


## 保存とデプロイ
### ローカル保存(LoRA)

このスクリプトはLoRAアダプターをOUTPUT_DIRに自動的に保存します。
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
> **注:** vLLMはWindowsをサポートしていません。Windowsでファインチューニング済みモデルをデプロイするには、llama.cpp(下記の[GGUFのエクスポート](#export-gguf-for-llamacpp)を参照)を使用するか、マージ済みモデルをvLLMを実行しているLinuxマシンに転送してください。
<!-- @os:end -->

<!-- @os:linux -->
vLLMでのデプロイでは、アダプターをフルモデルにマージします。
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

ローカル推論のために直接GGUFに変換します。
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 既知の警告

これらの警告は、Windows ROCm上でのUnslothの起動時に表示されますが、すべて無視して問題ありません。

| 警告 | 理由 | 無視しても安全か? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytesにはWindows ROCm用ビルドがない | はい — このプレイブックではbnbではなく`adamw_torch`を使用します |
| `No ROCm platform found for torch.distributed` | Windows上のROCmには分散学習機能がない | はい — シングルGPUトレーニングには影響しません |
| `Unsloth: WARNING! You are using an unsupported platform` | UnslothがLinux以外のビルドにフラグを立てる | はい — Windows ROCmはシングルGPUのSFTで動作します |
| `triton is not available` | TritonにはWindows用ビルドがない | はい — UnslothはPyTorchカーネルにフォールバックします |

これらの警告が表示されても、トレーニングは正常に進行します。
<!-- @os:end -->

## 次のステップ
- Unslothの直感的なGUIである[Unsloth Studio](https://unsloth.ai/docs/new/studio)を試す
- 独自の特定のデータセットでトレーニングする
- さまざまなハイパーパラメータでファインチューニングを試す
- vLLMまたはllama.cppでデプロイする
- 低メモリ環境向けにQLoRAを試す

## リソース

Unslothとファインチューニングについてさらに詳しく学ぶための追加リソースを以下に示します。

* [Unslothドキュメント](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unslothファインチューニングガイド](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)