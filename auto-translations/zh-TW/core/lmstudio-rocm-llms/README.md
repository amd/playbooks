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

LM Studio 是一個功能強大的 GUI 包裝工具,用於 [llama.cpp](https://github.com/ggml-org/llama.cpp),同時也提供 [符合 OpenAI 規範的端點](https://lmstudio.ai/docs/developer/openai-compat) 以進行本機模型服務。LM Studio 提供簡單但功能強大的介面,可輕鬆下載和部署模型。LM Studio 為 AMD 使用者提供 Vulkan 和 AMD ROCm™ 軟體後端(稱為執行環境)。


## 您將學到什麼
- 如何設定並使用 LM Studio 以充分運用您的本機硬體
- 在完全離線的環境中測試和管理 LLM
- 透過 OpenAI 相容 API 提供模型服務,以支援自訂工作流程和應用程式


## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @os:linux -->
> **注意**:您可以透過 AMD Ryzen™ AI Developer Center 安裝 VS Code。至於 LM Studio,請依照下方安裝說明進行。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:如果尚未安裝 VS Code 或 LM Studio,您可以從 AMD Ryzen™ AI Developer Center 進行安裝。 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## 下載模型

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## 與 LLM 對話
了解如何開始與完全在本機執行、達到 ChatGPT 等級的 LLM 進行對話。  

1. 開啟 LMStudio。
2. 按下 `Ctrl + L` 開啟模型載入器,選取 `Manually choose model load parameters`,然後點選 `${model_name}`
3. 確認已勾選「show advanced settings」。  
4. 依需求變更 `Context Length`。內容長度越高代表模型記憶體使用量越大,但會使用更多系統記憶體。此手冊建議設定為 4096。
5. 確認 `GPU Offload` 已設定為最大,且 `Flash Attention` 為開啟狀態(Cache Quantizations 可保持關閉)。
6. 勾選 `Remember settings` 並點選 `Load Model`。
7. 若不在聊天視窗中,請按下 `Ctrl + 1` 或點選畫面左上方的 👾 按鈕。
8. 傳送訊息,開始與模型互動!

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **提示**:內容長度指的是模型的記憶容量。Flash attention 可提升處理速度,同時降低記憶體使用量。GPU Offload 會將運算工作轉移至顯示卡,以獲得更快的回應速度。

## 透過符合 OpenAI 規範的端點提供 LLM 服務

LM Studio 也以 LM Studio Server 的形式提供符合 OpenAI 規範的端點。這已在 [此處](../playbooks/vscode-qwen3-coder) 使用 Cline 的代理式程式碼撰寫工作流程中展示過。另一個常見用例是透過將標準 HTTP 請求傳送至推論端點,將 LM Studio Server 連接至任何網頁應用程式(React、Node.js、Python)。

若要設定 LM Studio Server,請依照以下說明操作:

1. 在左側,點選 `Developer` 標籤(命令列圖示)或按下 `Ctrl + 2`,然後點選 `Server Settings`。  
2. (選用):若您想在區域網路上提供模型服務,請勾選 `Serve on Local Network`。若您想搭配網站使用,或在 VS Code 中進行大量呼叫,請勾選 `Enable CORS`。 
3. 在左上角,透過點選 `Status` 前方的切換按鈕,確認伺服器正在執行中。
4. 現在符合 OpenAI 規範的端點即已在執行。位址通常為 http://127.0.0.1:1234  
5. 若尚未載入模型,您可以依照先前提到的步驟,點選 `Load Model` 來載入模型。 

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


此模型現在可透過 LM Studio Server 端點存取,並支援包括以下項目在內的 OpenAI 端點:

| 端點 | 方法 | 文件 |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### 範例:對您的端點進行 Ping 測試
剛剛建立了 OpenAI 相容端點,接下來讓我們看看如何將其整合到 Python 開發環境中(例如 VSCode),並將您的系統用作本機 API 供應商。

1. 建立 Python 虛擬環境:

<!-- @os:linux -->
<!-- @device:halo_box -->
    在 Linux 上,於您選擇的目錄中開啟終端機,並依照下列指令建立 venv。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予您的使用者存取 GPU 裝置的權限**(登出並重新登入後才會生效):

```bash
sudo usermod -aG render,video $LOGNAME
```

    在 Linux 上,於您選擇的目錄中開啟終端機,並依照下列指令建立 venv。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    在 Windows 上,於您選擇的目錄中開啟終端機,並依照下列指令建立 venv。
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **提示**:Windows 使用者在執行某些 PowerShell 指令之前,可能需要修改其 PowerShell 執行原則(例如將其設定為 RemoteSigned 或 Unrestricted)。

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    在 Windows 上,於您選擇的目錄中開啟終端機,並依照下列指令建立 venv。
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **提示**:Windows 使用者在執行某些 PowerShell 指令之前,可能需要修改其 PowerShell 執行原則(例如將其設定為 RemoteSigned 或 Unrestricted)。

<!-- @device:end -->
<!-- @os:end -->

2. 安裝 OpenAI 套件
    ```bash
    pip install openai
    ```

3. 執行下列指令碼來對我們剛建立的端點進行 Ping 測試。
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### (選用):在執行環境之間切換

1. 在鍵盤上按下 `Ctrl + Shift + R`。或者,點擊左側的 `Discover` 分頁(放大鏡圖示),然後在彈出視窗中點擊 `Runtime`。   
2. 接著您應該會看到 `Runtime Selections`,可以使用下拉式選單來變更執行環境。


## 後續步驟

- **自訂應用程式整合**:使用本機 OpenAI 相容 API,整合您自己的 Python 指令碼或應用程式。
- **進階前端介面**:將 Open WebUI 等強大介面連接到您的伺服器,以進行聊天記錄與角色管理。

如需更多文件,請造訪:https://lmstudio.ai/docs/developer