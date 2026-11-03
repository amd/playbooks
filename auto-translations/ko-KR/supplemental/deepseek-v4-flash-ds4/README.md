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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)는 DeepSeek V4 패밀리의 효율성에 초점을 맞춘 버전으로, 2,840억 개의 파라미터를 가진 Mixture of Experts 모델이며 130억 개의 활성 파라미터를 사용합니다. [DeepSeek의 기술 보고서](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)에 따르면, SWE-bench Verified에서 79%, LiveCodeBench에서 91.6%의 점수를 기록했습니다.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4)는 이 모델 아키텍처만을 위해 구축된 전용 추론 엔진입니다. 범용 런타임이 아니라, ds4는 AMD ROCm™ 소프트웨어를 위한 아키텍처별 커널 최적화를 통해 DeepSeek V4 패밀리를 직접 대상으로 합니다. 현재 Strix Halo에서 DeepSeek V4 Flash를 구현한 가장 성능이 뛰어난 구현체 중 하나입니다.

이 튜토리얼에서는 터미널 UI인 `ai-toolbox-cockpit`을 사용하여 ds4를 설정하고, 모델 가중치를 다운로드하며, AMD Ryzen™ AI Halo Developer Platform에서 DeepSeek V4 Flash를 로컬로 서빙하는 방법을 보여줍니다.

## 학습 내용

- `ai-toolbox-cockpit` 터미널 UI를 설치하고 실행하는 방법
- ds4 ROCm 툴박스 컨테이너를 생성하는 방법
- 단일 Halo 노드에 권장되는 양자화 버전을 다운로드하는 방법
- ds4 추론 서버를 시작하고 OpenAI 호환 엔드포인트를 노출하는 방법
- Web UI 또는 코딩 에이전트를 로컬 서버에 연결하는 방법

## 메모리 구성 설정

<!-- @require:memory-config -->

## 소프트웨어 사전 요구 사항 설치

> **이 구성(단일 노드 IQ2_XXS, 126k 컨텍스트)의 시스템 요구 사항:**
> - **최소 128GB의 통합 메모리**를 갖춘 Strix Halo 시스템.
> - 공유 메모리 풀을 최대한 크게 확보할 수 있도록 **BIOS 전용 VRAM(UMA 프레임 버퍼)을 최소값으로 설정**.
> - GPU **공유 메모리 풀을 최소 110GB로 설정**: `amd-ttm --set 110`을 실행(위의 메모리 구성 단계 참조)한 후 재부팅합니다. 값이 낮으면 모델이 126k 컨텍스트로 로드될 때 메모리 부족 오류가 발생할 수 있습니다. 시스템에 사용 가능한 메모리가 더 적다면, 대신 Server Mode에서 **Context** 값을 낮추십시오.
>
> **참고:** 시작점으로 **GPU 공유 메모리 풀**을 **110GB**로 설정해 보십시오. 메모리 부족 오류가 발생하면 공유 메모리 풀을 늘리거나 컨텍스트 크기를 줄이십시오.

ai-toolbox-cockpit은 컨테이너 툴박스를 사용하여 ds4 엔진을 실행합니다. `podman`, `distrobox`, `pipx`를 설치하십시오:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## 사용 가능한 양자화 버전

ds4 개발자는 GGUF 형식으로 여러 양자화된 DeepSeek V4 Flash 버전을 제공합니다. 아래의 모든 모델은 중요도 행렬(imatrix) 보정을 사용하여, 코딩 및 추론 작업에 가장 중요한 모델 부분에 대해 더 높은 정밀도를 유지합니다.

| 양자화 | 크기 | 설명 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8GB | 단일 128GB 노드에 권장 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97GB | 정확도 향상을 위해 37~42 레이어를 Q4 정밀도로 유지. 128GB에 맞지만 컨텍스트를 위한 여유 공간이 적음 |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153GB | 더 높은 품질. 멀티 노드 클러스터링을 통해 두 개의 Halo 노드 필요 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6GB | 생성 속도를 개선하기 위한 추측 디코딩용 선택적 추가 구성 요소 |

**IQ2_XXS imatrix** 모델은 좋은 시작점입니다. 단일 노드에 충분히 들어맞으며, 합리적인 컨텍스트 창을 위한 충분한 메모리 여유를 남깁니다.

## ai-toolbox-cockpit 설치

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit)은 다양한 AI 백엔드를 쉽게 설치할 수 있도록 해주는 가벼운 터미널 UI입니다. 이를 사용하여 ds4 컨테이너 생성, 모델 가중치 다운로드, 서버 시작을 처리합니다. `pipx`로 설치하십시오:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

콕핏을 실행하십시오:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## 1단계: 툴박스 생성

**Interactive Toolboxes** 탭에서 ds4에 사용할 수 있는 최신 안정 버전 툴박스(예: `ds4-rocm-10.0`)를 선택하고 **Create/Update**를 클릭합니다. 이렇게 하면 컨테이너 이미지를 가져와 툴박스 환경을 생성합니다.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## 2단계: 모델 다운로드

**Models** 탭으로 이동합니다. 먼저 백엔드(ds4)를 선택합니다. 그런 다음 드롭다운에서 **IQ2_XXS imatrix (~80.8GB)**를 선택하고 **Download**를 클릭합니다. 모델 파일은 기본적으로 `~/ds4`에 저장됩니다(저장 경로는 변경할 수 있습니다).

> **참고:** IQ2_XXS 모델은 약 80GB 크기이므로, 연결 속도에 따라 다운로드에 시간이 걸릴 수 있습니다. 다운로드가 완료되면 계속 진행할 수 있습니다.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## 3단계: 서버 시작

**Server Mode** 탭으로 이동합니다. 다운로드한 모델과 툴박스를 선택한 다음, 컨텍스트 크기, 호스트, 포트를 구성합니다. 준비가 되면 **Start ds4-server**를 클릭합니다.

> **팁** `126000`의 컨텍스트 크기는 단일 노드에 맞을 것으로 예상되는 합리적인 시작 값입니다. 여유 메모리가 있다면 더 높게 설정할 수 있고, 메모리 부족 오류가 발생하면 더 낮출 수 있습니다. 포트(이 가이드에서는 `8000`)는 임의로 지정된 값이므로 사용 가능한 포트를 아무거나 선택하십시오.

> **KV 디스크 캐시(선택 사항).** **KV Disk Cache**를 켜면 KV 캐시를 디스크(**Host Cache Dir**, 기본값 `~/.cache/ds4-kv`)로 오프로드하여, 반복되는 시스템 프롬프트를 다시 계산하는 대신 SSD에서 복원합니다. 이는 길고 반복적인 프롬프트를 사용하는 코딩 에이전트 워크플로를 위한 성능 최적화 기능이며, 서버를 실행하는 데 **필수는 아닙니다**.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

서버가 시작되어 포트 8000에서 대기하며, `http://localhost:8000/v1`에서 OpenAI 호환 API 엔드포인트를 노출합니다.

**빠른 테스트:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->
## 웹 UI 연결하기

OpenAI API 형식을 지원하는 모든 채팅 인터페이스를 연결할 수 있습니다. 예를 들어, HuggingFace ChatUI를 사용하려면 다음과 같이 합니다:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

브라우저에서 `http://localhost:3000`을 열어 채팅을 시작하세요.

> **참고:** `--network=host`는 웹 UI를 호스트의 네트워크에 배치하여 `localhost`에서 ds4 서버에 직접 접근할 수 있도록 합니다. 이렇게 하면 ds4 서버는 계속 루프백에 바인딩된 상태로 유지되어(다른 인터페이스에 노출할 필요가 없습니다).

> **팁:** 웹 UI 포트(여기서는 `3000`이며 `PORT`를 통해 설정됨)는 임의로 지정할 수 있습니다 — `3000`이 이미 사용 중이라면 사용 가능한 다른 포트를 선택하고, 브라우저에서 해당 포트를 열면 됩니다. `OPENAI_BASE_URL`의 포트가 ds4 서버가 실행 중인 포트와 일치하는지 확인하세요.

## 코딩 에이전트 연결하기

ds4 서버는 OpenAI 및 Anthropic 호환 엔드포인트를 모두 제공하므로, 대부분의 코딩 에이전트가 직접 연결할 수 있습니다. 예를 들어, `pi` 코딩 에이전트에 추가하려면 `~/.pi/agent/models.json`에 다음 블록을 추가하세요:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **팁**: 코딩 에이전트나 웹 UI가 Halo 플랫폼과 다른 머신에서 실행 중인 경우, SSH를 통해 서버 포트(여기서는 `8000`)를 포워딩해야 합니다:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## 다음 단계

- **멀티 노드 클러스터링**: Halo 장치가 두 대 있는 경우, ds4는 파이프라인 병렬 처리를 통해 두 머신에 걸쳐 Q4 모델(~153GB)을 분산시킬 수 있습니다. 설정 방법은 [ds4-toolbox 문서](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)를 참고하세요.
- **추측 디코딩(MTP)**: MTP 가중치(~3.6GB)를 다운로드하고 서버에 `--mtp`를 전달하면 생성 속도가 더 빨라집니다.
- **KV 캐시 디스크 오프로딩**: 코딩 에이전트 워크플로의 경우, `--kv-disk-dir`를 활성화하면 반복되는 시스템 프롬프트를 매번 다시 계산하는 대신 SSD에서 복원할 수 있습니다.

자세한 내용은 [ds4 저장소](https://github.com/antirez/ds4)와 [ds4-cockpit toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox)를 참고하세요.