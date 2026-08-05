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

🍋 **Lemonade**는 대규모 언어 모델(LLM), 이미지 생성기, 오디오 모델을 사용자의 하드웨어에서 직접 실행할 수 있게 해주는 오픈 소스 로컬 AI 서버입니다. 업계 표준인 **OpenAI API**를 통해 모델을 노출하므로, OpenAI와 호환되는 모든 앱이 즉시 Lemonade와 함께 작동할 수 있습니다. 이 플레이북을 마칠 때쯤이면 Lemonade를 사용하여 사용자의 컴퓨터에서 모델을 로컬로 실행할 수 있게 됩니다.

## 배우게 될 내용

이 플레이북을 마치면 다음을 수행할 수 있습니다:

* **Lemonade Server를 설치**하고 정상적으로 실행되는지 확인합니다.
* 단일 명령으로 **LLM을 다운로드하고 대화**해 봅니다.
* **웹 UI를 살펴보고** 비전, 음성-텍스트 변환, 이미지 생성 등 다양한 모달리티를 시도해 봅니다.
* Vulkan과 AMD ROCm™ 소프트웨어 간에 **GPU 백엔드를 전환**합니다.
* OpenAI 호환 API를 사용하여 로컬 LLM 기반의 **Python 앱을 빌드**합니다.

<!-- @device:halo_box,halo,stx,krk -->
* AMD Ryzen™ AI 하드웨어에서 Hybrid 및 FLM 실행 모드를 사용하여 **AMD Neural Processing Unit(NPU)에서 모델을 실행**합니다.

<!-- @device:end -->

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->

## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

시작하기 전에 다음 사항을 확인하세요:

- **Windows 11** 또는 지원되는 **Linux** 배포판(Ubuntu 24.04+, Fedora, Debian)이 실행되는 PC
- 1~7단계에서 사용되는 런타임 모델(`Gemma-4-E2B-it-GGUF`, 약 3GB)에는 **16GB의 RAM**을 권장합니다. 6단계에서 더 큰 코드 생성 모델(`Qwen3.5-35B-A3B-GGUF`, 약 20GB)을 사용하려면 **32GB 이상**을 권장합니다.
- 다운로드하는 모델에 따라 **약 4~30GB의 여유 디스크 공간**이 필요합니다. 이 가이드에서 가장 큰 모델은 약 20GB입니다.
- **Python 3.10–3.13** (Python 앱 섹션에서 사용됨)
- 인터넷 연결(유선 또는 무선)

<!-- @device:halo_box,halo,stx,krk -->
- [선택 사항] NPU에서 모델을 실행하려는 경우, [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers)에서 최신 드라이버가 설치된 AMD XDNA 2 NPU(Ryzen AI 300/400/Max 300 시리즈 또는 Z2 Extreme)

<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## 핵심 개념 — 로컬 AI 서버의 작동 방식

모델을 실행하기 전에, *왜* 이런 방식으로 구성되어 있는지 이해할 필요가 있습니다. Lemonade는 **로컬 모델 서버**로, AI 모델을 메모리에 로드하고 클라우드 AI 서비스가 하는 것처럼 HTTP를 통해 애플리케이션에 노출하는 프로세스입니다.

### 서버가 필요한 이유는 무엇일까요?

| 이점 | 사용자에게 의미하는 것 |
|---------|----------------------|
| **간소화된 통합** | 앱은 하드웨어별 C++ 또는 Python 라이브러리를 다루는 대신 단일 HTTP API와 통신합니다. |
| **모델 공유** | 로드된 단일 모델이 여러 앱에 동시에 서비스를 제공할 수 있어, RAM을 소비하는 중복 복사본이 생기지 않습니다. |
| **클라우드-로컬 이식성** | OpenAI의 클라우드 API용으로 작성된 코드는 URL 하나만 변경하면 Lemonade와 함께 작동합니다. |
| **관심사 분리** | 모델 관리, 스트리밍, 장애 허용은 서버가 처리하므로 개발자는 자신의 앱에 집중할 수 있습니다. |

### OpenAI API 표준

Lemonade는 ChatGPT, Azure OpenAI 및 수십 개의 다른 서비스에서 사용하는 것과 동일한 인터페이스인 **OpenAI API**를 구현합니다. 대화 모델은 간단합니다:

| 역할 | 대화 주체 |
|------|---------------|
| **system** | 모델에 대한 지시 사항(페르소나, 제약 조건, 사용 가능한 도구) |
| **user** | 사람(또는 애플리케이션)이 모델에 보내는 메시지 |
| **assistant** | 모델이 생성한 응답 |

즉, OpenAI를 지원하는 모든 라이브러리 또는 앱은 Lemonade Server가 실행 중일 때 `http://localhost:13305/api/v1`을 가리키는 것만으로 Lemonade와 통신할 수 있습니다.

## 주요 활동 — 첫 번째 로컬 AI 채팅

LLM을 다운로드하고 사용자 자신의 컴퓨터에서 AI를 완전히 실행하며 대화를 나눠 봅시다.

### 1단계: 모델 다운로드 및 실행

Lemonade에는 엄선된 모델 라이브러리가 포함되어 있습니다. 비전 지원이 포함된 강력하고 소형인 모델인 **Gemma-4-E2B-it**부터 시작해 보겠습니다. 터미널을 열고 다음을 실행합니다:


```
lemonade run Gemma-4-E2B-it-GGUF
```


이 단일 명령은 세 가지 작업을 수행합니다:

1. 모델이 아직 다운로드되지 않은 경우 Hugging Face에서 모델(약 3GB)을 **다운로드**합니다. (시간이 다소 걸릴 수 있습니다)
2. 포트 13305에서 Lemonade Server 프로세스를 **시작**합니다.
3. 모델과 채팅을 시작할 수 있도록 **Lemonade App을 엽니다.**


<!-- @os:windows -->
Windows에서는 Lemonade App이 자동으로 실행되어 바로 채팅을 시작할 수 있습니다. `minimal.msi` 패키지를 설치한 경우 앱이 포함되어 있지 않습니다. 채팅을 시작하려면 웹 브라우저를 열고 `http://localhost:13305`로 이동하세요.

<!-- @os:end -->

<!-- @os:linux -->
Linux에서는 브라우저를 열고 `http://localhost:13305`로 이동하여 웹 앱에 액세스합니다.

<!-- @os:end -->

질문을 입력해 보세요:


```
What are three fun facts about lemons?
```


모델은 채팅 창에서 직접 응답합니다. **축하합니다! 대규모 언어 모델을 로컬에서 실행하고 계십니다.**

![로그가 표시된 Lemonade App](../../dependencies/assets/ChatwithLogs.png)

Lemonade App의 서버 로그 창에서 각 응답 후 모델 성능에 대한 원격 측정 데이터를 확인할 수 있습니다. 예를 들면:


```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 2단계: 웹 인터페이스와 다양한 모달리티 살펴보기

Lemonade에는 다음과 같은 기능을 제공하는 내장 웹 인터페이스가 포함되어 있습니다:

- 익숙한 채팅 창에서 로드된 모델과 **상호작용**
- Model Manager 탭에서 **모델 탐색**
- 원클릭으로 **새 모델 다운로드**

웹 UI의 **Model Manager** 탭에서 Recipe 또는 Category별로 모델을 탐색하며 다양한 모달리티 간 전환을 시도해 보세요:

1. **비전:** 이미 로드한 `Gemma-4-E2B-it-GGUF` 모델은 비전을 지원합니다. 채팅 상자에 이미지를 붙여넣고 모델에게 이미지를 설명해 달라고 요청해 보세요.
2. **이미지 생성:** Image 카테고리에서 Model Manager를 통해 `SDXL-Turbo`와 같은 이미지 모델을 다운로드한 다음, Lemonade Image Generator를 사용해 프롬프트를 입력하고 로컬에서 이미지를 생성해 보세요.
3. **오디오:** Audio 카테고리에서 음성-텍스트 변환이 가능한 `Whisper-Tiny`와 같은 오디오 모델을 다운로드하세요. 오디오 녹음을 제공하여 로컬에서 텍스트로 변환할 수 있습니다. 텍스트-음성 변환의 경우 Speech 카테고리에 있는 `kokoro-v1`과 같은 모델을 사용해 보세요.

![Lemonade를 활용한 다중 모달리티](../../dependencies/assets/multi_modality.png)

### 3단계: 다른 백엔드로 모델 사용해 보기

Lemonade App에서 모델 위에 마우스를 올리면 톱니바퀴 아이콘이 표시됩니다. 이 아이콘을 클릭하면 원하는 백엔드 선택을 포함해 모델 옵션을 설정할 수 있습니다.

기본적으로 Lemonade는 GPU 가속을 위해 Vulkan을 사용합니다. 지원되는 AMD 개별 GPU가 있는 경우 ROCm으로 전환할 수 있습니다.

![Lemonade 백엔드 선택](../../dependencies/assets/lemonademodeloptions.png)

설치된 백엔드를 관리하려면 가장 왼쪽 열의 백엔드 버튼을 클릭하세요.

또는 다음 명령을 사용하여 백엔드를 지정할 수도 있습니다:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

환경 변수 `LEMONADE_LLAMACPP`를 `vulkan`, `rocm`, `cpu` 값 중 하나로 설정하여 기본 백엔드를 지정할 수도 있습니다.

---

## 한 단계 더 나아가기 — Python으로 AI 기반 앱 만들기

로컬 AI 서버의 진정한 강점은 어떤 애플리케이션이든 몇 줄의 코드만으로 연결할 수 있다는 점입니다. 이를 직접 확인하기 위해 주제를 입력하면 플래시카드를 생성하고, 대화형으로 스스로 퀴즈를 풀어볼 수 있는 작지만 실용적인 **학습 플래시카드 생성기**를 만들어 보겠습니다.

### 4단계: 서버 시작하기

Lemonade 서버가 실행 중인지 확인하세요. 설치 후 일반적으로 백그라운드에서 자동으로 시작됩니다. 확인하려면 다음을 실행하세요:

```
lemonade status
```

다음과 같은 메시지가 표시되어야 합니다: `Server is running on port 13305`.

서버가 실행 중이 아니라면 Lemonade 앱을 열어 시작하세요. 기본 포트 **13305**를 사용합니다(트레이 아이콘에서 확인하거나 선택할 수 있습니다).

### 5단계: OpenAI Python 클라이언트 설치하기

터미널에서 venv를 생성하고 다음 명령을 사용하여 OpenAI Python 클라이언트를 설치하세요:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### 6단계: 플래시카드 앱 만들기

코드 생성을 위해 다른 모델인 `Qwen3.5-35B-A3B-GGUF`를 다운로드해 보겠습니다. 이 모델은 크고(~20GB) 성능이 뛰어나 32GB 이상의 RAM을 갖춘 시스템에 가장 적합합니다. 사용 가능한 RAM이 더 적다면 대신 `Qwen3.5-9B-GGUF`(~6GB)를 사용해 보세요.

UI에서 다운로드하거나 다음을 실행할 수 있습니다:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

간단한 플래시카드 앱의 코드를 생성하기 위해 다음 프롬프트를 Lemonade Chat UI에 입력하세요.

Python 앱을 생성하는 데는 코드 작성에 더 뛰어난 대형 모델인 Qwen3.5-35B-A3B-GGUF를 사용하며, 앱 자체는 런타임에 이미 다운로드한 소형 모델인 Gemma-4-E2B-it-GGUF를 호출합니다. 생성된 코드는 원하는 파일에 복사하여 Python으로 실행할 수 있습니다.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **팁**: 철저한 프롬프트 작성과 리소스 및 속도 최적화를 위한 두 모델 시스템 사용이라는 표준 엔지니어링 방식을 따랐습니다.

편의를 위해 예시 출력을 [`flashcards.py`](assets/flashcards.py)로 제공했습니다. 자유롭게 다운로드하여 원하는 디렉터리에 저장하세요. 어느 쪽이든 이제 실행 가능한 Python 파일이 준비되어 있어야 합니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### 7단계: 생성된 코드 실행하기

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**다음과 같은 화면이 표시됩니다:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

약 150줄의 코드로 로컬 LLM으로 구동되는 완전한 기능을 갖춘 학습 도구를 만들었습니다. 관리할 API 키도 없고, 사용 비용도 없으며, 데이터가 기기 밖으로 전송되지 않습니다.

> **핵심 포인트:** `client = OpenAI(base_url=...) ` 줄이 이 앱을 OpenAI 클라우드가 아닌 Lemonade에 연결하는 *유일한* 부분이라는 점에 주목하세요. 나머지 코드는 OpenAI 호환 서비스에 대해 작성하는 것과 동일합니다. OpenAI Python 라이브러리를 사용해 본 적이 있다면, 이미 Lemonade로 앱을 만드는 방법을 알고 있는 셈입니다.

### 이것이 보여주는 것

이 작은 앱은 여러 실제 통합 패턴을 활용합니다:

| 패턴 | 나타나는 위치 |
|---------|-----------------|
| **시스템 프롬프트** | `"system"` 메시지는 LLM에 구조화된 JSON을 출력하도록 지시합니다 |
| **구조화된 출력** | 앱은 LLM의 응답을 JSON으로 파싱하여 플래시카드를 생성합니다 |
| **상태 비저장 요청** | 각 `generate_flashcards()` 호출은 독립적입니다 |
| **오류 처리** | `try/except`는 LLM의 출력이 유효한 JSON이 아닌 경우를 우아하게 처리합니다 |

이러한 패턴은 챗봇, 코드 어시스턴트, 콘텐츠 생성기, 자동화 도구와 같은 모든 애플리케이션에 동일하게 적용됩니다.

#### 추가 도전 과제

* 도전 과제를 하나 더 원한다면, [여기](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)에 제공된 예시를 참고하여 사용자에게 플래시카드를 읽어주는 기능을 추가해 보세요.

---

<!-- @device:halo_box,halo,stx,krk -->
## NPU에서 모델 실행 (선택 사항)

Ryzen AI 300/400/Max 300 시리즈 또는 Z2 Extreme을 보유하고 있다면, 사용 중인 기기에는 AI 워크로드를 위해 특별히 설계된 전용 칩인 **NPU(Neural Processing Unit)**가 내장되어 있습니다. NPU에서 모델을 실행하면 GPU를 사용하는 것보다 전력 효율이 높아, 백그라운드 AI 작업, 장시간 세션, 배터리 사용 환경에 이상적입니다.

Lemonade는 세 가지 NPU 실행 모드를 지원하며, 모두 동일한 OpenAI API 뒤에서 투명하게 작동합니다.

| 모드 | 작동 방식 | 레시피 | 예시 모델 |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU가 프롬프트를 처리하고, iGPU가 토큰을 생성 | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU 전용** | 전체 추론이 NPU에서 실행 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | NPU에서 FastFlowLM 엔진을 사용하며, AMD XDNA2에 최적화 | FLM (`flm`) | qwen3.5-4b-FLM |

### 요구 사항

- **AMD Ryzen AI 300/400 시리즈 또는 Z2 시리즈** 프로세서
- **FLM** 모델의 경우: FLM 런타임은 Lemonade 앱 내에서 설치할 수 있으며, FLM 모델을 실행할 때 Lemonade가 자동으로 FLM 런타임을 설치합니다. FastFlowLM에 대해 자세히 알아보려면 [여기](https://fastflowlm.com/docs/)를 참고하세요.


### 8단계: Hybrid 모델 실행하기

Hybrid 모델은 NPU와 iGPU 간에 작업을 분산하여 속도와 효율성의 균형을 잘 유지합니다. Lemonade 앱에서 `Ryzen AI LLM` 목록에서 모델을 선택하세요. 예를 들어 `Qwen3-4B-Hybrid`를 선택하거나 다음 명령을 사용하여 실행할 수 있습니다:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade는 NPU를 자동으로 감지하여 **Ryzen AI LLM** 백엔드를 설치합니다.

> **내부적으로 어떤 일이 일어나나요?** 메시지를 보내면 NPU가 전체 프롬프트를 병렬로 처리합니다(이를 "prefill"이라고 함). 그런 다음 iGPU가 응답을 한 번에 하나의 토큰씩 생성합니다(이를 "decode"라고 함). 이 하이브리드 방식은 각 칩의 강점을 최대한 활용합니다.

### 9단계: FLM 모델 실행하기

FastFlowLM(FLM) 모델은 AMD의 XDNA2 NPU 아키텍처에 특별히 최적화되어 있으며, 크기 대비 매우 빠른 속도를 낼 수 있습니다. 예를 들어 `FastFlowLM NPU` 목록에서 `qwen3.5-4b-FLM`을 선택하거나 다음 명령을 사용하세요:

<!-- @os:windows -->
Windows에서 `FastFlowLM`을 활성화하려면:

* `Backends Manager` 메뉴를 엽니다.
* `FastFlowLM NPU` 백엔드 카테고리를 찾습니다.
* Install NPU를 클릭합니다.
* 설치가 완료되면 약 36개의 기본 모델이 FFLM 드롭다운 메뉴에 표시됩니다.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
`Lemonade` 앱을 처음 실행하면 `FastFlowNPU` 백엔드가 기본적으로 활성화되어 있지 않습니다.
로컬 앱이 설치 페이지를 열어 설정 과정을 안내합니다.

Linux에서 `FastFlowLM`을 활성화하려면:

* `Lemonade` 앱을 엽니다.
* [공식 FLM](https://lemonade-server.ai/flm_npu_linux.html) 문서를 방문하여 사용 중인 Linux 배포판을 선택한 후 FLM 설치 단계를 따르세요.
* 설치 페이지의 안내에 따라 백포트(backports)를 활성화합니다.
* [태그 페이지](https://github.com/FastFlowLM/FastFlowLM/tags)에서 최신 `v0.9.x` 릴리스를 다운로드합니다.'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
AMD Halo Developer Platform의 경우, 반드시 Debian 13을 선택하세요.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* 다운로드한 `.deb` 패키지를 설치합니다.
* 권장: `Lemonade App`을 종료했다가 다시 열어 변경 사항이 감지되도록 합니다.
* 권장: `Backends Manager`를 열고 `FastFlowNPU` Backend를 Install 클릭합니다.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
설치가 성공적으로 완료되면, **Lemonade Desktop App** 내의 **Download Manager**에서 `flm:npu`가 완료된 것을 확인할 수 있습니다.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
그런 다음 사용 가능한 FFLM 모델 중 원하는 것을 선택하여 NPU 백엔드를 사용할 수 있습니다.

특정 모델의 경우, [모델 페이지](https://fastflowlm.com/docs/models/qwen/)에서 원하는 모델을 다운로드한 후 문서에 제공된 Shell 명령을 사용하여 검증하세요.
```
flm run qwen3.5-4b-FLM
```
또는 
```
lemonade run qwen3.5-4b-FLM
```
를 통해
FLM 모델에는 가장 인기 있는 아키텍처(Gemma 3, Qwen 3, Llama 3, DeepSeek R1) 중 일부가 포함되어 있으며, 1GB 미만부터 13GB 이상까지 다양합니다.
Lemonade는 NPU를 자동으로 감지하여 **FastFlowLM NPU** 백엔드를 설치합니다.

<!-- @os:windows -->
> **팁:** 최상의 NPU 성능을 위해 터보 모드를 활성화하세요:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### 모델 전환하기

6단계의 플래시카드 앱은 NPU 모델에서도 작동하며, 모델 이름만 변경하면 됩니다:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 다음 단계

이제 자신의 하드웨어에서 실행되는 로컬 AI 서버를 갖게 되었습니다. 다음으로 진행할 수 있는 단계는 다음과 같습니다:

1. **즐겨 사용하는 앱과 연결하기**: Lemonade는 [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), 그리고 [더 많은 앱](https://lemonade-server.ai/marketplace)과 별도의 설정 없이 바로 작동합니다.

2. **더 많은 모델 살펴보기**: 전체 [모델 라이브러리](https://lemonade-server.ai/docs/server/server_models/)를 탐색하여 코딩, 추론, 비전 등에 최적화된 모델을 찾아보세요. Lemonade 앱이나 `lemonade list` 명령을 사용하여 사용 가능한 모델을 확인할 수 있습니다.

3. **ROCm GPU 가속 활용하기**: 지원되는 AMD GPU를 보유하고 있다면 ROCm 백엔드로 전환하세요: `lemonade config set llamacpp.backend=rocm`. [지원되는 AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)를 참고하세요.

4. **전체 API 사양 읽어보기**: Lemonade는 채팅 완성, 임베딩, 오디오 전사, 이미지 생성, 텍스트 음성 변환 등을 지원합니다. 모든 엔드포인트는 [서버 사양](https://lemonade-server.ai/docs/server/server_spec/)에서 확인할 수 있습니다.

5. **기여하기**: Lemonade는 오픈 소스입니다. [기여 가이드](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)를 확인하고 [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)를 찾아보세요.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->