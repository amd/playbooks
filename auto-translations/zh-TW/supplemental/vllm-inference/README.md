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

vLLM 是一款為大型語言模型（LLM）設計的高效能推論引擎。它提供具備連續批次處理（continuous batching）的最佳化服務，以達到高輸送量，並提供與 OpenAI 相容的 API，以實現無縫的應用程式整合。這使得 vLLM 非常適合用於對速度與資源效率要求嚴苛的生產環境部署。

本使用手冊將教您如何在整合式 GPU 上使用容器化的 vLLM 提供 LLM 服務，並透過 OpenAI Python API 與模型互動。

## 您將學到什麼

- 如何設定並啟動具備 AMD ROCm™ 支援的 vLLM 伺服器
- 如何透過與 OpenAI 相容的 API 端點與模型互動
- 如何使用 `vllm-prompt` 向本機伺服器傳送提示（prompt）

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

> **注意**：如果尚未安裝 VS Code，您可以使用 AMD Ryzen™ AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體必要條件

vLLM 在預先建置的容器中執行，其中已預先配對好 ROCm 及其相依項目。無需額外安裝。

主機端無需安裝 vLLM 的步驟。請使用以下指令啟動 vLLM：

```bash
vllm-launch
```

此啟動程式會啟動容器、以整合式 GPU 為目標，並公開一個與 OpenAI 相容的本機 vLLM 伺服器。或者，您也可以按一下工作列中的 vLLM 圖示。

## 快速入門

### 1. 確認 vLLM 伺服器正在執行

`vllm-launch` 可能需要幾分鐘才能完成所有初始化。啟動後，伺服器會在 `http://localhost:8001` 提供服務。請保持啟動終端機開啟，因為伺服器是在前景執行，接著開啟另一個獨立的終端機以進行後續步驟。以下範例使用 `Qwen/Qwen3-1.7B`；如果您的啟動程式設定為使用其他模型，請在請求中替換為該模型 ID。

### 2. 傳送提示

使用提供的 `vllm-prompt` 指令碼，向本機 vLLM 相容 OpenAI 伺服器傳送請求：

```bash
vllm-prompt "Tell me a story"
```

### 3. 使用 OpenAI Python API 與模型聊天

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

建立一個 `OpenAI` 用戶端，將其指向本機 vLLM 伺服器而非 OpenAI 的伺服器。用戶端需要 `api_key`，但 vLLM 不會驗證它，因此任何字串皆可使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

接著，傳送一個聊天完成請求。此請求使用與 OpenAI API 相同的訊息格式——一份包含如 `"user"` 與 `"assistant"` 等角色的訊息清單。設定 `stream=True` 表示回應將以增量方式抵達，而非一次全部傳回：

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

最後，逐一走訪串流傳回的區塊，並在每段文字抵達時將其列印出來：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

隨附的 [chat_with_model.py](assets/chat_with_model.py) 指令碼包含完整範例，可供下載。


## 選擇與設定模型

預設情況下，`vllm-launch` 會在連接埠 `8001` 上提供 `Qwen/Qwen3-1.7B` 作為測試模型。您可以在不重新建置或編輯容器的情況下，變更模型、連接埠以及 vLLM 服務參數。

### AMD 測試過的模型

以下模型已由 AMD 預先設定並驗證：

| 模型 | 備註 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | 預設模型。輕量且載入快速。 |
| `openai/gpt-oss-20b` | 較大型的模型，可提供更高品質的回應。 |

### 啟動不同的模型

使用 `--model`（或 `-m`）傳入模型 ID：

```bash
vllm-launch --model openai/gpt-oss-20b
```

### 變更連接埠

使用 `--port`（或 `-p`）傳入大於 1024 的連接埠；預設為 `8001`：

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

如果您變更了連接埠，請將用戶端的 `base_url` 指向相同的連接埠（例如 `http://localhost:8080/v1`）。

### 傳遞額外的 vLLM 參數

任何額外的引數都會直接轉送給 vLLM，因此您可以調整服務行為，例如內容長度（context length）或資料型別。有兩種方式可以提供這些引數。

**內嵌方式**，於啟動程式選項之後：

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**持久化方式**，於 `~/.local/share/vLLM/vllm-launch.conf` 的組態檔中。此檔案預設不存在——請自行建立，並以 Bash 陣列的形式加入您的引數：

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

使用 `+=` 以附加到預設引數，而非取代它們：

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

若要隨時檢視所有啟動程式選項，請執行：

```bash
vllm-launch --help
```

### 模型的儲存位置

`vllm-launch` 會在兩個位置尋找模型：

| 位置 | 路徑 |
|----------|------|
| 系統模型 | `/var/cache/models` |
| 使用者模型 | `~/.local/share/vLLM/models` |

您可以將下載的模型放置於上述任一目錄，並透過將其路徑或 ID 傳給 `--model` 來啟動：

```bash
vllm-launch --model /var/cache/models/my-model
```

> **注意**：以此方式執行您自行下載的模型，只要將模型放置於上述目錄之一，預期即可運作，但此工作流程尚未經 AMD 正式驗證。

## 疑難排解

### 連線遭拒

請確認伺服器正在執行：
```bash
curl http://localhost:8001/health
```

## 摘要

在本使用手冊中，您已學會如何：

- 在整合式 GPU 上啟動具備 ROCm 支援的容器化 vLLM
- 在連接埠 8001 上啟動具備 OpenAI 相容 API 端點的 vLLM 伺服器
- 使用 `vllm-prompt` 傳送提示
- 使用串流與非串流兩種請求方式，向 vLLM 伺服器發出 API 呼叫
- 排解伺服器啟動、記憶體以及用戶端連線方面的常見問題

您現在已擁有一套容器化的 vLLM 部署，可在整合式 GPU 上以最佳化效能提供大型語言模型服務。

## 後續步驟

- **嘗試不同的模型** — 使用 `vllm-launch --model <model>` 來試驗不同的 LLM 並比較效能（請參閱[選擇與設定模型](#choosing-and-configuring-a-model)）。
- **建置應用程式** — 使用與 OpenAI 相容的 API，將 vLLM 整合到 Python 應用程式、聊天機器人或自動化工作流程中。
- **微調並提供服務** — 使用 LoRA 或 QLoRA 微調模型，接著透過 vLLM 部署以獲得最佳化的推論效能。
## 其他資源

- **[vLLM 官方文件](https://docs.vllm.ai/)** — 完整的指南與 API 參考資料
- **[vLLM GitHub 儲存庫](https://github.com/vllm-project/vllm)** — 原始碼、問題回報與社群討論