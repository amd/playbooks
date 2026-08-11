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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概觀

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一款 AI 軟體代理程式，能夠撰寫程式碼、執行命令、瀏覽網頁，並在實際的工作區中編輯檔案。您不需要從聊天視窗中複製建議，而是將代理程式指向專案資料夾，讓它實際完成工作：實作功能、修復錯誤、撰寫測試，或說明程式碼庫。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是執行 OpenHands 建議使用的瀏覽器使用者介面。只需一個 `agent-canvas` 指令，就能同時啟動代理程式伺服器、自動化後端，以及網頁前端，讓您可以透過瀏覽器與代理程式進行對話。

為了讓所有內容都保留在您的 AMD 系統上，代理程式會與 Lemonade Server 所提供的本機模型進行通訊。Lemonade 透過與 OpenAI 相容的 API 公開該模型，因此 Agent Canvas 可以像設定任何其他 OpenAI 風格的端點一樣進行設定，而模型、您的程式碼，以及對話內容則全部保留在您的機器上。

在本手冊中，您將啟動一個本機模型、啟動 Agent Canvas、將其指向該模型，並針對一個實際的專案資料夾執行您的第一個程式撰寫工作。

## 您將學到什麼

- 如何啟動 Lemonade Server，並確認本機模型能夠回應聊天請求
- 如何從 npm 套件安裝並啟動 Agent Canvas
- 如何設定 Agent Canvas 以使用本機 Lemonade 模型作為 LLM
- 如何開始一個 OpenHands 對話，並觀察代理程式在工作區中編輯檔案及執行命令
- 如何檢視代理程式所做的變更，並透過後續訊息引導它

## 核心概念

| 概念 | 這是什麼 | 在本手冊中的定位 |
| --- | --- | --- |
| Lemonade Server | 一個專為 AMD 硬體打造的本機 LLM 服務平台，能公開與 OpenAI 相容的 API。您的資料永遠不會離開您的機器。 | 執行為代理程式提供支援的模型。 |
| OpenHands | 一款 AI 軟體代理程式，能在工作區中讀取及編輯檔案、執行殼層命令，並瀏覽網頁。 | 您透過聊天所驅動的代理程式。 |
| Agent Canvas | 執行 OpenHands 對話並顯示工具呼叫與檔案變更的瀏覽器使用者介面及後端。 | 啟動整套系統並代管您的對話。 |
| 工作區 | 允許代理程式讀取及修改的專案資料夾。 | 代理程式編輯及命令的目標對象。 |

<!-- @device:stx,krk -->
> [!NOTE]
> 撰碼代理程式工作流程受益於較大的模型與情境視窗。請至少使用 32 GB 的系統記憶體，若使用較大的 GGUF 模型，建議使用 64 GB 或以上。
<!-- @device:end -->

## 先決條件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

您需要：

- 已安裝 Lemonade Server，並能夠提供下方的模型服務。
- Node.js 22.12 或更新版本，以及 `npm`（`agent-canvas` CLI 需要使用）。
- `uv`，這是 Agent Canvas 用來管理代理程式伺服器環境的 Python 套件管理員。若您的系統尚未安裝，請在啟動 Agent Canvas 之前，從 [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 進行安裝。
- 一個您要在其中工作的專案資料夾。這可以是任何本機 git 儲存庫，或您希望代理程式處理的程式碼目錄。

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. 啟動 Lemonade Server

從 Lemonade CLI 啟動模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade 會在以下位置公開與 OpenAI 相容的 API：

```text
http://127.0.0.1:13305/api/v1
```



## 2. 驗證本機模型

確認 Lemonade 能夠提供所選模型的服務：

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

接著傳送一個小型的聊天請求：

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

如果傳回一個 `choices` 陣列，代表 Lemonade 已準備好供 Agent Canvas 使用。

## 3. 安裝並啟動 Agent Canvas

全域安裝已發布的 Agent Canvas 套件：

```bash
npm install -g @openhands/agent-canvas
```

接著從終端機啟動完整的堆疊：

```bash
agent-canvas
```

根據預設，Agent Canvas 會在 `http://localhost:8000` 上啟動。請在您的瀏覽器中開啟該網址。若埠 8000 已被使用，請在啟動 Agent Canvas 時傳入 `--port`（或 `-p`）：

```bash
agent-canvas --port 3000
```

在 Windows 的 PowerShell 中也可使用相同的指令。接著改為開啟 `http://localhost:3000`。預設的本機後端應在首頁上顯示為健康狀態。

`agent-canvas` 指令會同時啟動代理程式伺服器、自動化後端，以及網頁前端。您只需要這一個指令，就能在本機執行 OpenHands。

## 4. 設定本機 LLM

第一次啟動時，Agent Canvas 會開啟一個入門流程。在該流程中：

1. 保持選取 **OpenHands** 作為代理程式，然後點選 **Next**。
2. 在 **Set up your LLM** 中，選取 **Advanced**。
3. 保持 **Authentication** 設定為 **API key**。
4. 將 **Custom Model** 設定為 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 將 **Base URL** 設定為 `http://127.0.0.1:13305/api/v1`。
6. 對於 **API Key**，請輸入任何非空白的預留值，例如 `lemonade-local`。Lemonade 不需要真實的金鑰，但 OpenHands 用戶端需要一個值才能傳送。
7. 點選 **Next**。

完成後的 Advanced 設定應如下所示。API 金鑰欄位會由使用者介面遮蔽顯示。

![Agent Canvas 首次使用時的 LLM Advanced 設定，顯示 Lemonade 模型與本機基礎網址](assets/01-llm-advanced-settings.png)

Agent Canvas 會將這些值儲存為一個 LLM 設定檔。若您的版本要求您為該設定檔命名，請使用不含空格的名稱，例如 `lemonade-local`。若您之後想更換模型，請開啟 **Settings > LLM** 並更新相同的 Advanced 欄位。您可以透過聊天輸入框中的 `/model` 指令，切換已儲存的設定檔。

## 5. 開啟工作區

代理程式只能讀取及修改您所選擇的工作區內的檔案。在開始工作之前，請將 Agent Canvas 指向您的專案資料夾：

1. 從首頁選擇 **Open Workspace**。
2. 選取包含您專案的資料夾（例如，您希望代理程式處理的 git 儲存庫）。
3. 在該工作區中開始一個新對話。

代理程式所做的一切——讀取檔案、執行命令、編輯程式碼——都僅限於該工作區的範圍內。

![入門完成後的 Agent Canvas 首頁](assets/02-agent-canvas-home.png)
## 6. 執行你的第一個編碼任務

在開啟工作區並選好本機 LLM 後，於聊天視窗輸入一個具體的任務。一個好的入門任務應該規模小且容易驗證，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

觀察對話時間軸。OpenHands 會：

- 讀取工作區以了解結構。
- 建立 `hello.py`，內含所需的函式與測試區塊。
- 視情況執行 `python3 hello.py` 以驗證輸出結果。
- 在聊天中回報它做了什麼以及任何指令輸出。

你應該會看到新檔案出現在工作區中，且代理程式的最終訊息會描述它所做的變更。這正是關鍵時刻：代理程式在你的專案資料夾中撰寫並執行了實際的程式碼。

## 7. 檢視並引導代理程式

代理程式完成一個步驟後，先檢視其成果，再接受下一步：

- **檔案變更**：使用工作區檔案瀏覽器或代理程式的差異檢視，查看確切新增、變更或刪除了哪些內容。
- **指令輸出**：展開代理程式執行的任何指令，以查看 stdout、stderr 及結束代碼（exit code）。
- **後續調整**：如果結果不是你想要的，可在同一段對話中回覆更正內容。代理程式會保留先前的脈絡，並針對同一批檔案繼續調整。

舉例來說，如果測試沒有印出預期的問候語，可以回覆：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

代理程式會重新讀取檔案、執行指令、診斷問題，並再次修改該檔案——全部都在同一段對話中完成。

## 疑難排解

- **`agent-canvas` 不在 PATH 中：** 請重新安裝
  `npm install -g @openhands/agent-canvas`，並確認 npm 全域執行檔目錄
  已加入你的 PATH。在 Windows 上，執行 `npm config get prefix`；
  回傳的目錄（通常是 `%APPDATA%\npm` 或 `%USERPROFILE%\.npm-global`）
  必須先加入使用者 PATH，才能在新的終端機中啟動 `agent-canvas`。
- **`npm install -g` 因權限錯誤而失敗：** 設定一個使用者擁有的
  全域 npm 目錄，然後重新開啟終端機並再次安裝 Agent Canvas。

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  若要將此 Windows PATH 變更永久生效，請至 **設定 > 系統 > 關於 > 進階系統設定 >
  環境變數**，將 `%USERPROFILE%\.npm-global` 加入你的使用者 PATH，
  並開啟一個新的終端機。
  <!-- @os:end -->
- **UI 已載入但後端顯示不健康：** 請稍候幾秒鐘，讓
  代理程式伺服器完成啟動，然後重新整理。如果仍顯示不健康，請重新啟動
  `agent-canvas`，並查看終端機輸出以檢查錯誤。
- **Lemonade 聊天請求因連線錯誤而失敗：** 請確認
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 執行成功，並確認
  Lemonade 仍以 `lemonade status` 提供該模型的服務。
- **代理程式因內容長度或權杖上限訊息而發生錯誤：** 請以較大的
  `ctx_size`（例如 `ctx_size=65536`）重新啟動 Lemonade，並開始一段
  全新的對話，以免代理程式攜帶過大的歷史紀錄。
- **代理程式產生品質不佳或不完整的編輯結果：** 請切換到 Lemonade 中
  較大的模型，或給代理程式一個較小、較具體的任務，並讓它完成後
  再要求下一項變更。
- **找不到 `uv`：** 請從
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/)進行安裝。
  Agent Canvas 使用 `uv` 來管理代理程式伺服器的 Python 環境。

## 後續步驟

- 在同一個工作區中嘗試更大型的任務，例如新增一個單元測試檔案或
  修正一個已知的錯誤，並在保留變更之前檢視代理程式的差異內容。
- 在 **自訂** 底下連接 MCP 伺服器，例如 GitHub 或 Slack，讓
  代理程式在工作時能讀取議題或發佈更新。
- 儲存數個 LLM 設定檔（一個快速的小型模型與一個較強大的大型模型），並在
  對話過程中使用 `/model` 於它們之間切換。
- 前往 [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)，
  將重複性的開發流程轉換為排程或事件觸發的代理程式執行。

## 資源

- [OpenHands 文件](https://docs.openhands.dev/)
- [Agent Canvas 總覽](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 設定](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 設定檔與模型組態](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 文件](https://lemonade-server.ai/docs)