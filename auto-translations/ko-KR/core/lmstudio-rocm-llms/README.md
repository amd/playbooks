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

LM Studio는 [llama.cpp](https://github.com/ggml-org/llama.cpp)를 위한 강력한 GUI 기반 래퍼이며, 로컬 모델 서빙을 위한 [OpenAI 호환 엔드포인트](https://lmstudio.ai/docs/developer/openai-compat)도 제공합니다. LM Studio는 모델을 손쉽게 다운로드하고 배포할 수 있는 간단하면서도 강력한 인터페이스를 제공합니다. LM Studio는 AMD 사용자를 위해 Vulkan과 AMD ROCm™ 소프트웨어 백엔드(런타임이라고 함)를 모두 제공합니다.


## 배우게 될 내용
- 로컬 하드웨어를 활용하도록 LM Studio를 구성하고 사용하는 방법
- 완전히 오프라인 환경에서 LLM을 테스트하고 관리하는 방법
- OpenAI 호환 API를 통해 모델을 서빙하여 사용자 지정 워크플로우와 앱을 구동하는 방법


## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @os:linux -->
> **참고**: AMD Ryzen™ AI Developer Center를 통해 VS Code를 설치할 수 있습니다. LM Studio의 경우 아래 설치 지침을 따르세요.
<!-- @os:end -->

<!-- @os:windows -->
> **참고**: VS Code 또는 LM Studio가 설치되어 있지 않은 경우 AMD Ryzen™ AI Developer Center에서 설치할 수 있습니다.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## 모델 다운로드

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## LLM과 채팅하기
완전히 로컬 환경에서 ChatGPT급 LLM과 채팅을 시작하는 방법을 알아봅니다.

1. LMStudio를 엽니다.
2. `Ctrl + L`을 눌러 모델 로더를 열고 `Manually choose model load parameters`를 선택한 다음 `${model_name}`을 클릭합니다.
3. "show advanced settings"가 체크되어 있는지 확인합니다.
4. 원하는 대로 `Context Length`를 변경합니다. 컨텍스트 길이가 길수록 더 많은 모델 메모리가 필요하지만, 시스템 메모리 사용량도 증가합니다. 이 플레이북에서는 4096을 권장합니다.
5. `GPU Offload`가 최대로 설정되어 있고 `Flash Attention`이 켜져 있는지 확인합니다(Cache Quantizations는 꺼진 상태로 두어도 됩니다).
6. `Remember settings`를 체크하고 `Load Model`을 클릭합니다.
7. 채팅 창에 있지 않다면 `Ctrl + 1`을 누르거나 화면 왼쪽 상단의 👾 버튼을 클릭합니다.
8. 메시지를 보내고 모델과 상호작용을 시작하세요!

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **팁**: 컨텍스트 길이는 모델의 메모리를 의미합니다. Flash attention은 메모리 사용량을 줄이면서 처리 속도를 향상시킵니다. GPU Offload는 더 빠른 응답을 위해 연산을 그래픽 카드로 이전합니다.

## OpenAI 호환 엔드포인트를 통해 LLM 서빙하기

LM Studio는 LM Studio Server 형태로 OpenAI 호환 엔드포인트도 제공합니다. 이는 Cline을 사용한 에이전틱 코딩 워크플로우에서 [여기](../playbooks/vscode-qwen3-coder)에 이미 시연되어 있습니다. 또 다른 일반적인 사용 사례는 표준 HTTP 요청을 추론 엔드포인트로 전송하여 LM Studio Server를 웹 애플리케이션(React, Node.js, Python)에 연결하는 것입니다.

LM Studio Server를 설정하려면 다음 지침을 따르세요.

1. 왼쪽에서 `Developer` 탭(명령줄 아이콘)을 클릭하거나 `Ctrl + 2`를 누른 다음 `Server Settings`를 클릭합니다.
2. (선택 사항): LAN을 통해 모델을 서빙하려면 `Serve on Local Network`를 체크합니다. 웹사이트나 VS Code 내에서 광범위한 호출과 함께 사용하려면 `Enable CORS`를 체크합니다.
3. 왼쪽 상단에서 `Status` 앞의 토글 버튼을 클릭하여 서버가 실행 중인지 확인합니다.
4. 이제 OpenAI 호환 엔드포인트가 실행됩니다. 주소는 일반적으로 http://127.0.0.1:1234 입니다.
5. 모델이 아직 로드되지 않았다면 `Load Model`을 클릭하고 앞서 설명한 단계를 따라 로드할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


이제 이 모델은 LM Studio Server 엔드포인트를 통해 접근할 수 있으며, 다음을 포함한 OpenAI 엔드포인트를 지원합니다:

| 엔드포인트 | 메서드 | 문서 |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### 예제: 엔드포인트 핑 테스트하기
방금 OpenAI Compatible 엔드포인트를 생성했으니, 이제 이를 Python 개발 환경(예: VSCode)에 통합하여 시스템을 로컬 API Provider로 사용하는 방법을 살펴보겠습니다.

1. Python 가상 환경을 생성합니다:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Linux에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 venv를 생성합니다.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**사용자에게 GPU 장치에 대한 접근 권한을 부여합니다** (적용되려면 로그아웃 후 다시 로그인해야 합니다):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Linux에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 venv를 생성합니다.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    Windows에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 venv를 생성합니다.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **팁**: Windows 사용자는 일부 Powershell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다(예:
    > RemoteSigned 또는 Unrestricted로 설정).

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windows에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 venv를 생성합니다.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **팁**: Windows 사용자는 일부 Powershell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다(예:
    > RemoteSigned 또는 Unrestricted로 설정).

<!-- @device:end -->
<!-- @os:end -->

2. OpenAI 패키지를 설치합니다
    ```bash
    pip install openai
    ```

3. 방금 생성한 엔드포인트를 핑 테스트하려면 다음 스크립트를 실행합니다.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### (선택 사항): 런타임 간 전환하기

1. 키보드에서 `Ctrl + Shift + R`을 누릅니다. 또는 왼쪽의 `Discover` 탭(돋보기 아이콘)을 클릭한 다음 팝업에서 `Runtime`을 클릭합니다.
2. 그러면 `Runtime Selections`가 표시되며, 드롭다운 메뉴를 사용하여 런타임을 변경할 수 있습니다.


## 다음 단계

- **사용자 지정 앱 통합**: 로컬 OpenAI 호환 API를 사용하여 자체 Python 스크립트나 애플리케이션을 통합하세요.
- **고급 프런트엔드**: Open WebUI와 같은 강력한 인터페이스를 서버에 연결하여 채팅 기록과 페르소나 관리를 활용하세요.

더 많은 문서를 보려면 다음을 방문하세요: https://lmstudio.ai/docs/developer