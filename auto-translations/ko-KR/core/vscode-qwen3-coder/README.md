<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 이 플레이북은 최소 **32GB**의 시스템 메모리가 필요합니다.
<!-- @device:end -->

## 개요

코딩 에이전트는 대형 언어 모델(LLM)을 기반으로 하는 AI 에이전트와의 협업을 통해 개발자의 역량을 강화하는 강력한 도구입니다. 터미널이나 VS Code와 같은 개발 환경에 내장되어 개발자의 워크플로우에 원활하게 통합될 수 있습니다.

이 튜토리얼에서는 Cline, VS Code, LM Studio를 사용하여 로컬 머신에서 완전히 코딩 에이전트를 실행하는 방법을 설명합니다.

## 학습 내용

* 소프트웨어 엔지니어링 작업을 지원하기 위해 Cline 코딩 에이전트와 함께 VS Code를 실행하는 방법.
* 로컬 코딩 에이전트 추론을 위해 LM Studio와 통신하도록 Cline을 구성하는 방법.
* 실제 소프트웨어 엔지니어링 작업을 해결하기 위해 로컬 코딩 에이전트를 사용하는 방법.

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않은 경우 Ryzen AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치

<!-- @require:lmstudio,vscode -->

## LM Studio 실행 및 구성

코딩 에이전트를 구동하는 LLM을 제공하기 위해 LM Studio를 사용합니다.

- 검색창에서 `LM Studio`를 검색하고 애플리케이션을 실행합니다. 다음 페이지가 표시됩니다.

![LM Studio 초기 화면](assets/initial-lm-studio.png)

다음으로, 시스템에 LLM을 로드해야 합니다. 큰 컨텍스트 길이를 가진 `Qwen3-Coder-30B-A3B` 모델을 사용할 것입니다. (아직 설치하지 않은 경우 Model 탭을 사용하여 설치하세요).
- LM Studio 창 상단의 검색창을 클릭하거나 `CTRL+L`을 누릅니다. `Manually choose model load parameters` 스위치를 클릭한 다음 Qwen3-Coder-30B-A3B 모델을 클릭합니다.
- 컨텍스트 길이를 `4096`에서 `32768`로 변경하고, `GPU Offload`가 최대로 설정되어 있는지 확인합니다. 그런 다음 `Load Model`을 클릭합니다.

![모델 선택](assets/model-list-zoomed.png)

에이전트가 대규모 코드베이스를 처리하고 변경 사항을 기억할 수 있도록 큰 컨텍스트 길이를 사용합니다.

![모델 구성](assets/selecting-model-zoomed.png)

다음으로, LM Studio 서버를 활성화해야 합니다.
- 왼쪽의 Developer 탭을 클릭하거나 LM Studio에서 `CTRL+2`를 누릅니다.
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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Code 실행 및 구성

VS Code에 Cline 확장 프로그램을 설치하고 방금 만든 LM Studio 서버에 연결합니다.
- 검색창에서 `VS Code`를 검색하고 애플리케이션을 실행합니다.
- VS Code 왼쪽 열의 `Extensions` 아이콘을 클릭하고 `Cline`을 검색합니다. 그런 다음 `Install` 버튼을 클릭합니다.

![Cline 확장 프로그램 설치](assets/installing-cline-vscode-extension.png)

- 왼쪽에 Cline 아이콘이 표시됩니다. 해당 아이콘을 클릭하여 Cline을 엽니다. `How will you use Cline?`이라는 창이 나타납니다. LM Studio를 통해 실행되는 로컬 LLM을 사용할 것이므로 `Bring my own API Key`를 선택하고 `Continue`를 클릭합니다.

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

다음으로, 설정한 LM Studio 서버와 통신하도록 Cline을 구성해야 합니다.
- API Provider를 `LM Studio`로, 모델을 `Qwen3-Coder-30B-A3B-GGUF`로 설정합니다.

>**팁**: 더 최신 모델이 제공될 수 있습니다. 원하는 경우 Qwen3.6 모델을 다운로드하여 전환하는 것을 고려해 보세요.


![모델 구성](assets/cline-model-configuration-zoomed.png)

## 첫 번째 프로젝트 만들기

로컬 에이전트를 사용하여 웹사이트를 만들어 봅시다! Cline이 파일을 생성할 원하는 디렉토리로 VSCode를 엽니다.
- 이를 위해 VS Code 왼쪽 상단의 `File -> Open Folder`로 이동하여 `Documents`와 같은 폴더를 선택합니다.

![VS Code 빈 폴더](assets/open-cline-test.png)

이제 로컬 코딩 에이전트에 프롬프트를 입력할 준비가 되었습니다.
- 왼쪽 열의 Cline 확장 프로그램을 클릭하고 에이전트를 시작할 프롬프트를 입력합니다. 예시로 다음 프롬프트를 사용해 봅시다:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

그러면 에이전트가 프롬프트에 따라 파일을 생성하기 시작합니다. 사용자는 아래와 같이 VS Code에서 코드가 생성되는 것을 확인할 수 있습니다. Cline이 파일을 생성할 때마다 `Save`를 클릭해야 할 수 있습니다.

![Cline 코드 생성](assets/cline-code-generation.png)

소프트웨어 생성이 완료되면 에이전트가 완료되고 애플리케이션을 실행할 수 있습니다. 이 경우 에이전트는 `index.html`, `script.js`, `styles.css` 세 개의 파일을 작성했습니다. HTML 파일을 더블 클릭하기만 하면 생성된 웹사이트를 로드하고 상호작용할 수 있습니다.

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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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

웹사이트를 생성한 후에도 Cline과 계속 협력하여 웹사이트를 개선할 수 있습니다. 가능한 두 가지 개선 사항은 다음과 같습니다:

- **문서화**: 에이전트에게 `Add a README`라고 프롬프트를 입력하기만 하면 에이전트가 웹사이트를 문서화하는 `README.md` 파일을 생성합니다.
- **애니메이션**: 모델에게 `Add an animation that visually represents a large language model running on a laptop.`이라고 프롬프트를 입력하여 웹사이트에 애니메이션을 추가합니다.

이 설정을 사용하여 다른 애플리케이션을 생성해 보시기 바랍니다. 아래는 저희가 시도해 본 몇 가지 재미있는 예시입니다:

- **레트로 아케이드 게임**: 다른 프롬프트도 시도해 보세요. 에이전트가 다음 프롬프트를 사용하여 `PyGame` 패키지로 Python에서 레트로 스타일 게임을 만드는 것도 재미있을 수 있습니다:

```code
Create a simple pong game using the PyGame python package.
```

- **데이터 분석**: 코딩 에이전트가 특히 유용한 분야 중 하나는 스크립팅과 데이터 분석입니다. 다음은 주가 시각화를 위한 데이터 분석 소프트웨어를 생성하는 로컬 모델의 능력을 보여주는 프롬프트입니다:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## 리소스

코딩 에이전트, Cline 및 워크로드 실행에 대해 자세히 알아볼 수 있는 추가 리소스는 다음과 같습니다.

* AMD LM Studio 파트너십 및 통합에 대한 자세한 정보: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AI 및 Radeon™ 그래픽 카드에서 Cline을 실행하는 방법을 안내하는 AMD 블로그: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC에서 로컬로 코딩 에이전트를 실행하는 방법에 관한 Cline 블로그: https://cline.bot/blog/local-models-amd