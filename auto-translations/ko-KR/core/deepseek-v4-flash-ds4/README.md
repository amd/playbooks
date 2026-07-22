<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북에는 GitHub에서 렌더링할 수 없는 특수 태그가 사용되었습니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

## 개요

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)는 DeepSeek V4 제품군 중 효율성에 중점을 둔 버전으로, 활성 파라미터 130억 개를 가진 2,840억 파라미터 규모의 Mixture of Experts 모델입니다. [DeepSeek의 기술 보고서](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)에 따르면, SWE-bench Verified에서 79%, LiveCodeBench에서 91.6%의 점수를 기록했습니다.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4)는 이 모델 아키텍처를 위해 특별히 제작된 전용 추론 엔진입니다. 범용 런타임이 아니라, ds4는 AMD ROCm™ 소프트웨어를 위한 아키텍처 특화 커널 최적화를 통해 DeepSeek V4 제품군을 직접 대상으로 합니다. 현재 Strix Halo에서 DeepSeek V4 Flash를 구현한 것 중 가장 성능이 뛰어난 구현체 중 하나입니다.

이 튜토리얼에서는 터미널 UI인 `ds4-cockpit`을 사용하여 ds4를 설정하고, 모델 가중치를 다운로드하며, AMD Ryzen™ AI Halo Developer Platform에서 DeepSeek V4 Flash를 로컬로 서비스하는 방법을 보여줍니다.

## 배우게 될 내용

- 터미널 UI `ds4-cockpit`을 설치하고 실행하는 방법
- ds4 ROCm 툴박스 컨테이너를 생성하는 방법
- 단일 Halo 노드를 위한 권장 양자화 다운로드
- ds4 추론 서버를 시작하고 OpenAI 호환 엔드포인트를 노출하는 방법
- Web UI 또는 코딩 에이전트를 로컬 서버에 연결하는 방법

<!-- @setup:memory_config -->

## 소프트웨어 필수 구성 요소 설치

> **이 구성에 대한 시스템 요구 사항(126k 컨텍스트의 단일 노드 IQ2_XXS):**
> - **최소 128GB의 통합 메모리**를 갖춘 Strix Halo 시스템.
> - 공유 메모리 풀을 최대한 크게 사용할 수 있도록 **BIOS 전용 VRAM(UMA 프레임 버퍼)을 최소값으로 설정**.
> - GPU **공유 메모리 풀을 최소 110GB로 설정**: `amd-ttm --set 110`을 실행(위의 메모리 구성 단계 참조)한 후 재부팅합니다. 값이 낮으면 126k 컨텍스트로 모델을 로드할 때 메모리 부족 오류가 발생합니다. 시스템에 사용 가능한 메모리가 더 적다면 대신 Server Mode의 **Context** 값을 낮추세요.

ds4-cockpit은 컨테이너 툴박스를 사용하여 ds4 엔진을 실행합니다. `podman`, `distrobox`, `pipx`를 설치하세요:

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

ds4 저자는 GGUF 형식으로 DeepSeek V4 Flash의 여러 양자화 버전을 제공합니다. 아래의 모든 모델은 importance matrix(imatrix) 보정을 사용하여, 코딩 및 추론 작업에 가장 중요한 모델 부분에 대해 더 높은 정밀도를 유지합니다.

| 양자화 | 크기 | 설명 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8GB | 단일 128GB 노드에 권장 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97GB | 정확도 향상을 위해 37~42번 레이어를 Q4 정밀도로 유지. 128GB에는 들어가지만 컨텍스트를 위한 여유 공간이 줄어듦 |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153GB | 더 높은 품질. 멀티 노드 클러스터링을 통해 두 개의 Halo 노드가 필요 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6GB | 생성 속도를 향상시키기 위한 speculative decoding용 선택적 추가 기능 |

**IQ2_XXS imatrix** 모델은 좋은 출발점입니다. 단일 노드에 무리 없이 들어가고, 적절한 컨텍스트 윈도우를 위한 충분한 메모리 여유를 남깁니다.

## ds4-cockpit 설치

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox)은 Strix Halo에서 ds4를 쉽게 실행할 수 있게 해주는 가벼운 터미널 UI입니다. 툴박스 컨테이너 생성, 모델 가중치 다운로드, 서버 시작을 처리합니다. `pipx`로 설치하세요:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

콕핏을 실행합니다:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## 툴박스 생성

**Interactive Toolboxes** 탭에서 사용 가능한 최신 툴박스(예: `ds4-rocm-7.2.4`)를 선택하고 **Create/Update**를 클릭합니다. 이렇게 하면 컨테이너 이미지를 가져와서 툴박스 환경을 생성합니다.

> **팁**: 새로운 ROCm 빌드가 출시됨에 따라 툴박스 버전이 시간이 지나면서 변경됩니다. 목록에서 사용 가능한 최신 버전을 선택하세요.

<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## 모델 다운로드

**Model Manager** 탭으로 이동합니다. 드롭다운에서 **IQ2_XXS imatrix (~80.8GB)**를 선택하고 **Download**를 클릭합니다. 모델 파일은 기본적으로 `~/ds4`에 저장됩니다(저장 경로는 변경 가능).

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
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

## 서버 시작

**Server Mode** 탭으로 이동합니다. 다운로드한 모델과 툴박스를 선택한 다음, 컨텍스트 크기(예: 126000), 호스트, 포트(8000)를 구성합니다. 준비되면 **Start ds4-server**를 클릭합니다.

> **KV Disk Cache(선택 사항).** **KV Disk Cache**를 켜면 KV 캐시를 디스크(**Host Cache Dir**, 기본값 `~/.cache/ds4-kv`)로 오프로드하여, 반복되는 시스템 프롬프트를 다시 계산하는 대신 SSD에서 복원합니다. 길고 반복적인 프롬프트가 있는 코딩 에이전트 워크플로우를 위한 성능 최적화 기능이며, 서버를 실행하는 데 **필수는 아닙니다**.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

서버가 시작되어 포트 8000에서 대기하며, `http://localhost:8000/v1`에서 OpenAI 호환 API 엔드포인트를 노출합니다.

**간단한 테스트:**
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
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
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

## Web UI 연결

OpenAI API 형식을 지원하는 모든 채팅 인터페이스를 연결할 수 있습니다. 예를 들어 HuggingFace ChatUI를 사용하려면 다음과 같이 합니다:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

브라우저에서 `http://localhost:3000`을 열어 채팅을 시작하세요.

## 코딩 에이전트 연결

ds4 서버는 OpenAI 및 Anthropic 호환 엔드포인트를 모두 노출하므로, 대부분의 코딩 에이전트가 직접 연결할 수 있습니다. 예를 들어 `pi` 코딩 에이전트에 추가하려면, `~/.pi/agent/models.json`에 다음 블록을 추가하세요:

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

> **팁**: 코딩 에이전트나 Web UI가 Halo 플랫폼과 다른 머신에서 실행 중인 경우, SSH를 통해 포트 8000을 포워딩해야 합니다:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```
## 다음 단계

- **멀티 노드 클러스터링**: Halo 장치가 두 대 있다면, ds4는 파이프라인 병렬 처리를 통해 Q4 모델(~153GB)을 두 대의 머신에 분산할 수 있습니다. 설정 방법은 [ds4-toolbox 문서](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)를 참고하세요.
- **추측 디코딩(MTP)**: MTP 가중치(~3.6GB)를 다운로드한 후 서버에 `--mtp`를 전달하면 생성 속도를 더 빠르게 할 수 있습니다.
- **KV 캐시 디스크 오프로딩**: 코딩 에이전트 워크플로의 경우 `--kv-disk-dir`를 활성화하면 반복되는 시스템 프롬프트를 매번 다시 계산하지 않고 SSD에서 복원할 수 있습니다.

자세한 내용은 [ds4 저장소](https://github.com/antirez/ds4) 및 [ds4-cockpit 툴박스](https://github.com/kyuz0/strix-halo-ds4-toolbox)를 참고하세요.