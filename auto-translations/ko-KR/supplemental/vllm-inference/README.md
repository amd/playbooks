<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->


## 개요

vLLM은 대규모 언어 모델(LLM)을 위해 설계된 고성능 추론 엔진입니다. 높은 처리량을 위한 연속 배치(continuous batching)로 최적화된 서빙을 제공하며, 애플리케이션과의 원활한 통합을 위한 OpenAI 호환 API를 제공합니다. 이러한 특징 덕분에 vLLM은 속도와 리소스 효율성이 중요한 프로덕션 배포에 매우 적합합니다.

이 플레이북에서는 통합 GPU에서 컨테이너화된 vLLM을 사용하여 LLM을 서빙하고 OpenAI Python API를 통해 모델과 상호작용하는 방법을 배웁니다.

## 학습 내용

- AMD ROCm™ 지원으로 vLLM 서버를 설정하고 시작하는 방법
- OpenAI 호환 API 엔드포인트를 통해 모델과 상호작용하는 방법
- `vllm-prompt`를 사용하여 로컬 서버에 프롬프트를 전송하는 방법

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

> **참고**: VS Code가 설치되어 있지 않은 경우, AMD Ryzen™ AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치

이 플레이북은 vLLM, ROCm 지원, 그리고 서버 실행에 필요한 헬퍼 스크립트가 포함된 사전 빌드된 컨테이너 이미지를 사용합니다. PyTorch, vLLM 또는 로컬 플레이북 스크립트를 수동으로 설치할 필요가 없습니다.

호스트 측에서 별도의 vLLM 설치 단계는 필요하지 않습니다. 다음 명령으로 vLLM을 시작하세요:

```bash
vllm-launch
```

런처는 컨테이너를 시작하고 통합 GPU를 대상으로 지정하며 로컬 OpenAI 호환 vLLM 서버를 노출합니다. 또는 작업 표시줄에서 vLLM 아이콘을 클릭할 수도 있습니다.

## 빠른 시작

### 1. vLLM 서버가 실행 중인지 확인

`vllm-launch`가 모든 것을 초기화하는 데 몇 분 정도 걸릴 수 있습니다. 시작되면 서버는 `http://localhost:8001`에서 사용할 수 있습니다. 서버가 포그라운드에서 실행되므로 실행 터미널을 열어 두고, 나머지 단계를 위해 별도의 터미널을 여세요. 아래 예제는 `Qwen/Qwen3-1.7B`를 사용합니다. 런처가 다른 모델로 구성되어 있다면 요청에서 해당 모델 ID로 대체하세요.

### 2. 프롬프트 전송

제공된 `vllm-prompt` 스크립트를 사용하여 로컬 vLLM OpenAI 호환 서버에 요청을 전송하세요:

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API를 사용하여 모델과 채팅

vLLM은 OpenAI 호환 API를 제공하므로 `openai` Python 패키지를 사용하여 상호작용할 수 있습니다.

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

OpenAI 서버 대신 로컬 vLLM 서버를 가리키는 `OpenAI` 클라이언트를 생성합니다. 클라이언트에는 `api_key`가 필요하지만 vLLM은 이를 검증하지 않으므로 아무 문자열이나 사용할 수 있습니다:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

그런 다음 채팅 완성 요청을 전송합니다. 이는 OpenAI API와 동일한 메시지 형식, 즉 `"user"`, `"assistant"`와 같은 역할(role)을 가진 메시지 목록을 사용합니다. `stream=True`로 설정하면 응답이 한 번에 오지 않고 점진적으로 도착합니다:

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

마지막으로 스트리밍된 청크를 순회하며 도착하는 각 텍스트 조각을 출력합니다:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

포함된 [chat_with_model.py](assets/chat_with_model.py) 스크립트에는 전체 예제가 담겨 있으며 다운로드할 수 있습니다.


## 문제 해결

### 연결 거부(Connection refused)

서버가 실행 중인지 확인하세요:
```bash
curl http://localhost:8001/health
```

## 요약

이 플레이북에서 다음 내용을 학습했습니다:

- 통합 GPU에서 ROCm 지원으로 컨테이너화된 vLLM 시작하기
- 포트 8001에서 OpenAI 호환 API 엔드포인트를 사용하여 vLLM 서버 시작하기
- `vllm-prompt`로 프롬프트 전송하기
- 스트리밍 및 비스트리밍 요청을 모두 사용하여 vLLM 서버에 API 호출하기
- 서버 시작, 메모리, 클라이언트 연결과 관련된 일반적인 문제 해결하기

이제 통합 GPU에서 최적화된 성능으로 대규모 언어 모델을 서빙하는 컨테이너화된 vLLM 배포 환경을 갖추게 되었습니다.

## 다음 단계

- **다양한 모델 시도** — `vllm-launch` 구성에서 모델을 교체하여 다양한 LLM을 실험하고 성능을 비교해 보세요.
- **애플리케이션 구축** — OpenAI 호환 API를 사용하여 vLLM을 Python 앱, 챗봇 또는 자동화 워크플로에 통합해 보세요.
- **미세 조정 및 서빙** — LoRA 또는 QLoRA를 사용하여 모델을 미세 조정한 다음 vLLM으로 배포하여 최적화된 추론을 수행해 보세요.

## 추가 자료

- **[vLLM 공식 문서](https://docs.vllm.ai/)** — 종합 가이드 및 API 참조
- **[vLLM GitHub 리포지토리](https://github.com/vllm-project/vllm)** — 소스 코드, 이슈, 커뮤니티 논의