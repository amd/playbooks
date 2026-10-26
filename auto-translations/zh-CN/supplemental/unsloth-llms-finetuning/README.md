<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

本操作指南展示了如何在 AMD 硬件上使用 Unsloth 在本地对语言模型进行微调。

它使用了一个简短的监督微调（SFT）示例，在 `unsloth/gemma-4-E4B-it` 上使用 LoRA 适配器，并采用了 `mlabonne/FineTome-100k` 数据集的一个子集。目标是为你提供一个简单的端到端工作流程，涵盖设置、训练、推理和保存微调结果。

该示例设计得实用且易于修改，因此你可以将其作为自己数据集和模型的起点。

## 你将学到什么

- 如何搭建 Unsloth 环境
- 如何使用 Unsloth 通过 SFT 微调 LLM
- 如何将微调结果保存到本地存储

<!-- @device:halo,stx,krk -->
> **注意：** 本操作指南中的微调技术至少需要 **64 GB 的系统内存**，其中至少 **24 GB 可供 GPU 使用**（这 24 GB 是这 64 GB 中的一部分，而不是额外增加的）。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意：** 本操作指南中的微调技术至少需要 **24 GB 的 GPU 总内存**和 **32 GB 的系统内存**。
> - 在 Windows 上，GPU 总内存包括显卡的专用显存以及共享 GPU 内存（从系统内存中借用）。
> - 因此，专用显存低于 24 GB 的显卡仍可通过使用共享 GPU 内存补足差额来运行本操作指南。
<!-- @os:end -->

<!-- @os:linux -->
> **注意：** 本操作指南中的微调技术需要一块至少具有 **24 GB 专用 GPU 内存**的显卡以及 **32 GB 的系统内存**。
> - 在 Linux 上，训练完全在显卡的专用显存中运行。
> - 当显存耗尽时，它不会回退到共享 GPU 内存（系统内存）。
> - 专用显存低于 24 GB 的显卡在 Linux 上训练时会出现内存不足的情况，即使系统拥有充足的内存也是如此。
<!-- @os:end -->
<!-- @device:end -->

## 为什么选择 Unsloth？

与标准配置相比，Unsloth 通过降低内存占用和加快训练速度，使 LLM 微调更易于在本地硬件上运行。

在本操作指南中，我们将 Unsloth 与 **基于 LoRA 的 SFT** 结合使用。这意味着基础模型大部分保持冻结状态，而只训练一小部分适配器权重。这非常适合本地开发，因为它比全量微调更轻量，迭代速度也更快。

Unsloth 还支持其他训练方法，包括 QLoRA 和强化学习工作流程。本操作指南首先聚焦于最简单的路径：一个用户可以运行、理解并扩展的小型 LoRA 微调示例。

<!-- @device:halo_box,halo,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新
> **注意**：如果未安装 VS Code，你可以通过 Ryzen AI Developer Center 进行安装。

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
**授予你的用户访问 GPU 设备的权限**（需要注销并重新登录才能生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

打开终端并创建一个 venv：
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
> **注意：** Windows 需要 Python 3.13。

<!-- @device:halo_box -->
打开 PowerShell 终端并创建一个虚拟环境：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
打开 PowerShell 终端并创建一个虚拟环境：
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
<!-- @require:driver -->

> **重要提示：** Unsloth 尚不支持 ROCm 10 附带的 PyTorch 2.13 版本。对于本操作指南，请使用以下命令安装 **带有 PyTorch 2.12 的 ROCm 7.14**。请勿使用 ROCm 10 / PyTorch 2.13 软件包。

在已创建的虚拟环境中**安装支持 AMD ROCm™ 软件的 PyTorch**：

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

有关其他设备，请参阅 [ROCm 7.14 文档](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html)获取完整说明。

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

> **注意：** 在导入期间，Unsloth 可能会探测可选的 `bitsandbytes` 加速路径。在某些 ROCm 版本上，你可能会看到诸如 `bitsandbytes library load error: Configured ROCm binary not found` 之类的消息。本操作指南使用带有 `optim="adamw_torch"` 的标准 LoRA 微调，因此我们不依赖 `bitsandbytes` 优化器或 4 位 QLoRA。此消息可以安全忽略。

<!-- @os:windows -->
> **注意：** 在 Windows ROCm 上，Unsloth 启动时会打印多个警告——请参阅下方的[已知警告](#known-warnings)。这些警告都可以安全忽略；训练仍能正常进行。
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

本操作指南在此处提供了一个简洁的端到端脚本，而不是手动执行每个步骤：[test_unsloth.py](assets/test_unsloth.py)。

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

本操作指南的其余部分将从概念上逐一介绍该脚本的每个主要步骤。

## 工作原理

test_unsloth.py 脚本执行以下步骤：
* **加载模型**：使用 FastModel 加载 unsloth/gemma-4-E4B-it。
* **准备数据**：标准化数据集（例如 FineTome-100k）并应用 Gemma-4 聊天模板。
* **应用 LoRA**：向语言、注意力和 MLP 模块添加适配器以实现高效训练。
* **训练**：使用带有仅响应损失掩码的 SFTTrainer。
* **推理**：运行快速生成测试以验证性能。
* **保存**：将 LoRA 适配器导出到本地。
## 主要配置

您可以修改以下常量来自定义运行方式：

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Unsloth 欢迎信息示例以及加载模型权重时的输出：

![alt text](assets/welcome.png)

## 准备数据集

我们使用以下数据集的一个子集：
```text
mlabonne/FineTome-100k
```
该数据集已：
* 转换为聊天格式
* 使用 Gemma-4 聊天模板进行处理
* 清理以移除重复的 BOS 令牌

## 训练模型

该脚本运行一个简短的训练演示，参数如下：
- 约 50 步
- 小批量大小
- 梯度累积

在训练过程中，您将看到如下日志：

![alt text](assets/training.png)


## 保存与部署

### 本地保存（LoRA）

该脚本会自动将 LoRA 适配器保存到 OUTPUT_DIR 中。
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
> **注意：** vLLM 不支持 Windows。若要在 Windows 上部署您微调的模型，请使用 llama.cpp（参见下方 [导出 GGUF](#export-gguf-for-llamacpp)），或将合并后的模型传输到运行 vLLM 的 Linux 机器上。
<!-- @os:end -->

<!-- @os:linux -->
若要使用 vLLM 进行部署，请将适配器合并为完整模型：
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

以下警告是 Unsloth 在 Windows ROCm 上启动时打印的，均可安全忽略：

| 警告 | 原因 | 是否可安全忽略？ |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes 没有 Windows ROCm 版本构建 | 是 —— 本操作指南使用的是 `adamw_torch`，而非 bnb |
| `No ROCm platform found for torch.distributed` | Windows 上的 ROCm 不支持分布式训练 | 是 —— 单 GPU 训练不受影响 |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth 标记非 Linux 构建 | 是 —— Windows ROCm 支持单 GPU SFT |
| `triton is not available` | Triton 没有 Windows 版本构建 | 是 —— Unsloth 会回退使用 PyTorch 内核 |

尽管出现这些警告，训练仍将正常进行。
<!-- @os:end -->

## 后续步骤
- 尝试 [Unsloth Studio](https://unsloth.ai/docs/new/studio)，这是一个直观的 Unsloth 图形界面
- 在您自己的特定数据集上进行训练
- 尝试使用不同的超参数进行微调
- 使用 vLLM 或 llama.cpp 进行部署
- 尝试使用 QLoRA 以降低内存需求

## 资源

以下是了解更多关于 Unsloth 与微调相关内容的其他资源：

* [Unsloth 文档](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth 微调指南](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)