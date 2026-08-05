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

[OpenHands](https://github.com/All-Hands-AI/OpenHands)는 코드를 작성하고, 명령을 실행하고, 웹을 탐색하고, 실제 워크스페이스에서 파일을 편집할 수 있는 AI 소프트웨어 에이전트입니다. 채팅 창에서 제안을 복사해오는 대신, 프로젝트 폴더를 에이전트에게 지정하고 기능 구현, 버그 수정, 테스트 작성, 코드베이스 설명 등의 작업을 맡길 수 있습니다.

[Agent Canvas](https://github.com/OpenHands/agent-canvas)는 OpenHands를 실행하기 위해 권장되는 브라우저 UI입니다. `agent-canvas` 명령 하나로 에이전트 서버, 자동화 백엔드, 웹 프런트엔드를 함께 시작하므로 브라우저에서 에이전트와 대화를 진행할 수 있습니다.

모든 것을 AMD 시스템에 유지하기 위해, 에이전트는 Lemonade Server가 제공하는 로컬 모델과 통신합니다. Lemonade는 이 모델을 OpenAI 호환 API를 통해 노출하므로, Agent Canvas는 다른 OpenAI 스타일 엔드포인트와 마찬가지로 이를 구성할 수 있으며, 모델, 코드, 대화 컨텍스트는 모두 사용자의 컴퓨터에 그대로 남아 있습니다.

이 플레이북에서는 로컬 모델을 시작하고, Agent Canvas를 실행하고, 해당 모델을 가리키도록 설정한 다음, 실제 프로젝트 폴더에 대해 첫 번째 코딩 작업을 실행합니다.

## 배울 내용

- Lemonade Server를 시작하고 로컬 모델이 채팅 요청에 응답하는지 확인하는 방법
- npm 패키지에서 Agent Canvas를 설치하고 실행하는 방법
- 로컬 Lemonade 모델을 LLM으로 사용하도록 Agent Canvas를 구성하는 방법
- OpenHands 대화를 시작하고 에이전트가 워크스페이스에서 파일을 편집하고 명령을 실행하는 모습을 지켜보는 방법
- 에이전트가 변경한 내용을 검토하고 후속 메시지로 방향을 지정하는 방법

## 핵심 개념

| 개념 | 설명 | 이 플레이북에서의 역할 |
| --- | --- | --- |
| Lemonade Server | AMD 하드웨어를 위해 제작된 로컬 LLM 서빙 플랫폼으로, OpenAI 호환 API를 노출합니다. 데이터가 컴퓨터를 벗어나지 않습니다. | 에이전트에 동력을 공급하는 모델을 실행합니다. |
| OpenHands | 워크스페이스 내에서 파일을 읽고 편집하며, 셸 명령을 실행하고, 웹을 탐색하는 AI 소프트웨어 에이전트입니다. | 채팅에서 조작하는 에이전트입니다. |
| Agent Canvas | OpenHands 대화를 실행하고 도구 호출 및 파일 변경 사항을 표시하는 브라우저 UI와 백엔드입니다. | 스택을 실행하고 대화를 호스팅합니다. |
| Workspace | 에이전트가 읽고 수정할 수 있도록 허용된 프로젝트 폴더입니다. | 에이전트의 편집 및 명령의 대상입니다. |

<!-- @device:stx,krk -->
> [!NOTE]
> 코딩 에이전트 워크플로는 더 큰 모델과 컨텍스트 창을 사용할 때 이점이 있습니다. 최소 32GB의 시스템 메모리를 사용하고, 더 큰 GGUF 모델의 경우 64GB 이상을 권장합니다.
<!-- @device:end -->

## 사전 요구 사항

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

다음이 필요합니다:

- 아래 모델을 서빙할 수 있도록 설치된 Lemonade Server.
- Node.js 22.12 이상 및 `npm`(`agent-canvas` CLI에서 사용).
- Agent Canvas가 에이전트 서버 환경을 관리하는 데 사용하는 Python 패키지 관리자인 `uv`. 시스템에 아직 설치되어 있지 않다면, Agent Canvas를 실행하기 전에 [uv 설치 가이드](https://docs.astral.sh/uv/getting-started/installation/)에서 설치하세요.
- 작업할 프로젝트 폴더. 에이전트가 작업하기를 원하는 로컬 git 리포지토리 또는 코드 디렉터리라면 무엇이든 가능합니다.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Lemonade Server 시작

Lemonade CLI에서 모델을 시작합니다:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade는 다음 위치에 OpenAI 호환 API를 노출합니다:

```text
http://127.0.0.1:13305/api/v1
```



## 2. 로컬 모델 확인

Lemonade가 선택한 모델을 서빙할 수 있는지 확인합니다:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

그런 다음 작은 채팅 요청을 전송합니다:

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

`choices` 배열이 반환되면 Lemonade가 Agent Canvas를 사용할 준비가 된 것입니다.

## 3. Agent Canvas 설치 및 실행

게시된 Agent Canvas 패키지를 전역으로 설치합니다:

```bash
npm install -g @openhands/agent-canvas
```

그런 다음 터미널에서 전체 스택을 시작합니다:

```bash
agent-canvas
```

기본적으로 Agent Canvas는 `http://localhost:8000`에서 시작됩니다. 브라우저에서 해당 URL을 여세요. 포트 8000이 이미 사용 중이면 Agent Canvas를 실행할 때 `--port`(또는 `-p`)를 전달하세요:

```bash
agent-canvas --port 3000
```

Windows의 PowerShell에서도 동일한 명령이 작동합니다. 이 경우 대신 `http://localhost:3000`을 여세요. 기본 로컬 백엔드는 홈 화면에서 정상(healthy)으로 표시되어야 합니다.

`agent-canvas` 명령은 에이전트 서버, 자동화 백엔드, 웹 프런트엔드를 함께 시작합니다. OpenHands를 로컬에서 실행하는 데 이 명령 하나만 있으면 됩니다.

## 4. 로컬 LLM 구성

처음 실행하면 Agent Canvas가 온보딩 흐름을 엽니다. 이 흐름에서:

1. 에이전트로 **OpenHands**가 선택된 상태를 유지하고 **Next**를 클릭합니다.
2. **Set up your LLM**에서 **Advanced**를 선택합니다.
3. **Authentication**을 **API key**로 유지합니다.
4. **Custom Model**을 `openai/Qwen3.6-35B-A3B-GGUF`로 설정합니다.
5. **Base URL**을 `http://127.0.0.1:13305/api/v1`로 설정합니다.
6. **API Key**에는 `lemonade-local`과 같이 비어 있지 않은 임의의 플레이스홀더 값을 입력합니다. Lemonade는 실제 키를 요구하지 않지만, OpenHands 클라이언트는 전송할 값이 필요합니다.
7. **Next**를 클릭합니다.

완료된 Advanced 설정은 다음과 같이 보여야 합니다. API 키 필드는 UI에서 마스킹 처리됩니다.

![Lemonade 모델과 로컬 base URL이 설정된 Agent Canvas 최초 사용 LLM Advanced 설정](assets/01-llm-advanced-settings.png)

Agent Canvas는 이 값들을 LLM 프로필로 저장합니다. 사용 중인 버전에서 이 프로필의 이름을 지정하도록 요청하면, `lemonade-local`과 같이 공백이 없는 이름을 사용하세요. 나중에 모델을 변경하려면 **Settings > LLM**을 열고 동일한 Advanced 필드를 업데이트하세요. 채팅 입력창에서 `/model` 명령으로 저장된 프로필을 전환할 수 있습니다.

## 5. 워크스페이스 열기

에이전트는 선택한 워크스페이스 내부의 파일만 읽고 수정할 수 있습니다. 작업을 시작하기 전에 Agent Canvas가 프로젝트 폴더를 가리키도록 지정하세요:

1. 홈 화면에서 **Open Workspace**를 선택합니다.
2. 프로젝트가 포함된 폴더를 선택합니다(예: 에이전트가 작업하기를 원하는 git 리포지토리).
3. 해당 워크스페이스에서 새 대화를 시작합니다.

에이전트가 수행하는 모든 작업—파일 읽기, 명령 실행, 코드 편집—은 해당 워크스페이스로 범위가 제한됩니다.

![온보딩 이후의 Agent Canvas 홈](assets/02-agent-canvas-home.png)
## 6. 첫 번째 코딩 작업 실행하기

워크스페이스를 열고 로컬 LLM을 선택한 상태에서, 채팅에 구체적인 작업을 입력합니다. 좋은 첫 작업은 작고 검증 가능한 것이어야 합니다. 예를 들면:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

대화 타임라인을 지켜보세요. OpenHands는 다음을 수행합니다:

- 워크스페이스를 읽어 구조를 파악합니다.
- 요청된 함수와 테스트 블록을 포함한 `hello.py`를 생성합니다.
- 필요한 경우 `python3 hello.py`를 실행하여 출력을 확인합니다.
- 자신이 수행한 작업과 명령 출력을 채팅에 보고합니다.

워크스페이스에 새 파일이 나타나고, 에이전트의 마지막 메시지에 자신이 수행한 변경 사항이 설명되어 있는 것을 확인할 수 있습니다. 이것이 바로 결정적인 순간입니다: 에이전트가 여러분의 프로젝트 폴더에서 실제 코드를 작성하고 실행한 것입니다.

## 7. 에이전트 검토 및 방향 조정

에이전트가 한 단계를 완료한 후, 다음 단계를 승인하기 전에 작업 내용을 검토하세요:

- **파일 변경 사항**: 워크스페이스 파일 브라우저 또는 에이전트의 diff 보기를 사용하여
  정확히 무엇이 추가, 변경, 삭제되었는지 확인합니다.
- **명령 출력**: 에이전트가 실행한 명령을 펼쳐서 stdout, stderr,
  종료 코드를 확인합니다.
- **후속 조치**: 결과가 원하는 것과 다르다면, 같은
  대화에서 수정 사항을 답장으로 남깁니다. 에이전트는 이전 컨텍스트를 유지하며
  동일한 파일에 대해 반복 작업합니다.

예를 들어, 테스트에서 예상한 인사말이 출력되지 않았다면 다음과 같이 답장하세요:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

에이전트는 파일을 다시 읽고, 명령을 실행하고, 문제를 진단한 후 다시
파일을 수정합니다—모두 같은 대화 안에서 이루어집니다.

## 문제 해결

- **`agent-canvas`가 PATH에 없는 경우:**
  `npm install -g @openhands/agent-canvas`로 재설치하고 npm 전역 바이너리
  디렉터리가 PATH에 포함되어 있는지 확인하세요. Windows에서는 `npm config get prefix`를
  실행합니다. 반환된 디렉터리(주로 `%APPDATA%\npm` 또는 `%USERPROFILE%\.npm-global`)가
  새 터미널에서 `agent-canvas`를 실행할 수 있으려면 사용자 PATH에 포함되어 있어야 합니다.
- **`npm install -g`가 권한 오류로 실패하는 경우:** 사용자 소유의
  전역 npm 디렉터리를 구성한 다음, 터미널을 다시 열고 Agent Canvas를 다시 설치하세요.

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

  Windows PATH 변경 사항을 영구적으로 적용하려면 **설정 > 시스템 > 정보 > 고급 시스템
  설정 > 환경 변수**에서 사용자 PATH에 `%USERPROFILE%\.npm-global`을 추가하고,
  새 터미널을 여세요.
  <!-- @os:end -->
- **UI는 로드되지만 백엔드가 비정상(unhealthy) 상태로 표시되는 경우:** 에이전트 서버가
  시작을 완료할 때까지 몇 초 기다린 후 새로고침하세요. 계속 비정상 상태라면 `agent-canvas`를
  재시작하고 터미널 출력에서 오류를 확인하세요.
- **Lemonade 채팅 요청이 연결 오류로 실패하는 경우:**
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"`가 성공하는지, 그리고
  Lemonade가 `lemonade status`로 확인했을 때 여전히 모델을 서비스하고 있는지 확인하세요.
- **에이전트가 컨텍스트 길이 또는 토큰 제한 관련 오류를 발생시키는 경우:** 더 큰
  `ctx_size`(예: `ctx_size=65536`)로 Lemonade를 재시작하고, 에이전트가 지나치게 큰
  기록을 유지하지 않도록 새 대화를 시작하세요.
- **에이전트가 품질이 낮거나 불완전한 편집을 생성하는 경우:** Lemonade에서 더 큰
  모델로 전환하거나, 에이전트에게 더 작고 구체적인 작업을 주고 다음 변경을 요청하기 전에
  완료하도록 하세요.
- **`uv`가 없는 경우:**
  [uv 설치 가이드](https://docs.astral.sh/uv/getting-started/installation/)에서 설치하세요.
  Agent Canvas는 에이전트 서버의 Python 환경을 관리하기 위해 `uv`를 사용합니다.

## 다음 단계

- 동일한 워크스페이스에서 단위 테스트 파일 추가나 알려진 버그 수정과 같은 더 큰
  작업을 시도해 보고, 변경 사항을 유지하기 전에 에이전트의 diff를 검토하세요.
- **Customize**에서 GitHub나 Slack과 같은 MCP 서버를 연결하여
  에이전트가 작업하는 동안 이슈를 읽거나 업데이트를 게시할 수 있도록 하세요.
- 여러 개의 LLM 프로필(빠른 소형 모델과 더 강력한 대형 모델)을 저장해 두고
  대화 중간에 `/model`을 사용해 전환해 보세요.
- 반복적인 개발 루프를 예약되거나 이벤트로 트리거되는 에이전트 실행으로 전환하려면
  [OpenHands 자동화](https://docs.openhands.dev/openhands/usage/automations/overview)로 넘어가세요.

## 참고 자료

- [OpenHands 문서](https://docs.openhands.dev/)
- [Agent Canvas 개요](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 설정](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 프로필 및 모델 구성](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 문서](https://lemonade-server.ai/docs)