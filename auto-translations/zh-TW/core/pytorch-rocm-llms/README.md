<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概觀


想在自己的硬體上執行強大的 AI 語言模型嗎？本指南將說明如何操作。
本教學課程使用由 AMD ROCm™ 軟體驅動的 PyTorch，執行可摘要文件、回答問題、產生文字等功能的模型，且全部在本機執行。

## 您將學到的內容

- 使用 PyTorch 和 ROCm 在本機執行 gpt-oss-20b 和 qwen3.5-4B 等 LLM
- 建立使用 LLM 的文件摘要工具

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體組態

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：如果尚未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體必要條件

### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
在 Linux 上，於您選擇的目錄中開啟終端機，並依照下列指令建立已預先安裝 ROCm+Pytorch 的 venv。
<!-- @test:id=create-venv timeout=300 -->
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
**授予您的使用者存取 GPU 裝置的權限**（登出再重新登入後生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

在 Linux 上，於您選擇的目錄中開啟終端機，並依照下列指令建立 venv。
<!-- @test:id=create-venv timeout=300 -->
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
在 Windows 上，於您選擇的目錄中開啟終端機，並依照下列指令建立已預先安裝 ROCm+Pytorch 的 venv。
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
在 Windows 上，於您選擇的目錄中開啟終端機，並依照下列指令建立 venv。
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **提示**：在執行某些 PowerShell 指令之前，Windows 使用者可能需要修改其 PowerShell 執行原則（例如，
> 將其設定為 RemoteSigned 或 Unrestricted）。

<!-- @os:end -->

### 安裝基本相依性
<!-- @require:driver,pytorch -->

### 安裝其他相依性

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->
<!-- @device:halo,halo_box -->
<!-- @prereq:hf-models-gpt-oss-20b -->
<!-- @device:end -->
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:hf-models-qwen3-5-4b -->
<!-- @device:end -->

<!-- @device:halo,halo_box -->
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **注意：** 如果模型無法載入或記憶體不足，請嘗試安裝 `kernels` 套件，以優化量化方式載入模型。
>
> ```bash
> # 使用與 Transformers 版本相容的此版本
> pip install "kernels==0.14.1" 
> ```
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## 使用範例指令碼快速入門

此操作手冊包含可直接使用的指令碼。點擊它們即可預覽，並將其下載到您所建立環境的相同目錄中。

| 指令碼 | 說明 | 用法 |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | 基本 LLM 文字產生 | `python run_llm.py` |
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

這兩個指令碼都支援：
- 透過 `--model` 旗標選擇模型
- 聊天範本格式化，以實現正確的模型提示，對文件摘要特別有用

## 載入並執行您的第一個 LLM

隨附的 [run_llm.py](assets/run_llm.py) 指令碼展示了如何使用 PyTorch 和 AMD ROCm 產生文字。

> **注意：** 當您載入模型時，Hugging Face Transformers 會先檢查其本機快取（Linux 上為 `~/.cache/huggingface/hub`，Windows 上為 `C:\Users\<user>\.cache\huggingface\hub`）。如果模型未被快取，則會自動從 huggingface.co 下載。第一次執行可能需要幾分鐘，視模型大小和網路速度而定。

下方程式碼片段展示了如何使用模型並自訂所提出的問題。

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
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
    device_map="auto",
    disable_mmap=True
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

試用下載的指令碼：

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## 建立文件摘要工具

既然您已產生本機 LLM 輸出，您可以進一步建立實用的文件摘要工具。在本節中，您將使用 [summarizer.py](assets/summarizer.py) 指令碼讀入 .txt 檔案，並自動產生精簡摘要，全部在您的 GPU 上本機執行。

此指令碼設計為開箱即用。在編輯器中開啟指令碼，即可探索程式碼、自訂提示，並調整長度和溫度等參數。

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

## 瞭解生成參數

| 參數 | 控制內容 | 典型值 |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM 輸出的最大長度 | 摘要建議使用 50–500 個 token（1 個 token 約為 0.75 個英文單字） |
| `temperature` | 創意程度。數值低則輸出較集中，數值高則較不可預測 | - **0.1–0.3**：集中、確定性高（適合摘要） <br> **0.5–0.7**：平衡（一般用途） <br> **0.8–1.0**：富有創意、多樣化（腦力激盪） |
| `top_p` | 核採樣（Nucleus Sampling）- 數值低會限制模型輸出範圍更窄 | **0.1-0.5**：嚴格、可預測 <br> **0.9-0.95**：（標準、自然、對話式） |


## 實際應用場景

- **研究論文分析**：從複雜的出版物中萃取關鍵發現，以便快速檢閱
- **新聞彙整**：將新聞文章摘要成簡潔的每日摘要或重點
- **會議記錄**：將逐字稿濃縮為可執行項目與簡潔摘要
- **法律文件審查**：快速從冗長的法律文件中萃取相關條款或義務
- **程式碼文件**：產生簡潔的儲存庫概觀和函式說明
## 後續步驟

- **微調 (Fine-tuning)**：針對您的特定領域或專業術語調整模型以提升準確度（請參閱 Fine-tuning Playbooks）
- **RAG 系統**：將 LLM 與文件檢索結合，以實現具備情境感知能力的回答與搜尋
- **模型探索**：嘗試使用 Llama 3、Phi-3 或 Qwen 等新模型，以獲得更好的結果
- **生產環境部署**：使用 vLLM 等工具，在組織中進行可擴展的 LLM 服務部署

您的系統讓您能夠在本地端執行複雜的語言模型。請嘗試不同的模型、提示詞與參數，找出最適合您應用情境的組合。