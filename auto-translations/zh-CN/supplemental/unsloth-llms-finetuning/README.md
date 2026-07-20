<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 本操作手册使用了 GitHub 无法渲染的特殊标签。请访问 [amd.com/playbooks](https://amd.com/playbooks) 以正确预览此内容。
<!-- @github-only:end -->

## 概述

本操作手册展示了如何在 AMD 硬件上使用 Unsloth 在本地微调语言模型。

它使用了一个简短的监督微调（SFT）示例，在 `unsloth/gemma-4-E4B-it` 上使用 LoRA 适配器，并使用 `mlabonne/FineTome-100k` 数据集的一个子集。目标是为您提供一个简单的端到端工作流程，涵盖设置、训练、推理和保存微调结果。

该示例设计得实用且易于修改，因此您可以将其作为自己数据集和模型的起点。

## 您将学到什么

- 如何设置 Unsloth 环境
- 如何使用 Unsloth 通过 SFT 微调 LLM
- 如何将微调结果保存到本地存储

<!-- @device:halo,stx,krk -->
> **注意：** 本操作手册中的微调技术至少需要 24 GB 的 GPU 内存和 32 GB 的系统 RAM。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意：** 本操作手册中的微调技术至少需要 24 GB 的 GPU 内存和 32 GB 的系统 RAM。
<!-- @os:end -->

<!-- @os:linux -->
> **注意：** 本操作手册中的微调技术至少需要 24 GB 的**专用** GPU 内存和 32 GB 的系统 RAM。
<!-- @os:end -->
<!-- @device:end -->

## 为什么选择 Unsloth？

与标准设置相比，Unsloth 通过减少内存使用和加快训练速度，使 LLM 微调更容易在本地硬件上运行。

在本操作手册中，我们将 Unsloth 与**基于 LoRA 的 SFT** 结合使用。这意味着基础模型大部分保持冻结，同时训练一组小得多的适配器权重。这非常适合本地开发，因为它比完全微调更轻量，迭代速度也更快。

Unsloth 还支持其他训练方法，包括 QLoRA 和强化学习工作流程。本操作手册首先关注最简单的路径：一个小型 LoRA 微调示例，用户可以运行、理解并加以扩展。

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新
> **注意**：如果未安装 VS Code，您可以通过 Ryzen AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

### 创建虚拟环境

<!-- @os:linux -->
<!-- @device:halo_box -->
打开终端并创建一个已预装 AMD ROCm™ 软件和 PyTorch 的 venv：
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
**为您的用户授予对 GPU 设备的访问权限**（需要注销并重新登录才能生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

打开终端并创建一个 venv：
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
> **注意：** Windows 需要 Python 3.13。

<!-- @device:halo_box -->
打开 PowerShell 终端并创建虚拟环境：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
打开 PowerShell 终端并创建虚拟环境：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### 安装基本依赖项
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

### 附加依赖项

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

> **注意：** 在导入过程中，Unsloth 可能会探测可选的 `bitsandbytes` 加速路径。在某些 ROCm 版本上，您可能会看到类似 `bitsandbytes library load error: Configured ROCm binary not found` 的消息。本操作手册使用标准的 LoRA 微调，配置为 `optim="adamw_torch"`，因此我们不依赖 `bitsandbytes` 优化器或 4 位 QLoRA。此消息可以安全忽略。

<!-- @os:windows -->
> **注意：** 在 Windows ROCm 上，Unsloth 启动时会打印若干警告——请参见下方[已知警告](#known-warnings)。这些都可以安全忽略；训练可以正常工作。
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

## 下载 Unsloth 微调脚本

本操作手册提供了一个简洁的端到端脚本，而不是手动执行每个步骤：[test_unsloth.py](assets/test_unsloth.py)。

运行以下代码以执行该脚本：

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

本操作手册的其余部分将从概念上介绍脚本的每个主要步骤。

## 工作原理

test_unsloth.py 脚本执行以下步骤：
* **加载模型**：使用 FastModel 加载 unsloth/gemma-4-E4B-it。
* **准备数据**：标准化数据集（例如 FineTome-100k）并应用 Gemma-4 聊天模板。
* **应用 LoRA**：为语言、注意力和 MLP 模块添加适配器，以实现高效训练。
* **训练**：使用带有仅响应损失掩码的 SFTTrainer。
* **推理**：运行一次快速生成测试以验证性能。
* **保存**：将 LoRA 适配器导出到本地。

## 关键配置

您可以修改以下常量来自定义运行：

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

加载模型权重时 Unsloth 欢迎消息和输出示例：

![alt text](assets/welcome.png)

## 准备数据集

我们使用以下数据集的一个子集：
```text
mlabonne/FineTome-100k
```
该数据集：
* 已转换为聊天格式
* 使用 Gemma-4 聊天模板处理
* 已清理以移除重复的 BOS 令牌

## 训练模型

该脚本运行一个简短的训练演示，参数如下：
- 约 50 步
- 较小的批量大小
- 梯度累积

在训练过程中，您将看到如下日志：

![alt text](assets/training.png)


## 保存和部署

### 本地保存（LoRA）

该脚本会自动将 LoRA 适配器保存到 OUTPUT_DIR。
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

### 保存合并模型（用于 vLLM）

<!-- @os:windows -->
> **注意：** vLLM 不支持 Windows。要在 Windows 上部署您的微调模型，请使用 llama.cpp（参见下方[导出 GGUF](#export-gguf-for-llamacpp)）或将合并后的模型转移到运行 vLLM 的 Linux 机器上。
<!-- @os:end -->

<!-- @os:linux -->
要使用 vLLM 部署，请将适配器合并为完整模型：
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

### 导出 GGUF（用于 llama.cpp）

直接转换为 GGUF 以进行本地推理：
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 已知警告

以下警告是 Unsloth 在 Windows ROCm 上启动时打印的,均可安全忽略:

| 警告 | 原因 | 可以忽略吗? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes 没有 Windows ROCm 版本 | 是——本教程使用的是 `adamw_torch`,而非 bnb |
| `No ROCm platform found for torch.distributed` | Windows 上的 ROCm 不支持分布式训练 | 是——单 GPU 训练不受影响 |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth 会标记非 Linux 构建版本 | 是——Windows ROCm 可用于单 GPU SFT |
| `triton is not available` | Triton 没有 Windows 版本 | 是——Unsloth 会回退使用 PyTorch 内核 |

尽管出现这些警告,训练仍会正常进行。
<!-- @os:end -->

## 后续步骤
- 试试 [Unsloth Studio](https://unsloth.ai/docs/new/studio),这是一个直观易用的 Unsloth 图形界面
- 在你自己的特定数据集上进行训练
- 尝试使用不同的超参数进行微调
- 使用 vLLM 或 llama.cpp 进行部署
- 尝试使用 QLoRA 以降低显存占用

## 资源

以下是一些了解 Unsloth 与微调的更多资源:

* [Unsloth 文档](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth 微调指南](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)