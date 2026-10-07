<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述


想要在自己的硬件上运行强大的 AI 语言模型吗？本指南将向您展示如何实现。
本教程使用由 AMD ROCm™ 软件驱动的 PyTorch，来运行可以总结文档、回答问题、生成文本等功能的模型，全部在本地运行。

## 您将学到什么

- 使用 PyTorch 和 ROCm 在本地运行 gpt-oss-20b 和 qwen3.5-4B 等 LLM
- 创建一个使用 LLM 的文档摘要工具

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
在 Linux 上，在您选择的目录中打开终端，并按照以下命令创建一个已预装 ROCm+Pytorch 的 venv。
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予您的用户访问 GPU 设备的权限**（需要注销并重新登录才能生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

在 Linux 上，在您选择的目录中打开终端，并按照以下命令创建一个 venv。
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
在 Windows 上，在您选择的目录中打开终端，并按照以下命令创建一个已预装 ROCm+Pytorch 的 venv。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
在 Windows 上，在您选择的目录中打开终端，并按照以下命令创建一个 venv。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **提示**：Windows 用户在运行某些 Powershell 命令之前，可能需要修改其 PowerShell 执行策略（例如，将其设置为 RemoteSigned 或 Unrestricted）。

<!-- @os:end -->

### 安装基本依赖项
<!-- @require:driver,pytorch -->

### 安装其他依赖项

<!-- @var:id=ms_model device=halo,halo_box value="openai-mirror/gpt-oss-20b" -->
<!-- @var:id=ms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf modelscope
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf modelscope
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf modelscope
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf modelscope
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## 使用示例脚本快速入门

本行动手册包含可直接使用的脚本。点击它们即可预览并下载到您创建环境所在的同一目录中。

| 脚本 | 描述 | 用法 |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | 基本 LLM 文本生成 | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | 支持 Harmony 的文档摘要工具 | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

两个脚本均支持：
- 通过 `--model` 标志选择模型
- 用于正确进行模型提示的聊天模板格式化，对文档摘要尤其有用

## 加载并运行您的第一个 LLM

随附的 [run_llm.py](assets/run_llm.py) 脚本展示了如何使用 PyTorch 和 AMD ROCm 生成文本。

> **注意：** 当您加载模型时，ModelScope 会首先检查其本地缓存（Linux 上为 `~/.cache/modelscope/models`，Windows 上为 `C:\Users\<user>\.cache\modelscope\models`）。如果模型未被缓存，它会自动从 modelscope.cn 下载。首次运行可能需要几分钟，具体取决于模型大小和网络速度。

以下代码片段展示了如何使用该模型并自定义所提出的问题。

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from modelscope.hub.snapshot_download import snapshot_download

model_name = "${ms_model}"
model_dir = snapshot_download(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    local_files_only=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText
from modelscope.hub.snapshot_download import snapshot_download

model_name = "${ms_model}"
model_dir = snapshot_download(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
model = AutoModelForImageTextToText.from_pretrained(
    model_dir,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    local_files_only=True
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${ms_model}"
model_dir = snapshot_download(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    local_files_only=True
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

试用下载的脚本：

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${ms_model}
```
<!-- @test:end -->


## 构建文档摘要工具

既然您已经生成了本地 LLM 输出，接下来可以在此基础上构建一个实用的文档摘要工具。在本节中，您将使用 [summarizer.py](assets/summarizer.py) 脚本输入一个 .txt 文件，并自动生成简洁的摘要，全部在您的 GPU 上本地运行。

该脚本旨在开箱即用。请在编辑器中打开该脚本，以探索代码、自定义提示，并调整长度和温度等参数。

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${ms_model}
```
<!-- @test:end -->

### 用法示例

```bash
# Summarize the built-in example text (defaults to openai-mirror/gpt-oss-20b)
python summarizer.py --model ${ms_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## 了解生成参数

| 参数 | 控制内容 | 典型值 |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM 输出的最大长度 | 摘要使用 50–500 个 token。（1 个 token 约等于 0.75 个英文单词） |
| `temperature` | 创造力。较低的值使输出更集中，较高的值会带来更多不可预测性 | - **0.1–0.3**：集中、确定（适合摘要） <br> **0.5–0.7**：均衡（通用用途） <br> **0.8–1.0**：富有创意、多样化（头脑风暴） |
| `top_p` | 核采样（Nucleus Sampling）- 较低的值会将模型限制在更窄的输出范围内 | **0.1-0.5**：严格、可预测 <br> **0.9-0.95**：（标准、自然、对话式） |


## 实际应用

- **研究论文分析**：从复杂的出版物中提取关键发现，以便快速审阅
- **新闻聚合**：将新闻文章总结为简短的每日摘要或要点
- **会议记录**：将会议记录浓缩为可执行事项和简明摘要
- **法律文件审查**：从冗长的法律文本中快速提取相关条款或义务
- **代码文档**：生成简洁的代码仓库概述和函数说明

## 后续步骤

- **微调**：根据您的特定领域或术语调整模型以提高准确性（参见微调行动手册）
- **RAG 系统**：将 LLM 与文档检索相结合，实现具备上下文感知能力的问答和搜索
- **模型探索**：尝试使用 Llama 3、Phi-3 或 Qwen 等新模型以获得更好的结果
- **生产部署**：使用 vLLM 等工具在组织中实现可扩展的 LLM 服务

您的系统赋予您在本地运行复杂语言模型的能力。请尝试不同的模型、提示和参数，以发现最适合您应用场景的方案。
