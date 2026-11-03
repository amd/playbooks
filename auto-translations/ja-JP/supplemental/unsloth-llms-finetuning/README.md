<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

このプレイブックでは、AMD ハードウェア上でローカルに Unsloth を使用して言語モデルをファインチューニングする方法を紹介します。

`mlabonne/FineTome-100k` データセットのサブセットを使用し、`unsloth/gemma-4-E4B-it` に対して LoRA アダプターを用いた短い教師ありファインチューニング (SFT) の例を扱います。目的は、セットアップ、トレーニング、推論、ファインチューニング結果の保存をカバーする、シンプルなエンドツーエンドのワークフローを提供することです。

この例は実用的で修正しやすいように設計されているため、独自のデータセットやモデルを扱う際の出発点として利用できます。

## このプレイブックで学べること

- Unsloth 環境をセットアップする方法
- Unsloth を使用して SFT により LLM をファインチューニングする方法
- ファインチューニングした結果をローカルストレージに保存する方法

<!-- @device:halo,stx,krk -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも **64 GB のシステム RAM** が必要であり、そのうち少なくとも **24 GB は GPU が利用可能** である必要があります(この 24 GB は 64 GB の一部であり、追加ではありません)。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも **24 GB の合計 GPU メモリ** と **32 GB のシステム RAM** が必要です。
> - Windows では、合計 GPU メモリは、グラフィックスカードの専用 VRAM とシステム RAM から借用される共有 GPU メモリを合わせたものになります。
> - そのため、専用 VRAM が 24 GB 未満のカードでも、共有 GPU メモリで不足分を補うことでこのプレイブックを実行できます。
<!-- @os:end -->

<!-- @os:linux -->
> **注:** このプレイブックのファインチューニング手法には、少なくとも **24 GB の専用 GPU メモリ** を搭載したグラフィックスカードと **32 GB のシステム RAM** が必要です。
> - Linux では、トレーニングはすべてグラフィックスカードの専用 VRAM 内で実行されます。
> - VRAM が不足した場合でも、共有 GPU メモリ (システム RAM) にフォールバックすることはありません。
> - 専用 VRAM が 24 GB 未満のカードは、システムに十分な RAM があっても、Linux でのトレーニング中にメモリ不足になります。
<!-- @os:end -->
<!-- @device:end -->

## なぜ Unsloth なのか?

Unsloth は、標準的なセットアップと比較してメモリ使用量を削減し、トレーニングを高速化することで、ローカルハードウェア上での LLM ファインチューニングを容易にします。

このプレイブックでは、Unsloth を **LoRA ベースの SFT** と組み合わせて使用します。つまり、ベースモデルはほぼ固定されたまま、はるかに小さなアダプターの重みのセットがトレーニングされます。これはフルファインチューニングよりも軽量で反復しやすいため、ローカル開発に適しています。

Unsloth は、QLoRA や強化学習ワークフローを含む他のトレーニング手法もサポートしています。このプレイブックでは、まず最もシンプルな道筋、つまりユーザーが実行、理解、拡張できる小さな LoRA ファインチューニングの例に焦点を当てます。

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

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
**GPU デバイスへのアクセスをユーザーに付与します**(これを有効にするにはログアウトして再度ログインしてください):

```bash
sudo usermod -aG render,video $LOGNAME
```

ターミナルを開き、venv を作成します:
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
<!-- @require:driver -->

> **重要:** Unsloth は、ROCm 10 に同梱されている PyTorch 2.13 ビルドをまだサポートしていません。このプレイブックでは、以下のコマンドを使用して **PyTorch 2.12 を含む ROCm 7.14** をインストールしてください。ROCm 10 / PyTorch 2.13 パッケージは使用しないでください。

作成した仮想環境に **AMD ROCm™ ソフトウェアサポート付きの PyTorch をインストール** します:

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

その他のデバイスについては、[ROCm 7.14 ドキュメント](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html)を参照して完全な手順を確認してください。

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

> **注:** インポート中に、Unsloth はオプションの `bitsandbytes` アクセラレーションパスを探索することがあります。ROCm のバージョンによっては、`bitsandbytes library load error: Configured ROCm binary not found` のようなメッセージが表示される場合があります。このプレイブックでは `optim="adamw_torch"` を使用した標準の LoRA ファインチューニングを使用しているため、`bitsandbytes` オプティマイザーや 4-bit QLoRA には依存していません。このメッセージは無視して問題ありません。

<!-- @os:windows -->
> **注:** Windows ROCm では、Unsloth は起動時にいくつかの警告を表示します — 以下の [既知の警告](#known-warnings) を参照してください。これらはすべて無視して問題なく、トレーニングは正常に動作します。
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

各ステップを手動で実行する代わりに、このプレイブックはクリーンでエンドツーエンドのスクリプトをここに提供しています: [test_unsloth.py](assets/test_unsloth.py)。

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

このプレイブックの残りの部分では、スクリプトの各主要ステップについて概念的に説明していきます。

## 仕組み

test_unsloth.py スクリプトは以下のステップを実行します:
* **モデルの読み込み**: FastModel を使用して unsloth/gemma-4-E4B-it を読み込みます。
* **データの準備**: データセット(例: FineTome-100k)を標準化し、Gemma-4 チャットテンプレートを適用します。
* **LoRA の適用**: 効率的なトレーニングのために、言語、注意機構、MLP モジュールにアダプターを追加します。
* **トレーニング**: 応答のみの損失マスキングを備えた SFTTrainer を使用します。
* **推論**: パフォーマンスを検証するためのクイック生成テストを実行します。
* **保存**: LoRA アダプターをローカルにエクスポートします。
## 主要な設定

実行をカスタマイズするために、以下の定数を変更できます:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Unslothのウェルカムメッセージとモデルの重みを読み込む際の出力例:

![alt text](assets/welcome.png)

## データセットの準備

以下のサブセットを使用します:
```text
mlabonne/FineTome-100k
```
このデータセットは:
* チャット形式に変換されています
* Gemma-4チャットテンプレートを使用して処理されています
* 重複したBOSトークンを削除するようにクリーニングされています

## モデルのトレーニング

このスクリプトは、以下のパラメータを使用して短いトレーニングデモを実行します:
- 約50ステップ
- 小さいバッチサイズ
- 勾配累積

トレーニング中、以下のようなログが表示されます:

![alt text](assets/training.png)


## 保存とデプロイ

### ローカル保存(LoRA)

このスクリプトは、LoRAアダプタを自動的にOUTPUT_DIRに保存します。
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
> **注:** vLLMはWindowsをサポートしていません。ファインチューニングしたモデルをWindowsにデプロイするには、llama.cpp(下記の[GGUFのエクスポート](#export-gguf-for-llamacpp)を参照)を使用するか、マージ済みモデルをvLLMを実行しているLinuxマシンに転送してください。
<!-- @os:end -->

<!-- @os:linux -->
vLLMでのデプロイのために、アダプタを完全なモデルにマージします:
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

ローカル推論のために直接GGUFに変換します:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 既知の警告

以下の警告は、Windows ROCm上でのUnslothの起動時に表示されますが、すべて無視して問題ありません:

| 警告 | 理由 | 無視しても安全か? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytesにはWindows ROCmビルドがありません | はい — このプレイブックはbnbではなく`adamw_torch`を使用します |
| `No ROCm platform found for torch.distributed` | Windows上のROCmには分散トレーニングがありません | はい — シングルGPUトレーニングには影響しません |
| `Unsloth: WARNING! You are using an unsupported platform` | Unslothは非Linuxビルドにフラグを立てます | はい — Windows ROCmはシングルGPUのSFTで動作します |
| `triton is not available` | TritonにはWindowsビルドがありません | はい — UnslothはPyTorchカーネルにフォールバックします |

これらの警告が表示されても、トレーニングは正常に進行します。
<!-- @os:end -->

## 次のステップ
- Unslothの直感的なGUIである[Unsloth Studio](https://unsloth.ai/docs/new/studio)を試してみてください
- 独自の特定のデータセットでトレーニングしてみてください
- 異なるハイパーパラメータでファインチューニングを試してみてください
- vLLMまたはllama.cppでデプロイしてください
- より少ないメモリでのセットアップのためにQLoRAを試してみてください

## リソース

以下は、Unslothとファインチューニングについてさらに学ぶための追加リソースです:

* [Unsloth ドキュメント](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth ファインチューニングガイド](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)