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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 이 플레이북에는 최소 **32GB**의 시스템 메모리가 필요합니다.
<!-- @device:end -->

## 개요

코딩 에이전트는 대규모 언어 모델(LLM)을 기반으로 한 AI 에이전트와의 협업을 통해 개발자에게 힘을 실어주는 강력한 도구입니다. 이러한 에이전트는 터미널이나 VS Code와 같은 개발 환경에 내장될 수 있어 개발자의 워크플로에 원활하게 통합됩니다.

이 튜토리얼에서는 Cline, VS Code, LM Studio를 사용하여 코딩 에이전트를 로컬 머신에서 완전히 실행하는 방법을 설명합니다.

## 학습 내용

* 소프트웨어 엔지니어링 작업을 지원하기 위해 Cline 코딩 에이전트와 함께 VS Code를 실행하는 방법
* LM Studio와 통신하여 코딩 에이전트를 로컬로 추론하도록 Cline을 구성하는 방법
* 로컬 코딩 에이전트를 사용하여 실제 소프트웨어 엔지니어링 작업을 해결하는 방법

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않은 경우 Ryzen AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

<!-- @require:lmstudio,vscode -->

## LM Studio 실행 및 구성

코딩 에이전트를 구동하는 LLM을 서비스하기 위해 LM Studio를 사용합니다.

- 검색 창에서 `LM Studio`를 검색하여 애플리케이션을 실행합니다. 다음과 같은 화면이 표시됩니다.

![LM Studio 초기 화면](assets/initial-lm-studio.png)

다음으로 시스템에 LLM을 로드해야 합니다. 여기서는 컨텍스트 길이가 큰 `Qwen3-Coder-30B-A3B` 모델을 사용합니다. (아직 설치하지 않았다면 Model 탭을 사용하여 설치하세요.)
- LM Studio 창 상단의 검색 창을 클릭하거나 `CTRL+L`을 누릅니다. `Manually choose model load parameters` 스위치를 클릭한 다음 Qwen3-Coder-30B-A3B 모델을 클릭합니다.
- 컨텍스트 길이를 `4096`에서 `32768`로 변경하고 `GPU Offload`가 최대값으로 설정되어 있는지 확인합니다. 그런 다음 `Load Model`을 클릭합니다.

![모델 선택](assets/model-list-zoomed.png)

에이전트가 대규모 코드베이스를 처리하고 변경 사항을 기억할 수 있도록 큰 컨텍스트 길이를 사용합니다.

![모델 구성](assets/selecting-model-zoomed.png)

다음으로 LM Studio 서버를 활성화해야 합니다.
- LM Studio 왼쪽에서 Developer 탭을 클릭하거나 `CTRL+2`를 누릅니다.
- 상태 토글을 확인하고 `Running`으로 설정되어 있는지 확인합니다.

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

![서버 상태](assets/lm-studio-server-status.png)

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Code 실행 및 구성

방금 만든 LM Studio 서버에 연결하기 위해 VS Code에 Cline 확장을 설치합니다.
- 검색 창에서 `VS Code`를 검색하여 애플리케이션을 실행합니다.
- VS Code 왼쪽 열에서 `Extensions` 아이콘을 클릭하고 `Cline`을 검색합니다. 그런 다음 `Install` 버튼을 클릭합니다.

![Cline 확장 설치](assets/installing-cline-vscode-extension.png)

- 왼쪽에 Cline 아이콘이 표시됩니다. 이를 클릭하여 Cline을 엽니다. `How will you use Cline?`이라는 창이 나타납니다. 여기서는 LM Studio를 통해 실행되는 로컬 LLM을 사용할 것이므로 `Bring my own API Key`를 선택하고 `Continue`를 클릭합니다.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![계정 생성](assets/cline-how-will-you-use-cline-zoomed.png)

다음으로 설정한 LM Studio 서버와 통신하도록 Cline을 구성해야 합니다.
- API Provider를 `LM Studio`로, 모델을 `Qwen3-Coder-30B-A3B-GGUF`로 설정합니다.

>**팁**: 더 새로운 모델을 사용할 수 있는 경우도 있습니다. 원한다면 Qwen3.6 모델을 다운로드하여 전환하는 것도 고려해 보세요.


![모델 구성](assets/cline-model-configuration-zoomed.png)

## 첫 번째 프로젝트 만들기

로컬 에이전트를 사용하여 웹사이트를 만들어 봅시다! Cline이 파일을 생성할 원하는 디렉터리로 VS Code를 엽니다.
- 이를 위해 VS Code 왼쪽 상단의 `File -> Open Folder`로 이동하여 `Documents`와 같은 폴더를 선택합니다.

![비어 있는 VS Code 폴더](assets/open-cline-test.png)

이제 로컬 코딩 에이전트에 프롬프트를 입력할 준비가 되었습니다.
- 왼쪽 열에서 Cline 확장을 클릭하고 에이전트를 시작할 프롬프트를 입력합니다. 예를 들어 다음 프롬프트를 사용해 보겠습니다:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

그러면 에이전트가 프롬프트에 따라 파일을 생성하기 시작합니다. 사용자는 아래와 같이 VS Code에서 코드가 생성되는 과정을 지켜볼 수 있습니다. Cline이 파일을 생성하려 할 때마다 `Save`를 클릭해야 할 수도 있습니다.

![Cline 코드 생성](assets/cline-code-generation.png)

소프트웨어 생성이 끝나면 에이전트 작업이 완료되고 애플리케이션을 실행할 수 있습니다. 이 경우 에이전트는 `index.html`, `script.js`, `styles.css` 세 개의 파일을 작성했습니다. HTML 파일을 더블클릭하기만 하면 생성된 웹사이트를 로드하고 상호작용할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
## 다음 단계

웹사이트를 생성한 후에도 Cline과 계속 작업하여 웹사이트를 개선할 수 있습니다. 가능한 두 가지 개선 사항은 다음과 같습니다.

- **문서화**: 에이전트에게 `Add a README`라는 프롬프트를 입력하기만 하면 에이전트가 웹사이트를 문서화하는 `README.md` 파일을 생성합니다.
- **애니메이션**: `Add an animation that visually represents a large language model running on a laptop.`라는 프롬프트를 모델에 입력하면 웹사이트에 애니메이션이 생성됩니다.

이 설정을 사용하여 다른 애플리케이션을 생성해 보는 것을 권장합니다. 아래는 저희가 시도해 본 몇 가지 재미있는 예시입니다.

- **레트로 아케이드 게임**: 다른 프롬프트도 시도해 보세요. 다음 프롬프트를 사용하여 `PyGame` 패키지로 Python에서 레트로 스타일 게임을 만들도록 에이전트에게 요청하는 것도 재미있을 수 있습니다.

```code
Create a simple pong game using the PyGame python package.
```

- **데이터 분석**: 코딩 에이전트가 특히 유용한 분야 중 하나는 스크립팅 및 데이터 분석입니다. 다음은 로컬 모델이 주가 시각화를 위한 데이터 분석 소프트웨어를 생성하는 능력을 보여주는 프롬프트입니다.

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## 리소스

아래는 코딩 에이전트, Cline, 그리고 다음에서 워크로드를 실행하는 방법에 대해 더 알아볼 수 있는 추가 리소스입니다.

* AMD LM Studio 파트너십 및 통합에 대한 자세한 정보: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AI 및 Radeon™ 그래픽 카드에서 Cline을 실행하는 방법을 다루는 AMD 블로그: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC에서 로컬로 코딩 에이전트를 실행하는 방법에 대한 Cline 블로그: https://cline.bot/blog/local-models-amd