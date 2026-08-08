<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

## 概要

効率的なファインチューニングは、大規模言語モデル（LLM）を下流タスクに適応させるために不可欠です。LLaMA Factoryは、大規模言語モデルやマルチモーダルモデルのトレーニングとファインチューニングを効率化する、オープンソースで使いやすいプラットフォームです。ユーザーは、最小限のコーディングでローカルに数百の事前学習済みモデルをカスタマイズできます。

このプレイブックでは、ローカルのAMDハードウェア上でLLaMA Factoryを使用してLLMをファインチューニングする方法を説明します。

<!-- @device:stx,krk -->
> **注：** このプレイブックのファインチューニング手法には、少なくとも**32 GBのシステムRAM**が必要で、そのうち少なくとも**16 GBがGPUで利用可能**である必要があります（この16 GBは32 GBの一部であり、追加ではありません）。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注：** このプレイブックのファインチューニング手法には、少なくとも**16 GBの合計GPUメモリ**と**32 GBのシステムRAM**が必要です。
> - Windowsでは、合計GPUメモリはグラフィックカードの専用VRAMとシステムRAMから借用される共有GPUメモリを組み合わせたものです。
> - そのため、専用VRAMが16 GB未満のカードでも、共有GPUメモリで差分を補うことでこのプレイブックを実行できます。
<!-- @os:end -->

<!-- @os:linux -->
> **注：** このプレイブックのファインチューニング手法には、少なくとも**16 GBの専用GPUメモリ**を持つグラフィックカードと**32 GBのシステムRAM**が必要です。
> - Linuxでは、トレーニングはグラフィックカードの専用VRAM内で完全に実行されます。
> - VRAMが不足しても、共有GPUメモリ（システムRAM）にフォールバックすることはありません。
> - 専用VRAMが16 GB未満のカードは、システムに十分なRAMがあっても、Linux上でのトレーニング中にメモリ不足になります。
<!-- @os:end -->
<!-- @device:end -->

## 学べること

- AMD ROCm™ ソフトウェアを使用したLLaMA Factoryのセットアップ方法
- LLMファインチューニングパラメータの構成方法（Qwen/Qwen3-4B-Instruct-2507を例として使用）
- LLaMA Factoryファインチューニングの実行方法
- ファインチューニング済みモデルでの推論の実行方法
- ファインチューニング済みモデルのエクスポート方法

## 所要時間

- 所要時間：このプレイブックの実行には約60分かかります（モデル/データセットのサイズやネットワーク速度によって異なります）。
- 詳細については、[LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory)をご覧ください。

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ユーザーにGPUデバイスへのアクセス権を付与する**（これを有効にするにはログアウトして再度ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### 基本的な依存関係のインストール

<!-- @require:pytorch,driver -->
 
### 追加の依存関係のインストール

> **注**：Pythonのバージョンが3.11、3.12、または3.13であることを確認してください

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### LLaMA Factoryのインストール

LLaMA FactoryはPyTorchに依存しています。上記の要件に従って、すでにインストール済みのはずです。

[LLaMA Factory公式GitHubリポジトリ](https://github.com/hiyouga/LlamaFactory)からソースコードをダウンロードし、その依存関係をインストールします。

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

`llamafactory-cli`が実行可能かどうかを確認します。

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

出力例：

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

LLaMA Factoryのインストールに成功したので、次にファインチューニングを実行してみましょう。

## LLaMA Factory CLIを使用したファインチューニング

このセクションでは、ファインチューニング用データセットの準備方法、LoRA/QLoRAパラメータの構成方法、およびLoRAファインチューニングの実行方法について説明します。

### データセットの準備

LLaMA Factoryは、Alpaca形式とShareGPT形式のファインチューニングデータセットをサポートしています。利用可能なすべてのデータセットは[dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json)で定義されています。カスタムデータセットを使用する場合は、`dataset_info.json`にデータセットの説明を追加し、トレーニング前にデータセット名を指定してください。詳細は[こちら](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html)のドキュメントをご覧ください。

このプレイブックでは、identityおよびalpaca_en_demoデータセットを例として使用し、次のステップでデータセット情報を構成します。
### ファインチューニングパラメータの設定

LLaMA Factoryは複数のファインチューニング手法をサポートしています。

| ファインチューニング手法 | LLaMA Factoryの例 |
|-----------|------|
| フルパラメータ    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRAファインチューニング  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRAファインチューニング | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

これらのサンプル設定ファイルには、モデルパラメータ、ファインチューニング手法のパラメータ、データセットパラメータ、評価パラメータなどが指定されています。ご自身のニーズに応じて設定することができます。このプレイブックでは、[qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml)を使用します。

**主要なパラメータの説明:**
- `model_name_or_path` - Hugging Faceのモデル名、またはローカルのモデルファイルパス。
- `stage` - トレーニングステージ。オプション: rm（報酬モデリング）、pt（事前学習）、sft（教師ありファインチューニング）、PPO、DPO、KTO、ORPO。
- `do_train` - トレーニングの場合はtrue、評価の場合はfalse
- `finetuning_type` - ファインチューニング手法。オプション: freeze、lora、full
- `lora_rank` - LoRAで使用される低ランク行列の次元数。一般的な値: 4、6、8、16（値が小さいほどパラメータ数が少なくファインチューニングが高速になり、値が大きいほどタスクへの適応性は向上しますがリソース使用量が増加します）。
- `lora_target` - LoRA手法の対象モジュール。デフォルト: all。
- `dataset` - 使用するデータセット。複数のデータセットを指定する場合は「,」で区切ります
- `output_dir` - ファインチューニングの出力パス
- `logging_steps` - ロギング間隔（ステップ数）
- `save_steps` - モデルチェックポイントの保存間隔。
- `overwrite_output_dir` - 出力ディレクトリの上書きを許可するかどうか。
- `per_device_train_batch_size` - デバイスごとのトレーニングバッチサイズ。
- `gradient_accumulation_steps` - 勾配累積のステップ数。
- `learning_rate` - 学習率
- `num_train_epochs` - トレーニングエポック数
- `lr_scheduler_type` - 学習率スケジュール。オプション: linear、cosine、polynomial、constantなど。
- `warmup_ratio` - 学習率ウォームアップ比率

<!-- @os:linux -->
AMD Ryzen™およびAMD Radeon™ GPUでファインチューニングを実行するために、`lora_rank`のデフォルト値を変更します。
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
AMD Ryzen™およびAMD Radeon™ GPUとの互換性を高めるため、デフォルトのLoRAファインチューニング設定を以下のように更新します：
- ファインチューニング時のメモリ使用量を削減するため、`lora_rank`を`8`から`6`に設定します。
- AMD GPUとの互換性を高めメモリ使用量を抑えるため、`bf16`の代わりに`fp16`を使用します。
- Windowsではマルチプロセスによるデータ読み込みが原因の`"Can't pickle local object<>"`エラーを回避するため、`dataloader_num_workers`を`0`に設定します。

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### LLaMA Factoryファインチューニングの実行

**llamafactory-cli**は、複雑なコードを書くことなくLLMのエンドツーエンドのワークフロー（データ準備 → ファインチューニング → 評価 → デプロイ）を簡素化するために開発された、LLaMA Factory公式のコマンドラインインターフェース（CLI）ツールです。

トレーニング／ファインチューニング用に、**llamafactory-cli train**はLLaMA Factory CLIの中核となるサブコマンドです。ファインチューニングのワークフロー（データの前処理、ハイパーパラメータの調整、ハードウェアの最適化）を単一のCLIコマンドに抽象化し、複数のファインチューニング手法（LoRA／QLoRA／フルファインチューニング）をサポートしており、低リソースのGPU（例：16GB VRAMでのQLoRA）向けに最適化されています。

以下のコマンドを使用して、Qwen3 LoRAファインチューニング用に変更した設定ファイルに基づいてLLaMA Factoryのファインチューニングを実行できます。

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

LLMのファインチューニングを実行すると、生成されたすべての出力は「output_dir」に保存されます。これには、モデルチェックポイントファイル、設定ファイル、トレーニングメトリクスが含まれます。

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### ファインチューニング済みモデルのテスト

**llamafactory-cli chat**は、LLM（ベースモデルとLoRAファインチューニング済みモデルの両方）とのインタラクティブなチャット／推論のために設計されています。LLaMA Factoryは、[examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference)でファインチューニング済みモデルの推論を実行するためのサンプル設定を提供しています。このサンプル設定を変更して、推論バックエンドなどの設定を変更することもできます。

以下のコマンドを使用して、Qwen3ファインチューニング済みモデルをテストします：

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
ファインチューニング済みモデルを使用したチャットの例を以下に示します：

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### ファインチューニング済みモデルのエクスポート

本番環境での使用ケースでは、事前学習済みモデルとLoRAアダプタをマージし、単一のモデルとしてエクスポートする必要があります。このマージされたモデルは、通常のHugging Faceモデルファイルとして使用できます。LLaMA Factoryは、[examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora)にサンプル設定を提供しています。

以下のコマンドを使用して、Qwen3ファインチューニング済みモデルをエクスポートします：

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
ファインチューニング済みモデルをエクスポートした結果を以下に示します。

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 
## LLaMA Factory GUI の使用

`LLaMA-Factory` は、ブラウザ上のウェブ UI を通じて LLM のゼロコードファインチューニングもサポートしています。

以下のコマンドを使用して開きます:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` は、トレーニング、評価、予測、チャット、モデルのエクスポートなど、機械学習ワークフローを管理するための合理化されたインターフェースを提供します。各タブについて簡単に紹介します:

* **Train**: このタブでは、モデルとデータセットを選択し、トレーニングパラメータを設定して、トレーニングプロセスを開始できます。トレーニング設定を最適化するには、必須パラメータとオプションパラメータを理解することが重要です。
* **Evaluate & Predict**: トレーニング後、このタブを使用してモデルのパフォーマンスを評価し、予測を行うことができます。新しいデータに対するモデルの精度と有効性についての洞察が得られます。
* **Chat**: トレーニングが完了したら、Chat タブでモデルを読み込み、対話して作業の結果を確認します。この機能により、トレーニング済みモデルとのリアルタイムなコミュニケーションが可能になります。
* **Export**: このタブでは、デプロイやさらなる利用のためにトレーニング済みモデルをエクスポートできます。さまざまなアプリケーションに適した形式でモデルを保存できます。

詳細なガイダンスについては、[LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) および [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) の公式ドキュメントを参照することをお勧めします。さらに、[Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) では、インターフェースとその機能について貴重な洞察が得られます。

## 次のステップ
- `gpt-oss` などの最先端のさまざまなモデルを試してみてください。
- ファインチューニングされたモデルでさまざまなバックエンドを試してみてください

詳細なドキュメントについては、以下をご覧ください: https://llamafactory.readthedocs.io/en/latest/