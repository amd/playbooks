<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> 此手冊使用 GitHub 無法呈現的特殊標籤。請造訪 [amd.com/playbooks](https://amd.com/playbooks) 以正確預覽此內容。
<!-- @github-only:end -->


## 總覽

vLLM 是一款專為大型語言模型（LLM）設計的高效能推論引擎。它提供具備連續批次處理的最佳化服務，以達到高輸送量，並提供與 OpenAI 相容的 API，實現無縫的應用程式整合。這使得 vLLM 非常適合對速度與資源效率要求嚴格的正式環境部署。

本手冊將教您如何在內顯 GPU 上使用容器化的 vLLM 服務 LLM，並透過 OpenAI Python API 與模型互動。

## 您將學到什麼

- 如何設定並啟動具備 AMD ROCm™ 支援的 vLLM 伺服器
- 如何透過與 OpenAI 相容的 API 端點與模型互動
- 如何使用 `vllm-prompt` 將提示詞傳送至本機伺服器

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

> **注意**：若尚未安裝 VS Code，您可以透過 AMD Ryzen™ AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

本手冊使用預先建置的容器映像，其中已包含 vLLM、ROCm 支援，以及啟動伺服器所需的輔助指令碼。您無需手動安裝 PyTorch、vLLM 或本機手冊指令碼。

主機端無需執行 vLLM 安裝步驟。請使用以下指令啟動 vLLM：

```bash
vllm-launch
```

啟動程式會啟動容器、鎖定內顯 GPU，並公開一個本機的 OpenAI 相容 vLLM 伺服器。您也可以點選工作列中的 vLLM 圖示。

## 快速入門

### 1. 確認 vLLM 伺服器正在執行

`vllm-launch` 可能需要數分鐘才能完成所有初始化。啟動後，伺服器將可透過 `http://localhost:8001` 存取。請保持啟動用的終端機開啟，因為伺服器是以前景方式執行，接著再開啟另一個終端機以進行後續步驟。以下範例使用 `Qwen/Qwen3-1.7B`；若您的啟動程式設定為其他模型，請在請求中替換為該模型的 ID。

### 2. 傳送提示詞

使用提供的 `vllm-prompt` 指令碼，將請求傳送至本機的 vLLM OpenAI 相容伺服器：

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

建立一個指向本機 vLLM 伺服器（而非 OpenAI 伺服器）的 `OpenAI` 用戶端。用戶端需要提供 `api_key`，但 vLLM 不會驗證此值，因此任意字串皆可使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

接著，傳送一個聊天完成請求。這使用與 OpenAI API 相同的訊息格式——一個包含如 `"user"` 與 `"assistant"` 等角色的訊息清單。將 `stream=True` 設定為啟用後，回應將以逐步方式抵達，而非一次全部傳回：

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

最後，遍歷串流回傳的區塊，並在每段文字抵達時將其印出：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

所附的 [chat_with_model.py](assets/chat_with_model.py) 指令碼包含完整範例，可供下載。


## 疑難排解

### 連線遭拒

請確認伺服器正在執行：
```bash
curl http://localhost:8001/health
```

## 總結

在本手冊中，您學到了如何：

- 在內顯 GPU 上啟動具備 ROCm 支援的容器化 vLLM
- 啟動具備 OpenAI 相容 API 端點（於連接埠 8001）的 vLLM 伺服器
- 使用 `vllm-prompt` 傳送提示詞
- 使用串流與非串流請求兩種方式，向 vLLM 伺服器發出 API 呼叫
- 排解與伺服器啟動、記憶體及用戶端連線相關的常見問題

您現在已擁有一套容器化的 vLLM 部署，可在內顯 GPU 上以最佳化效能服務大型語言模型。

## 後續步驟

- **嘗試不同模型** — 在 `vllm-launch` 設定中替換模型，以體驗不同的 LLM 並比較效能。
- **建置應用程式** — 使用與 OpenAI 相容的 API，將 vLLM 整合至 Python 應用程式、聊天機器人或自動化工作流程中。
- **微調並提供服務** — 使用 LoRA 或 QLoRA 微調模型，再透過 vLLM 部署以進行最佳化推論。

## 其他資源

- **[vLLM 官方文件](https://docs.vllm.ai/)** — 完整指南與 API 參考資料
- **[vLLM GitHub 儲存庫](https://github.com/vllm-project/vllm)** — 原始碼、問題回報與社群討論