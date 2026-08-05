<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 개요

개발자는 반복되는 작은 작업 루프에 많은 시간을 소비합니다. 레이블이 지정된
풀 리퀘스트 검토, GitHub 댓글 응답, 새 이슈 분류, Slack 스레드를 스탠드업
노트나 인시던트 후속 조치로 전환하는 작업, 릴리스나 리서치 신호를 추적하는
작업 등이 그렇습니다. 각 루프는 익숙하지만 여전히 판단이 필요합니다. 올바른
컨텍스트를 수집하고, 중요한 것을 결정하고, 팀이 이미 사용 중인 곳에 명확한
업데이트를 게시해야 합니다.

[OpenHands 자동화](https://docs.openhands.dev/openhands/usage/automations/overview)는
이러한 루프를 예약되거나 이벤트로 트리거되는 에이전트 대화로 전환합니다. 이는
AI 소프트웨어 에이전트가 컨텍스트를 읽고, 도구를 호출하고, 업데이트를 생성할
수 있는 실행입니다. OpenHands 확장 카탈로그의 공유 자동화 템플릿은 GitHub
풀 리퀘스트 검토, 저장소 모니터링, Linear 이슈 분류, 인시던트 회고, Slack
스탠드업 다이제스트, 리서치 브리핑에 대해 이 패턴을 따릅니다. 즉, 자동화가
깨어나서 GitHub나 Slack 같은 구성된 통합을 사용해 컨텍스트를 가져오고, 대규모
언어 모델(LLM)로 해당 컨텍스트에 대해 추론한 다음, 결과를 다시 작성합니다.

[Agent Canvas](https://github.com/OpenHands/agent-canvas)는 이러한 자동화를
빌드하고 테스트하기 위한 로컬 제어 플레인입니다. 이 플레이북에서는 에이전트
대화를 실행하는 백엔드 프로세스인 OpenHands Agent Server를 실행하고,
에이전트를 GitHub 및 Slack 같은 외부 서비스에 연결합니다.

워크플로를 AMD 시스템에 유지하기 위해 에이전트는 Lemonade Server에서
제공되는 로컬 모델과 통신합니다. Lemonade는 OpenAI 호환 API를 통해 해당
모델을 노출하므로, Agent Canvas는 모델, 프롬프트, 워크플로 컨텍스트를 로컬에
유지하면서 이를 원격 OpenAI 스타일 엔드포인트처럼 구성할 수 있습니다.

이 플레이북에서는 예약된 GitHub-to-Slack 개발 다이제스트라는 구체적인
자동화 하나를 빌드합니다. 이는 GitHub를 사용해 최근 저장소 활동을 검사하고,
Slack을 사용해 다이제스트를 게시하며, Agent Canvas API 호출을 사용해
자동화를 구성하고 테스트하고, Lemonade를 사용해 LLM을 로컬에서 실행합니다.

![GitHub MCP, OpenHands 자동화, Lemonade Server, Slack MCP를 보여주는 아키텍처 다이어그램](assets/00-architecture-overview.png)

## 배울 내용

- Lemonade Server를 시작하고 로컬 모델이 채팅 요청에 응답하는지 확인하는 방법
- Agent Canvas를 실행하고 그 Agent Server를 로컬 LLM으로 지정하는 방법
- Agent Server API를 통해 GitHub 및 Slack Model Context Protocol(MCP)
  서버를 설치하는 방법
- 개발 다이제스트를 Slack에 게시하는 예약된 OpenHands 자동화를 생성하고
  실행하는 방법
- 가장 흔한 로컬 모델 및 자동화 오류를 문제 해결하는 방법

## 핵심 개념

| 개념 | 설명 | 이 플레이북에서의 역할 |
| --- | --- | --- |
| Lemonade Server | AMD 하드웨어를 위해 구축된 로컬 LLM 서빙 플랫폼으로 OpenAI 호환 API를 노출합니다. 데이터는 절대 사용자 머신을 벗어나지 않습니다. | 에이전트를 구동하는 모델을 실행합니다. |
| OpenHands Agent Server | OpenHands 에이전트 대화를 실행하는 백엔드 프로세스입니다. | 에이전트, 그 LLM 프로필, MCP 서버를 호스팅합니다. |
| Agent Canvas | Agent Server와 에이전트 실행을 검사하기 위한 UI를 실행하는 OpenHands용 로컬 제어 플레인입니다. | 백엔드를 실행하고 호출할 API를 제공합니다. |
| MCP 서버 | GitHub나 Slack 같은 외부 서비스를 위한 도구를 에이전트에 제공하는 Model Context Protocol 서버입니다. | 에이전트가 GitHub를 읽고 Slack에 쓸 수 있게 합니다. |
| OpenHands 자동화 | 컨텍스트를 가져오고, 그에 대해 추론하고, 결과를 어딘가에 작성하는 예약되거나 이벤트로 트리거되는 에이전트 대화입니다. | 여기서 빌드하는 GitHub-to-Slack 다이제스트입니다. |

<!-- @device:stx,krk -->
> [!NOTE]
> 코딩 에이전트 워크플로는 더 큰 모델과 컨텍스트 창의 이점을 누립니다. 최소
> 32GB의 시스템 메모리를 사용하고, 더 큰 GGUF 모델에는 64GB 이상을
> 권장합니다.
<!-- @device:end -->

## 사전 요구 사항

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

다음이 필요합니다:

- 표준 [Lemonade 설치 가이드](https://lemonade-server.ai/docs/guide/install/)를
  따라 설치된 Lemonade Server.
- 게시된 Agent Canvas CLI를 설치하고 `npx`로 MCP 서버를 실행하는 데 사용되는
  Node.js 22.12 이상 및 `npm`.
- 스키마 기반 에이전트 설정, `LLMSummarizingCondenserSettings.max_tokens`,
  LLM `custom_tokenizer` 지원이 포함된 최신 게시 버전의
  `@openhands/agent-canvas` 패키지.
- Agent Server 환경에서 사용 가능한 Python `transformers` 패키지. 이는
  `custom_tokenizer`가 설정된 경우 채팅 템플릿 토큰 계산에 필요합니다.
- 요약하려는 저장소에 대한 읽기 액세스 권한이 있는 GitHub 토큰.
- `chat:write` 및 채널 읽기 액세스 권한이 있는 Slack 봇 토큰(`xoxb-...`).
- Slack 팀 ID(`T...`).
- 다이제스트를 게시할 Slack 채널 ID(`C...`).

자동화를 테스트하기 전에 Slack 앱을 대상 채널에 초대하세요.

## 이 플레이북에서 사용되는 변수

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

다음 값들은 이후 단계에서 Agent Canvas UI에 입력됩니다. 나중에 복사해
넣을 수 있도록 여기에 설정해 두세요:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

`GITHUB_REPO_FILTER`에는 명시적인 `owner/repo` 값을 사용하세요. 광범위한
조직 와일드카드는 로컬 모델에게 너무 많은 MCP 컨텍스트를 반환할 수
있습니다.

## 1. Lemonade Server 시작

Lemonade CLI에서 모델을 시작합니다:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade는 다음 위치에서 OpenAI 호환 API를 노출합니다:

```text
http://127.0.0.1:13305/api/v1
```

선택 사항: Agent Canvas나 자동화 실행기가 동일한 머신에 있지 않은 경우,
안전한 터널을 통해 Lemonade 엔드포인트를 게시하고 HTTPS URL을 LLM 기본
URL로 사용하세요:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. 로컬 모델 확인

Lemonade가 선택한 모델을 서빙할 수 있는지 확인합니다:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

그런 다음 작은 채팅 요청을 보냅니다:

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

이 요청이 `choices` 배열을 반환하면 Lemonade는 Agent Canvas를 위한 준비가
된 것입니다.
## 3. Agent Canvas 시작

게시된 Agent Canvas 패키지를 설치하고 전체 스택을 시작합니다.

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

전역 npm install이 권한 오류로 실패하는 경우 아래의 npm
권한 문제 해결 항목을 참고하세요.

기본적으로 Agent Canvas는 `http://localhost:8000`에서 시작됩니다. 브라우저에서
해당 URL을 열어 보세요. 기본 로컬 백엔드는 홈 화면에서 정상(healthy) 상태로
표시되어야 합니다.

`agent-canvas` 명령은 에이전트 서버, 자동화 백엔드, 웹 프런트엔드를 함께
시작합니다. OpenHands를 로컬에서 실행하려면 이 명령 하나만 있으면 됩니다.
이 플레이북의 나머지 부분에서는 브라우저의 Agent Canvas UI를 통해 모든 것을
구성합니다.

## 4. UI에서 로컬 LLM 구성

처음 실행하면 Agent Canvas는 온보딩 흐름을 엽니다. 해당 흐름에서:

1. 에이전트로 **OpenHands**가 선택된 상태를 유지하고 **Next**를 클릭합니다.
2. **Set up your LLM**에서 **Advanced**를 선택합니다.
3. **Authentication**을 **API key**로 유지합니다.
4. **Custom Model**을 `OPENHANDS_LLM_MODEL` 값인
   `openai/Qwen3.6-35B-A3B-GGUF`로 설정합니다.
5. **Base URL**을 `http://127.0.0.1:13305/api/v1`로 설정합니다.
6. **API Key**에는 `lemonade-local`과 같이 비어 있지 않은 임의의
   자리 표시자 값을 입력합니다. Lemonade는 실제 키를 요구하지 않지만
   OpenHands 클라이언트는 값을 전송해야 합니다.

연결 필드는 다음과 같아야 합니다. API 키 필드는 UI에서 마스킹되어 표시됩니다.

![Lemonade 모델과 로컬 기본 URL이 설정된 Agent Canvas 최초 사용 시 LLM Advanced 설정](assets/01-llm-advanced-settings.png)

그런 다음 **All**을 선택하고 추가 로컬 모델 필드를 설정합니다.

1. **Custom Tokenizer**로 스크롤하여 `Qwen/Qwen3.6-35B-A3B`로 설정합니다.
2. **LiteLLM Extra Body**로 스크롤하여
   `{"enable_thinking": true}`로 설정합니다.
3. **Next**를 클릭합니다.

![Qwen 커스텀 토크나이저가 설정된 Agent Canvas 최초 사용 시 LLM All 탭](assets/02-llm-all-tokenizer-settings.png)

![LiteLLM 추가 본문(body)이 구성된 Agent Canvas 최초 사용 시 LLM All 탭](assets/03-llm-all-extra-body-settings.png)

LLM 설정은 다음과 같이 표시되어야 합니다.

| 필드 | 값 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` 접두사는 LiteLLM에게 Lemonade 엔드포인트에 대해 OpenAI 호환
요청 형식을 사용하도록 지시합니다. 커스텀 토크나이저는 GGUF 모델의 원본
Hugging Face 토크나이저로, OpenHands가 로컬 모델 서버가 보는 것과 동일한
채팅 템플릿 토큰을 계산할 수 있게 해줍니다. 현재 최초 사용 시의 LLM 양식에는
컨덴서(condenser) 설정이 표시되지 않습니다. 사용 중인 Agent Canvas 빌드에서
나중에 **Settings > LLM** 아래에 컨덴서 설정이 노출되는 경우, `llm_summarizing`을
사용하고 최대 토큰을 Lemonade 컨텍스트 윈도우보다 낮은 값, 예를 들어
`56000`으로 설정하세요.

## 5. GitHub 및 Slack MCP 서버 설치

Agent Canvas UI에서 **Customize**(또는 **Settings > MCP**)를 열어 에이전트에
GitHub 및 Slack용 도구를 제공하는 MCP 서버를 추가합니다. 토큰 값은 로컬
Agent Server로만 전송되며 암호화된 설정으로 저장됩니다.

### GitHub MCP 서버

다음 설정으로 새 MCP 서버를 추가합니다.

| 필드 | 값 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = 사용자의 GitHub 토큰 |

요약하려는 저장소에 대한 읽기 권한이 있는 GitHub 토큰을 사용하세요.

### Slack MCP 서버

다음 설정으로 두 번째 MCP 서버를 추가합니다.

| 필드 | 값 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = 사용자의 다이제스트 채널 ID |

`SLACK_CHANNEL_IDS`를 다이제스트 채널 ID(`SLACK_DIGEST_CHANNEL`과 동일한 값)로
설정하여 에이전트가 모든 Slack 채널을 일일이 확인할 필요가 없도록 하세요.

두 서버를 모두 추가한 후, 각 서버에서 **Test** 버튼을 사용해 연결되고 도구를
알리는지 확인하세요. GitHub 서버는 GitHub 도구 목록을 표시해야 하고, Slack
서버는 Slack 도구 목록을 표시해야 합니다.

![GitHub 및 Slack 서버가 설치된 Agent Canvas MCP 페이지](assets/04-mcp-servers-installed.png)

## 6. 다이제스트 자동화 생성

Agent Canvas UI에서 **Automations** 페이지를 열고 새 자동화를 생성합니다.

1. **Create automation**을 선택하고 **Prompt preset** 유형을 선택합니다.
2. **Name**을 `GitHub Development Digest to Slack`으로 설정합니다.
3. **Prompt**를 다음 텍스트로 설정하되, 저장소 및 채널 자리 표시자를
   사용자의 값으로 대체합니다.

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

4. **Trigger**를 **Cron**으로 설정하고 일정을 `0 9 * * 1-5`(평일 오전 9시)로
   설정한 다음, **Timezone**을 사용자의 시간대(예: `America/New_York`)로
   설정합니다.
5. **Timeout**을 `900`초로 설정합니다.
6. 자동화를 저장합니다.

자동화 상세 페이지에는 새로 생성된 자동화가 cron 트리거 및 생성된
prompt-preset 진입점(entrypoint)과 함께 표시됩니다.

![생성 후 Agent Canvas 자동화 상세 화면](assets/05-automation-created.png)
## 7. 자동화 테스트

Agent Canvas UI의 자동화 상세 페이지에서:

1. **Run now**(또는 **Dispatch**)를 클릭하여 자동화를 즉시 한 번 실행합니다.
2. 동일한 페이지의 실행 목록을 지켜보세요. 최신 실행이 `COMPLETED` 상태로 전환되어야 합니다.
3. 대상 Slack 채널을 엽니다. 생성된 다이제스트가 표시되어야 합니다.

cron 일정이 실행될 때까지 기다릴 필요는 없습니다—**Run now**는 온디맨드로 실행을
트리거하므로 일정에 의존하기 전에 프롬프트, MCP 연결, Slack 게시가 모두
제대로 작동하는지 확인할 수 있습니다.

![Agent Canvas 자동화 실행이 성공적으로 완료됨](assets/06-automation-run-completed.png)

![생성된 OpenHands 다이제스트를 보여주는 Slack 채널](assets/07-slackbot-message.png)

## 문제 해결

- **Lemonade가 다운된 경우:** 1단계의 `lemonade run "${LEMONADE_MODEL}"` 명령으로
  재시작한 다음, 상태 확인(health check)을 다시 실행하세요.
- **`npm install -g`가 권한 오류로 실패하는 경우:** Linux 또는 WSL에서는
  사용자 소유의 전역 npm 디렉터리를 구성하고, 셸 시작 파일에 추가한 다음,
  Agent Canvas를 다시 설치하세요:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  `zsh`를 사용하는 경우 `~/.bashrc` 대신 `~/.zshrc`에 동일한
  `export PATH=...` 줄을 추가하세요.
- **`custom_tokenizer`를 설정한 후 Agent Canvas가 LLM 설정을 거부하는 경우:**
  Agent Server Python 환경에 `transformers`를 설치하고, 필요하면 Agent
  Canvas를 재시작한 다음 LLM 설정 저장을 다시 시도하세요. `custom_tokenizer`가
  설정된 경우 OpenHands는 토크나이저 채팅 템플릿을 로드하기 위해
  Transformers가 필요합니다.
- **Agent Canvas가 Lemonade에 연결할 수 없는 경우:**
  `curl -fsS "${LEMONADE_BASE_URL}/health"`를 확인하고, 첫 사용 시 LLM 양식이나
  **Settings > LLM**에 입력한 기본 URL이 실행 중인 로컬 엔드포인트나 HTTPS
  터널과 일치하는지 확인하세요.
- **LLM 설정이 저장되지 않은 경우:** 값을 입력한 후 **Next**를 클릭했는지
  확인하세요. **Settings > LLM**을 다시 열어 값이 유지되었는지 확인하세요.
- **GitHub MCP가 비공개 저장소를 볼 수 없는 경우:** GitHub 토큰이 대상
  저장소에 대한 읽기 액세스 권한을 가지고 있는지, 그리고 **Customize**의 MCP
  **Test** 버튼이 GitHub 도구를 알리는지 확인하세요.
- **Slack이 채널을 읽을 수는 있지만 게시할 수 없는 경우:** Slack 앱을 대상
  채널에 초대하고 봇에 `chat:write` 권한이 있는지 확인하세요.
- **자동화가 너무 많은 Slack 채널을 나열하는 경우:** Slack 채널 ID를 사용하고
  **Customize**의 Slack MCP 서버에 `SLACK_CHANNEL_IDS`를 설정하세요.
- **자동화 실행이 실패하거나 컨텍스트를 초과하는 경우:** Lemonade가
  `ctx_size=65536`으로 시작되었는지, OpenHands LLM에 `custom_tokenizer`가
  설정되었는지 확인하고, 명시적인 저장소를 사용하며 GitHub 결과 집합을
  3~5개 항목으로 제한하세요. Agent Canvas 빌드에 condenser 설정이 노출되어
  있다면 condenser 최대 토큰을 Lemonade 컨텍스트 윈도우보다 낮게 설정하세요.

## 다음 단계

- 주간 릴리스 전용 다이제스트를 추가하세요.
- 더 빠른 PR 또는 push 알림을 위한 GitHub 이벤트 트리거 자동화를 추가하세요.
- 동일한 다이제스트를 Notion, Linear 또는 다른 MCP 기반 도구로 라우팅하세요.

## 리소스

- [AMD AI 플레이북](https://developer.amd.com/playbooks/)
- [Lemonade Server 문서](https://lemonade-server.ai/docs)
- [OpenHands 확장 저장소](https://github.com/OpenHands/extensions)
- [Model Context Protocol 서버](https://github.com/modelcontextprotocol/servers)
- [Slack MCP 패키지](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)