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

開發人員花費大量時間在小型的重複性循環工作上:審查已標記的 pull request、回覆 GitHub 留言、分類新的 issue、將 Slack 討論串轉換成站立會議紀錄或事件後續追蹤,以及追蹤發布或研究相關訊號。每個循環都很熟悉,但仍需要判斷力:蒐集正確的內容脈絡、決定重要事項,並在團隊已在使用的地方張貼清楚的更新內容。

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)
將這些循環轉變為排程或事件觸發的 agent 對話:在這些執行過程中,AI 軟體 agent 可以讀取內容脈絡、呼叫工具,並產生更新內容。OpenHands extensions catalog 中共用的自動化範本針對 GitHub pull request 審查、儲存庫監控、Linear issue 分類、事件回顧、Slack 站立會議摘要以及研究簡報,都遵循相同的模式:自動化程序啟動、使用已設定的整合服務(例如 GitHub 或 Slack)擷取內容脈絡、透過大型語言模型(LLM)對該內容脈絡進行推理,然後寫回結果。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是用於建置與測試這些自動化的本機控制平面。在此手冊中,它會執行 OpenHands Agent Server(執行 agent 對話的後端程序),並將 agent 連接到 GitHub 與 Slack 等外部服務。

為了將工作流程保留在您的 AMD 系統上,agent 會與 Lemonade Server 提供的本機模型進行通訊。Lemonade 透過與 OpenAI 相容的 API 公開該模型,因此 Agent Canvas 可以將其設定為遠端 OpenAI 樣式的端點,同時讓模型、提示與工作流程內容脈絡都保留在本機。

在此手冊中,您將建置一個具體的自動化程序:一個排程的 GitHub 至 Slack 開發摘要。此自動化程序使用 GitHub 檢視近期的儲存庫活動、使用 Slack 張貼摘要、使用 Agent Canvas API 呼叫來設定與測試自動化程序,並使用 Lemonade 在本機執行 LLM。

![顯示 GitHub MCP、OpenHands automation、Lemonade Server 與 Slack MCP 的架構圖](assets/00-architecture-overview.png)

## 您將學到的內容

- 如何啟動 Lemonade Server 並驗證本機模型可回應聊天請求
- 如何啟動 Agent Canvas 並將其 Agent Server 指向本機 LLM
- 如何透過 Agent Server API 安裝 GitHub 與 Slack Model Context Protocol (MCP) 伺服器
- 如何建立並調度一個會將開發摘要張貼到 Slack 的排程 OpenHands automation
- 如何排解最常見的本機模型與自動化程序失敗問題

## 核心概念

| 概念 | 說明 | 在此手冊中的定位 |
| --- | --- | --- |
| Lemonade Server | 一個專為 AMD 硬體打造的本機 LLM 服務平台,提供與 OpenAI 相容的 API。您的資料不會離開您的電腦。 | 執行驅動 agent 的模型。 |
| OpenHands Agent Server | 執行 OpenHands agent 對話的後端程序。 | 承載 agent、其 LLM 設定檔以及其 MCP 伺服器。 |
| Agent Canvas | OpenHands 的本機控制平面,可執行 Agent Server 以及用於檢視 agent 執行狀況的 UI。 | 啟動後端程序並提供您所呼叫的 API。 |
| MCP server | 一種 Model Context Protocol 伺服器,可為 agent 提供 GitHub 或 Slack 等外部服務的工具。 | 讓 agent 能夠讀取 GitHub 並寫入 Slack。 |
| OpenHands automation | 一種排程或事件觸發的 agent 對話,會擷取內容脈絡、對其進行推理,並將結果寫入某處。 | 您在此建置的 GitHub 至 Slack 摘要。 |

<!-- @device:stx,krk -->
> [!NOTE]
> 編碼 agent 工作流程受益於更大的模型與內容脈絡視窗。請至少使用 32 GB 的系統記憶體,對於較大的 GGUF 模型,建議使用 64 GB 或更多。
<!-- @device:end -->

## 先決條件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

您需要:

- 依照標準的 [Lemonade 安裝指南](https://lemonade-server.ai/docs/guide/install/) 安裝 Lemonade Server。
- Node.js 22.12 或更新版本以及 `npm`,用於安裝已發佈的 Agent Canvas CLI,並透過 `npx` 執行 MCP 伺服器。
- 一個最新已發佈的 `@openhands/agent-canvas` 套件,具備結構定義驅動的 agent 設定、`LLMSummarizingCondenserSettings.max_tokens`,以及 LLM 的 `custom_tokenizer` 支援。
- Agent Server 環境中須提供 Python 的 `transformers` 套件。設定 `custom_tokenizer` 時,需要此套件來進行聊天範本 token 計數。
- 一個具備您想摘要的儲存庫讀取權限的 GitHub token。
- 一個具備 `chat:write` 與頻道讀取權限的 Slack bot token(`xoxb-...`)。
- 一個 Slack team ID(`T...`)。
- 一個用於張貼摘要的 Slack 頻道 ID(`C...`)。

在測試自動化程序之前,請先將 Slack 應用程式邀請至目標頻道。

## 此手冊中使用的變數

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

以下數值會在後續步驟中輸入到 Agent Canvas UI 中。請先在此處設定好,以便之後複製使用:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

請為 `GITHUB_REPO_FILTER` 使用明確的 `owner/repo` 值。過於寬泛的組織萬用字元可能會為本機模型帶來過多的 MCP 內容脈絡。

## 1. 啟動 Lemonade Server

從 Lemonade CLI 啟動模型:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade 會在以下位置公開與 OpenAI 相容的 API:

```text
http://127.0.0.1:13305/api/v1
```

選用:如果 Agent Canvas 或自動化執行器不在同一部機器上,請透過安全通道發佈 Lemonade 端點,並使用該 HTTPS URL 作為 LLM base URL:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. 驗證本機模型

確認 Lemonade 能夠提供所選模型的服務:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

接著傳送一個小型聊天請求:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

如果傳回一個 `choices` 陣列,表示 Lemonade 已準備好供 Agent Canvas 使用。
## 3. 啟動 Agent Canvas

安裝已發布的 Agent Canvas 套件並啟動完整堆疊：

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

若全域 npm install 因權限錯誤而失敗，請參閱下方的 npm
權限疑難排解項目。

依預設,Agent Canvas 會在 `http://localhost:8000` 啟動。請在
瀏覽器中開啟該網址。首頁畫面應會顯示預設的本機後端為健康狀態。

`agent-canvas` 指令會一併啟動 agent 伺服器、自動化後端,以及
網頁前端。您只需要這一個指令即可在本機執行 OpenHands。本操作手冊其餘部分皆透過瀏覽器中的 Agent
Canvas UI 進行設定。

## 4. 在 UI 中設定本機 LLM

首次啟動時,Agent Canvas 會開啟導入流程。在該流程中:

1. 保持代理選為 **OpenHands**,然後點選 **Next**。
2. 在 **Set up your LLM** 頁面,選擇 **Advanced**。
3. 保持 **Authentication** 設為 **API key**。
4. 將 **Custom Model** 設為 `OPENHANDS_LLM_MODEL` 的值,
   `openai/Qwen3.6-35B-A3B-GGUF`。
5. 將 **Base URL** 設為 `http://127.0.0.1:13305/api/v1`。
6. 在 **API Key** 欄位,輸入任意非空白的預留值,例如 `lemonade-local`。
   Lemonade 不需要真正的金鑰,但 OpenHands 用戶端需要傳送一個值。

連線欄位應該如下所示。API 金鑰欄位會由 UI 遮蔽顯示。

![Agent Canvas 首次使用的 LLM Advanced 設定,包含 Lemonade 模型與本機 base URL](assets/01-llm-advanced-settings.png)

接著選擇 **All**,並設定額外的本機模型欄位:

1. 捲動至 **Custom Tokenizer**,並設為 `Qwen/Qwen3.6-35B-A3B`。
2. 捲動至 **LiteLLM Extra Body**,並設為
   `{"enable_thinking": true}`。
3. 點選 **Next**。

![Agent Canvas 首次使用的 LLM All 分頁,包含 Qwen 自訂 tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas 首次使用的 LLM All 分頁,已設定 LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM 設定應顯示如下:

| 欄位 | 值 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` 前綴會告知 LiteLLM 對 Lemonade 端點使用 OpenAI 相容的
請求格式。自訂 tokenizer 是該 GGUF 模型原始的 Hugging
Face tokenizer;它能讓 OpenHands 計算與本機模型伺服器所見相同的
聊天範本 token 數。目前首次使用的 LLM 表單不會顯示 condenser 設定。若您的 Agent Canvas 版本之後在 **Settings > LLM** 下
提供 condenser 設定,請使用 `llm_summarizing`,並
將最大 token 數設為低於 Lemonade 情境視窗的值,例如 `56000`。

## 5. 安裝 GitHub 與 Slack MCP 伺服器

在 Agent Canvas UI 中,開啟 **Customize**(或 **Settings > MCP**)以新增
為代理提供 GitHub 與 Slack 工具的 MCP 伺服器。權杖值僅會
傳送至您的本機 Agent Server,並以加密設定的形式保存。

### GitHub MCP 伺服器

新增一個具有下列設定的 MCP 伺服器:

| 欄位 | 值 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = 您的 GitHub 權杖 |

請使用對想要摘要的儲存庫具有讀取權限的 GitHub 權杖。

### Slack MCP 伺服器

新增第二個具有下列設定的 MCP 伺服器:

| 欄位 | 值 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = 您的摘要頻道 ID |

請將 `SLACK_CHANNEL_IDS` 設為摘要頻道 ID(與
`SLACK_DIGEST_CHANNEL` 相同的值),讓代理不需要翻閱每個 Slack
頻道。

新增兩個伺服器後,請使用各伺服器上的 **Test** 按鈕確認其
可以連線並列出工具。GitHub 伺服器應列出 GitHub 工具,而
Slack 伺服器應列出 Slack 工具。

![已安裝 GitHub 與 Slack 伺服器的 Agent Canvas MCP 頁面](assets/04-mcp-servers-installed.png)

## 6. 建立摘要自動化

在 Agent Canvas UI 中,開啟 **Automations** 頁面並建立新的
自動化:

1. 選擇 **Create automation**,並選取 **Prompt preset** 類型。
2. 將 **Name** 設為 `GitHub Development Digest to Slack`。
3. 將 **Prompt** 設為以下文字,並將儲存庫與
   頻道預留值替換為您自己的值:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. 將 **Trigger** 設為 **Cron**,排程為 `0 9 * * 1-5`(週間
   上午 9 點),並將 **Timezone** 設為您所在的時區,例如
   `America/New_York`。
5. 將 **Timeout** 設為 `900` 秒。
6. 儲存此自動化。

自動化詳細頁面會顯示新建立的自動化,包含其 cron 觸發條件與
產生的 prompt-preset 進入點。

![建立後的 Agent Canvas 自動化詳細頁面](assets/05-automation-created.png)
## 7. 測試自動化流程

在 Agent Canvas UI 的自動化詳細頁面：

1. 點擊 **Run now**（或 **Dispatch**）以立即執行一次自動化。
2. 觀察同一頁面上的執行清單。最新的執行應轉為
   `COMPLETED`。
3. 開啟你的目標 Slack 頻道。應該會包含產生的摘要。

你不需要等待 cron 排程觸發——**Run now** 會依需求觸發一次執行，讓你可以在依賴排程之前先確認提示詞、MCP 連線以及 Slack 發文都正常運作。

![Agent Canvas 自動化執行成功完成](assets/06-automation-run-completed.png)

![Slack 頻道顯示產生的 OpenHands 摘要](assets/07-slackbot-message.png)

## 疑難排解

- **Lemonade 已停止運作：** 在步驟 1 中使用
  `lemonade run "${LEMONADE_MODEL}"` 指令重新啟動，然後重新執行健康
  檢查。
- **`npm install -g` 因權限錯誤而失敗：** 在 Linux 或 WSL 上，
  設定一個使用者擁有的全域 npm 目錄，將其加入你的 shell 啟動
  檔案，然後再次安裝 Agent Canvas：

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  如果你使用 `zsh`，請將相同的 `export PATH=...` 這一行加入
  `~/.zshrc`，而非 `~/.bashrc`。
- **設定 `custom_tokenizer` 後，Agent Canvas 拒絕 LLM 設定：**
  在 Agent Server 的 Python 環境中安裝 `transformers`，如有需要重新啟動 Agent
  Canvas，然後重試儲存 LLM 設定。設定 `custom_tokenizer` 時，OpenHands
  需要 Transformers 才能載入分詞器聊天範本。
- **Agent Canvas 無法連上 Lemonade：** 執行
  `curl -fsS "${LEMONADE_BASE_URL}/health"` 進行驗證，並確認在
  首次使用的 LLM 表單或 **Settings > LLM** 中輸入的基礎 URL 是否與
  正在執行的本機端點或 HTTPS 通道相符。
- **LLM 設定未儲存：** 確認你在輸入完數值後有點擊 **Next**。重新開啟
  **Settings > LLM** 以確認數值已保存。
- **GitHub MCP 無法看到私有儲存庫：** 確認 GitHub 權杖對目標儲存庫具有
  讀取權限，並確認 **Customize** 中的 MCP **Test** 按鈕
  有列出 GitHub 工具。
- **Slack 可以讀取頻道但無法發文：** 將 Slack 應用程式邀請至
  目標頻道，並確認該機器人擁有 `chat:write` 權限。
- **自動化列出過多 Slack 頻道：** 使用 Slack 頻道 ID，並在 **Customize** 中的
  Slack MCP 伺服器上設定 `SLACK_CHANNEL_IDS`。
- **自動化執行失敗或超出上下文限制：** 確認 Lemonade 啟動時已設定
  `ctx_size=65536`，確認 OpenHands LLM 已設定 `custom_tokenizer`，
  並使用明確指定的儲存庫，將 GitHub 結果集上限設為 3 到 5
  項。如果你的 Agent Canvas 版本有提供壓縮器（condenser）設定，請將壓縮器
  的最大權杖數設定為低於 Lemonade 的上下文視窗大小。

## 後續步驟

- 新增每週僅限發行版本的摘要。
- 新增由 GitHub 事件觸發的自動化，以取得更快速的 PR 或推送提醒。
- 將相同的摘要導向 Notion、Linear 或其他以 MCP 為基礎的工具。

## 資源

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server 文件](https://lemonade-server.ai/docs)
- [OpenHands extensions 儲存庫](https://github.com/OpenHands/extensions)
- [Model Context Protocol 伺服器](https://github.com/modelcontextprotocol/servers)
- [Slack MCP 套件](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)