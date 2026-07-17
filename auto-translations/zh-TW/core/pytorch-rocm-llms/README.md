<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概覽


想在自己的硬體上執行強大的 AI 語言模型嗎？本指南將為您說明如何操作。
本教學使用由 AMD ROCm™ 軟體驅動的 PyTorch 來執行可摘要文件、回答問題、生成文字等功能的模型，且全部在本地端執行。

## 您將學到的內容

- 使用 PyTorch 和 ROCm 在本地端執行 gpt-oss-20b 和 qwen3.5-4B 等 LLM
- 使用 LLM 建立文件摘要工具

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：若未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
在 Linux 上，於您選擇的目錄中開啟終端機，並依照以下指令建立已安裝 ROCm+Pytorch 的 venv。
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
**授予您的使用者存取 GPU 裝置的權限**（需登出後重新登入才能生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

在 Linux 上，於您選擇的目錄中開啟終端機，並依照以下指令建立 venv。
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
在 Windows 上，於您選擇的目錄中開啟終端機，並依照以下指令建立已安裝 ROCm+Pytorch 的 venv。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
在 Windows 上，於您選擇的目錄中開啟終端機，並依照以下指令建立 venv。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **提示**：Windows 使用者在執行某些 Powershell 指令前，可能需要修改 PowerShell 執行原則（例如
> 將其設定為 RemoteSigned 或 Unrestricted）。

<!-- @os:end -->

### 安裝基本相依套件
<!-- @require:driver,pytorch -->

### 安裝額外相依套件

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## 使用範例腳本快速開始

本 playbook 包含可直接使用的腳本。點擊它們即可預覽，並將其下載至您建立環境的相同目錄中。

| 腳本 | 說明 | 用法 |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | 基本 LLM 文字生成 | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | 支援 Harmony 的文件摘要工具 | `python summarizer.py --file document.txt` |

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

兩個腳本均支援：
- 透過 `--model` 旗標選擇模型
- 聊天範本格式化以正確提示模型，特別適用於文件摘要

## 載入並執行您的第一個 LLM

附帶的 [run_llm.py](assets/run_llm.py) 腳本示範如何使用 PyTorch 和 AMD ROCm 以 LLM 生成文字。

> **注意：** 載入模型時，Hugging Face Transformers 會先檢查其本地快取（Linux 上為 `~/.cache/huggingface/hub`，Windows 上為 `C:\Users\<user>\.cache\huggingface\hub`）。若模型尚未快取，則會自動從 huggingface.co 下載。首次執行可能需要幾分鐘，視模型大小和網路速度而定。

以下程式碼片段示範如何使用模型並自訂所提問的問題。

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

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

試用已下載的腳本：

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## 建立文件摘要工具

在您已生成本地 LLM 輸出之後，可以在此基礎上進一步建立實用的文件摘要工具。在本節中，您將使用 [summarizer.py](assets/summarizer.py) 腳本輸入一個 .txt 檔案，並自動生成簡潔的摘要，全部在您的 GPU 上本地執行。

該腳本設計為開箱即用。在編輯器中開啟腳本以探索程式碼、自訂提示，並調整長度和溫度等參數。

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### 使用範例

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## 了解生成參數

| 參數 | 控制內容 | 典型值 |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM 輸出的最大長度 | 摘要使用 50–500 個 token。（1 個 token 約等於 0.75 個英文單字） |
| `temperature` | 創意程度。低值使輸出更集中，高值則帶來更多不可預測性 | - **0.1–0.3**：集中、確定性（適合摘要） <br> **0.5–0.7**：平衡（一般用途） <br> **0.8–1.0**：富有創意、多樣化（腦力激盪） |
| `top_p` | 核採樣 - 低值將模型限制在更窄的輸出範圍 | **0.1-0.5**：嚴格、可預測 <br> **0.9-0.95**：（標準、自然、對話式） |


## 實際應用場景

- **研究論文分析**：從複雜的出版物中提取關鍵發現，以便快速審閱
- **新聞彙整**：將新聞文章摘要為簡短的每日摘要或重點
- **會議記錄**：將逐字稿濃縮為可執行的行動項目和簡潔摘要
- **法律文件審閱**：快速從冗長的法律文本中提取相關條款或義務
- **程式碼文件**：生成簡潔的儲存庫概覽和函式說明

## 後續步驟

- **微調**：將模型調整至您的特定領域或術語以提升準確性（請參閱微調 Playbooks）
- **RAG 系統**：將 LLM 與文件檢索結合，以實現具情境感知的回答和搜尋
- **模型探索**：嘗試 Llama 3、Phi-3 或 Qwen 等新模型以獲得更好的結果
- **生產部署**：使用 vLLM 等工具在組織中提供可擴展的 LLM 服務

您的系統賦予您在本地端執行複雜語言模型的能力。嘗試不同的模型、提示和參數，探索最適合您應用場景的組合。