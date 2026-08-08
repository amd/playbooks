<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위해 예상되는 플랫폼 구성을 설명합니다.

## 필수 앱/프레임워크

### Windows/Linux

- **Lemonade Server**는 [Lemonade 설치 가이드](https://lemonade-server.ai/docs/guide/install/)에 따라 설치해야 합니다.
- `agent-canvas` CLI 및 `npx`로 실행되는 MCP 서버에서 사용하는 **Node.js 22.12 이상**과 `npm`.
- Agent Canvas가 에이전트 서버 환경을 관리하는 데 사용하는 Python 패키지 관리자인 **uv**. [uv 설치 가이드](https://docs.astral.sh/uv/getting-started/installation/)에서 설치하세요.

## 필수 모델

### Windows/Linux

플레이북을 시작하기 전에 다음 모델이 Lemonade Server에서 사용 가능해야 합니다.

| 모델 유형 | 모델 ID | 참고 사항 |
| --- | --- | --- |
| GGUF 채팅 모델 | `Qwen3.6-35B-A3B-GGUF` | `http://127.0.0.1:13305/api/v1`에서 Lemonade Server가 제공합니다. 메모리가 32GB 미만인 기기에서는 더 작은 GGUF 모델을 사용하세요. |

다음 명령으로 모델을 시작하세요:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## 외부 자격 증명

이 플레이북에는 다음이 필요합니다:

- 요약 대상 리포지토리에 대한 읽기 권한이 있는 GitHub 토큰.
- `chat:write` 및 채널 읽기 권한이 있는 Slack 봇 토큰.
- Slack 팀 ID 및 대상 Slack 채널 ID.