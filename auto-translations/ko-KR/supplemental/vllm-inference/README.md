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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## 개요

vLLM은 대형 언어 모델(LLM)을 위해 설계된 고성능 추론 엔진입니다. 높은 처리량을 위한 연속 배칭(continuous batching)을 통해 최적화된 서빙을 제공하며, 원활한 애플리케이션 통합을 위한 OpenAI 호환 API를 제공합니다. 이 덕분에 vLLM은 속도와 리소스 효율성이 중요한 프로덕션 배포에 매우 적합합니다.

이 플레이북에서는 통합 GPU에서 컨테이너화된 vLLM을 사용하여 LLM을 서빙하고 OpenAI Python API를 통해 모델과 상호작용하는 방법을 배웁니다.

## 배우게 될 내용

- AMD ROCm™ 지원과 함께 vLLM 서버를 설정하고 시작하는 방법
- OpenAI 호환 API 엔드포인트를 통해 모델과 상호작용하는 방법
- `vllm-prompt`를 사용하여 로컬 서버로 프롬프트를 전송하는 방법

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

> **참고**: VS Code가 설치되어 있지 않은 경우, AMD Ryzen™ AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

vLLM은 ROCm 및 해당 종속성이 미리 매칭된 사전 빌드된 컨테이너에서 실행됩니다. 추가 설치가 필요하지 않습니다.

호스트 측에서 별도의 vLLM 설치 단계는 없습니다. 다음 명령으로 vLLM을 시작하세요:

```bash
vllm-launch
```

런처는 컨테이너를 시작하고 통합 GPU를 대상으로 지정하며 로컬 OpenAI 호환 vLLM 서버를 노출합니다. 또는 작업 표시줄의 vLLM 아이콘을 클릭할 수도 있습니다.

## 빠른 시작

### 1. vLLM 서버가 실행 중인지 확인

`vllm-launch`가 모든 것을 초기화하는 데 몇 분 정도 걸릴 수 있습니다. 시작되면 서버는 `http://localhost:8001`에서 사용할 수 있습니다. 서버가 포그라운드에서 실행되므로 실행 터미널을 계속 열어 두고, 나머지 단계를 위해 별도의 터미널을 여세요. 아래 예제에서는 `Qwen/Qwen3-1.7B`를 사용합니다. 런처가 다른 모델로 구성되어 있다면 요청 시 해당 모델 ID로 대체하세요.

### 2. 프롬프트 전송

제공된 `vllm-prompt` 스크립트를 사용하여 로컬 vLLM OpenAI 호환 서버로 요청을 보냅니다:

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API를 사용하여 모델과 채팅하기

vLLM은 OpenAI 호환 API를 노출하므로 `openai` Python 패키지를 사용하여 상호작용할 수 있습니다.

먼저 Python 가상 환경을 생성합니다:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

OpenAI 패키지 설치
```bash
pip install openai
```

OpenAI 서버가 아닌 로컬 vLLM 서버를 가리키는 `OpenAI` 클라이언트를 생성합니다. `api_key`는 클라이언트에서 필수로 요구되지만 vLLM은 이를 검증하지 않으므로 임의의 문자열을 사용해도 됩니다:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

그런 다음 채팅 완료 요청을 보냅니다. 이는 `"user"` 및 `"assistant"`와 같은 역할을 가진 메시지 목록을 사용하는 OpenAI API와 동일한 메시지 형식을 사용합니다. `stream=True`로 설정하면 응답이 한 번에 도착하는 대신 점진적으로 도착합니다:

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

마지막으로, 스트리밍된 청크를 반복하면서 도착하는 각 텍스트 조각을 출력합니다:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

포함된 [chat_with_model.py](assets/chat_with_model.py) 스크립트에는 전체 예제가 들어 있으며 다운로드할 수 있습니다.


## 모델 선택 및 구성

기본적으로 `vllm-launch`는 포트 `8001`에서 테스트 모델로 `Qwen/Qwen3-1.7B`를 서빙합니다. 컨테이너를 다시 빌드하거나 편집하지 않고도 모델, 포트, vLLM 서빙 매개변수를 변경할 수 있습니다.

### AMD가 테스트한 모델

다음 모델은 AMD에 의해 사전 구성되고 검증되었습니다:

| 모델 | 참고 사항 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | 기본 모델입니다. 가볍고 로드 속도가 빠릅니다. |
| `openai/gpt-oss-20b` | 더 높은 품질의 응답을 위한 대형 모델입니다. |

### 다른 모델 실행하기

`--model`(또는 `-m`)로 모델 ID를 전달합니다:

```bash
vllm-launch --model openai/gpt-oss-20b
```

### 포트 변경하기

`--port`(또는 `-p`)로 1024보다 큰 포트를 전달합니다. 기본값은 `8001`입니다:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

포트를 변경한 경우, 클라이언트의 `base_url`을 동일한 포트로 지정하세요(예: `http://localhost:8080/v1`).

### 추가 vLLM 매개변수 전달하기

추가 인수는 vLLM으로 직접 전달되므로 컨텍스트 길이나 데이터 유형과 같은 서빙 동작을 조정할 수 있습니다. 이를 제공하는 방법은 두 가지가 있습니다.

런처 옵션 뒤에 **인라인**으로 지정:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

`~/.local/share/vLLM/vllm-launch.conf`의 구성 파일에 **영구적으로** 지정합니다. 이 파일은 기본적으로 존재하지 않으므로 직접 생성하고 인수를 Bash 배열로 추가하세요:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

기본 인수를 대체하는 대신 추가하려면 `+=`를 사용하세요:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

언제든지 모든 런처 옵션을 확인하려면 다음을 실행하세요:

```bash
vllm-launch --help
```

### 모델 저장 위치

`vllm-launch`는 다음 두 위치에서 모델을 찾습니다:

| 위치 | 경로 |
|----------|------|
| 시스템 모델 | `/var/cache/models` |
| 사용자 모델 | `~/.local/share/vLLM/models` |

다운로드한 모델을 위 두 디렉터리 중 하나에 배치하고 경로나 ID를 `--model`에 전달하여 실행할 수 있습니다:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **참고**: 이런 방식으로 직접 다운로드한 모델을 실행하는 것은 위 디렉터리 중 하나에 모델을 배치하면 작동할 것으로 예상되지만, 이 워크플로는 아직 AMD에서 공식적으로 검증되지 않았습니다.

## 문제 해결

### 연결이 거부됨

서버가 실행 중인지 확인하세요:
```bash
curl http://localhost:8001/health
```

## 요약

이 플레이북에서 다음 방법을 배웠습니다:

- 통합 GPU에서 ROCm 지원과 함께 컨테이너화된 vLLM 시작하기
- 포트 8001에서 OpenAI 호환 API 엔드포인트로 vLLM 서버 시작하기
- `vllm-prompt`로 프롬프트 전송하기
- 스트리밍 및 비스트리밍 요청 모두를 사용하여 vLLM 서버에 API 호출하기
- 서버 시작, 메모리, 클라이언트 연결과 관련된 일반적인 문제 해결하기

이제 통합 GPU에서 최적화된 성능으로 대형 언어 모델을 서빙하는 컨테이너화된 vLLM 배포 환경을 갖추게 되었습니다.

## 다음 단계

- **다양한 모델 시도** — `vllm-launch --model <model>`을 사용하여 다양한 LLM을 실험하고 성능을 비교해 보세요([모델 선택 및 구성](#choosing-and-configuring-a-model) 참조).
- **애플리케이션 구축** — OpenAI 호환 API를 사용하여 vLLM을 Python 앱, 챗봇 또는 자동화 워크플로에 통합하세요.
- **미세 조정 및 서빙** — LoRA 또는 QLoRA를 사용하여 모델을 미세 조정한 다음, 최적화된 추론을 위해 vLLM으로 배포하세요.
## 추가 리소스

- **[vLLM 공식 문서](https://docs.vllm.ai/)** — 포괄적인 가이드 및 API 참조
- **[vLLM GitHub 저장소](https://github.com/vllm-project/vllm)** — 소스 코드, 이슈 및 커뮤니티 토론