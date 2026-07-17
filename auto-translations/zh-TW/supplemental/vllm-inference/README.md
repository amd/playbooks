<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 此教學手冊使用 GitHub 無法渲染的特殊標籤。請前往 [amd.com/playbooks](https://amd.com/playbooks) 以正確預覽此內容。
<!-- @github-only:end -->


## 概覽

vLLM 是一款專為大型語言模型（LLM）設計的高效能推論引擎。它提供具備連續批次處理的最佳化服務以實現高吞吐量，並提供與 OpenAI 相容的 API 以便無縫整合應用程式。這使得 vLLM 非常適合對速度和資源效率要求嚴苛的生產環境部署。

此教學手冊將教您如何使用容器化的 vLLM 在整合式 GPU 上提供 LLM 服務，並透過 OpenAI Python API 與模型互動。

## 您將學到的內容

- 如何設定並啟動具備 AMD ROCm™ 支援的 vLLM 伺服器
- 如何透過與 OpenAI 相容的 API 端點與模型互動
- 如何使用 `vllm-prompt` 向本地伺服器發送提示

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

> **注意**：若未安裝 VS Code，您可以透過 AMD Ryzen™ AI 開發者中心進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

此教學手冊使用預先建置的容器映像，其中已包含 vLLM、ROCm 支援以及啟動伺服器所需的輔助腳本。您無需手動安裝 PyTorch、vLLM 或本地教學手冊腳本。

主機端無需執行 vLLM 安裝步驟。請使用以下指令啟動 vLLM：

```bash
vllm-launch
```

啟動器會啟動容器、以整合式 GPU 為目標，並公開一個本地與 OpenAI 相容的 vLLM 伺服器。您也可以點擊工作列中的 vLLM 圖示來啟動。

## 快速入門

### 1. 確認 vLLM 伺服器正在執行

`vllm-launch` 可能需要幾分鐘來完成初始化。啟動後，伺服器將可在 `http://localhost:8001` 存取。請保持啟動終端機開啟，因為伺服器在前景執行，然後另開一個終端機執行後續步驟。以下範例使用 `Qwen/Qwen3-1.7B`；若您的啟動器設定為不同的模型，請在請求中替換為該模型 ID。

### 2. 發送提示

使用提供的 `vllm-prompt` 腳本向本地 vLLM 與 OpenAI 相容的伺服器發送請求：

```bash
vllm-prompt "Tell me a story"
```

### 3. 使用 OpenAI Python API 與模型對話

由於 vLLM 公開了與 OpenAI 相容的 API，您可以使用 `openai` Python 套件與其互動。

首先，建立一個 Python 虛擬環境：

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

安裝 OpenAI 套件
```bash
pip install openai
```

建立一個指向本地 vLLM 伺服器（而非 OpenAI 伺服器）的 `OpenAI` 用戶端。用戶端需要 `api_key`，但 vLLM 不會驗證它，因此任何字串均可使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

接著，發送一個聊天補全請求。此請求使用與 OpenAI API 相同的訊息格式——一個包含 `"user"` 和 `"assistant"` 等角色的訊息列表。設定 `stream=True` 表示回應將以漸進方式傳送，而非一次全部傳回：

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

最後，迭代串流區塊並在每段文字到達時逐一列印：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

附帶的 [chat_with_model.py](assets/chat_with_model.py) 腳本包含完整範例，可供下載。


## 疑難排解

### 連線被拒絕

請確認伺服器正在執行：
```bash
curl http://localhost:8001/health
```

## 總結

在此教學手冊中，您學到了如何：

- 在整合式 GPU 上以 ROCm 支援啟動容器化的 vLLM
- 啟動具備與 OpenAI 相容 API 端點的 vLLM 伺服器（連接埠 8001）
- 使用 `vllm-prompt` 發送提示
- 使用串流與非串流請求對 vLLM 伺服器進行 API 呼叫
- 針對伺服器啟動、記憶體及用戶端連線的常見問題進行疑難排解

您現在已擁有一個容器化的 vLLM 部署，可在整合式 GPU 上以最佳化效能提供大型語言模型服務。

## 後續步驟

- **嘗試不同的模型** — 在 `vllm-launch` 設定中替換模型，以實驗不同的 LLM 並比較效能。
- **建置應用程式** — 使用與 OpenAI 相容的 API，將 vLLM 整合至 Python 應用程式、聊天機器人或自動化工作流程中。
- **微調並部署** — 使用 LoRA 或 QLoRA 對模型進行微調，然後透過 vLLM 部署以實現最佳化推論。

## 其他資源

- **[vLLM 官方文件](https://docs.vllm.ai/)** — 完整指南與 API 參考資料
- **[vLLM GitHub 儲存庫](https://github.com/vllm-project/vllm)** — 原始碼、問題回報與社群討論