<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

## 개요

AMD ROCm™ 소프트웨어와 PyTorch 스택은 온디바이스 AI를 위한 통합 에코시스템을 구성합니다. Ryzen™ AI APU 및 Radeon™ GPU를 포함한 다양한 디바이스를 공식 지원하며 Windows와 Linux 모두에서 작동합니다.

이 플레이북에서는 엣지에서 완전히 실행되는 저지연, 표현력 있는, 프라이빗 음성-음성 번역을 구현하는 방법을 배웁니다.

## 학습 내용

- 음성-음성 환경 설정 방법
- 음성-음성 모델을 로드하고 사용하는 Python 코드 작성 방법
- Gradio UI 실행 및 실험 방법

## 실시간 음성-음성 번역을 사용하는 이유

- 번역과 언어 장벽 사이의 마찰 제거
- 어색한 멈춤 없이 어조, 감정, 의도 전달
- 글로벌 협업 및 빠른 의사결정 지원

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않은 경우 Ryzen AI Developer Center에서 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치

### 가상 환경 생성

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux에서 터미널을 열고 다음 명령을 실행하여 ROCm+Pytorch가 이미 설치된 venv를 생성합니다:

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPU 디바이스에 대한 사용자 액세스 권한 부여** (적용하려면 로그아웃 후 다시 로그인하세요):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux에서 터미널을 열고 다음 명령을 실행하여 venv를 생성합니다:

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
Windows에서 원하는 디렉터리에 터미널을 열고 다음 명령을 따라 ROCm+Pytorch가 이미 설치된 venv를 생성합니다:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **팁**: Windows 사용자는 일부 PowerShell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다 (예:
> RemoteSigned 또는 Unrestricted로 설정).

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows에서 원하는 디렉터리에 터미널을 열고 다음 명령을 따라 venv를 생성합니다:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **팁**: Windows 사용자는 일부 PowerShell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다 (예:
> RemoteSigned 또는 Unrestricted로 설정).

<!-- @device:end -->
<!-- @os:end -->

### 기본 종속성 설치

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### 추가 종속성

pip을 사용하여 m4t 종속성을 설치합니다:
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=300 setup=activate-venv hidden=True -->
```python
import importlib
import os
import sys

# Ensure local assets directory is importable
sys.path.insert(0, os.getcwd())

modules = [
    "torch",
    "torchaudio",
    "scipy",
    "soundfile",
    "gradio",
    "transformers",
    "safetensors",
    "sentencepiece",
    "accelerate",
    "tiktoken",
]

for module in modules:
    importlib.import_module(module)
    print(f"PASS: imported {module}")

from transformers import AutoProcessor, SeamlessM4Tv2Model
import lang_list
from lang_list import LANGUAGE_NAME_TO_CODE, ASR_TARGET_LANGUAGE_NAMES, S2ST_TARGET_LANGUAGE_NAMES

assert "English" in LANGUAGE_NAME_TO_CODE, "FAIL: English missing in LANGUAGE_NAME_TO_CODE"
assert len(S2ST_TARGET_LANGUAGE_NAMES) > 0, "FAIL: S2ST_TARGET_LANGUAGE_NAMES is empty"

print("PASS: imported local module lang_list")
print("PASS: key speech2speech imports work")
```
<!-- @test:end -->

<!-- @test:id=verify-scripts timeout=60 hidden=True -->
```python
import ast
import os
import sys

required_files = [
    "infer.py",
    "gradio_demo.py",
    "lang_list.py",
    "input1.wav",
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: All required files exist")

for script in ["infer.py", "gradio_demo.py", "lang_list.py"]:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->


## 음성-음성 데모 설정

#### seamless-m4t-v2에 대해 알아보기

자세한 내용은 Hugging Face의 [모델 카드](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main)를 확인하세요.
다음은 음성-음성 모델의 기술 아키텍처입니다:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### 스크립트 다운로드

이 플레이북에는 바로 사용할 수 있는 스크립트가 포함되어 있습니다. 생성한 환경과 동일한 디렉터리에 모두 다운로드하세요.

| 스크립트 | 설명 | 사용법 |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | 기본 LLM 텍스트 생성 | `python infer.py` |
| [input1.wav](assets/input1.wav) | 예제 오디오 파일 | N/A |
| [lang_list.py](assets/lang_list.py) | 언어 지원 파일 | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | 음성 번역을 위한 직관적인 UI | `python gradio_demo.py --no-share` |


### infer.py 시작하기

스크립트를 실행하려면 
```bash
python infer.py
```
> **참고**: 일부 경고가 표시될 수 있습니다. 이는 정상적인 동작입니다.
 
  
#### 코드 설명
**스니펫 1: 필요한 종속성 가져오기**

```python 
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"

import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio

from transformers import AutoProcessor, SeamlessM4Tv2Model

# ============ Configuration ============
DEFAULT_TARGET_LANGUAGE = "eng"

INPUT_AUDIO_PATH = "./input1.wav"
OUTPUT_AUDIO_PATH = "./out1.wav"

# Automatically downloads + caches via Hugging Face
MODEL_ID = "facebook/seamless-m4t-v2-large"

TARGET_SAMPLE_RATE = 16_000
```

**스니펫 2: HuggingFace에서 모델 로드**

이 함수는 모델 ID를 입력받아 아직 다운로드되지 않은 경우 모델을 다운로드합니다. 그런 다음 다음 함수에서 사용할 프로세서와 모델을 반환합니다.
```python
def load_model(model_id: str, device: torch.device):
    start = time.time()

    print("Loading model (downloads automatically on first run)...")

    processor = AutoProcessor.from_pretrained(model_id)

    dtype = torch.float16 if device.type == "cuda" else torch.float32

    model = SeamlessM4Tv2Model.from_pretrained(model_id, torch_dtype=dtype).to(device)

    elapsed = time.time() - start
    print(f"Model loading duration: {elapsed:.2f} seconds")

    return processor, model
```

**스니펫 3: 입력 오디오 클립 .wav 파일 로드 및 전처리**

이 함수는 오디오 클립을 로드하고 대상 샘플링 레이트로 리샘플링합니다.
```python
def preprocess_audio(audio_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> torch.Tensor:

    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)

    # Convert to tensor [channels, samples]
    audio = torch.from_numpy(audio_np.T)

    # Resample if needed
    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)

    # Convert stereo -> mono
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    return audio
```

**스니펫 4: 추론 실행**

이 함수는 모델로 추론을 실행하고 생성된 출력을 반환합니다.
```python
def run_inference(model, processor, audio: torch.Tensor, device: torch.device, target_lang: str = DEFAULT_TARGET_LANGUAGE):

    start = time.time()

    audio_inputs = processor(
        audio=audio.squeeze(0).cpu().numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    audio_inputs = {
        k: v.to(device) if isinstance(v, torch.Tensor) else v
        for k, v in audio_inputs.items()
    }

    with torch.inference_mode():
        output = model.generate(**audio_inputs, tgt_lang=target_lang)[0]

    audio_array = output.float().cpu().numpy().squeeze()

    elapsed = time.time() - start
    print(f"Inference duration: {elapsed:.2f} seconds")

    return audio_array, elapsed
```

**스니펫 5: 번역된 파일 저장**

이 함수는 오디오 배열을 .WAV 파일로 저장합니다. 
```python
def save_audio(audio_array: np.ndarray, output_path: str, sample_rate: int):
    if np.issubdtype(audio_array.dtype, np.floating):
        max_abs = np.max(np.abs(audio_array)) if audio_array.size else 0.0

        if max_abs > 1.0:
            audio_array = audio_array / max_abs

        audio_array = (audio_array * 32767.0).clip(-32768, 32767).astype(np.int16)

    scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

    print(f"Output saved to: {output_path}")
```

<!-- @os:windows -->
<!-- @test:id=infer-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
Remove-Item .\out1.wav -Force -ErrorAction SilentlyContinue

if (-not (Test-Path .\input1.wav)) { throw "FAIL: input1.wav not found in current directory" }

python .\infer.py
if ($LASTEXITCODE -ne 0) { throw "infer.py failed" }

if (-not (Test-Path .\out1.wav)) { throw "FAIL: out1.wav was not created" }
$file = Get-Item .\out1.wav
if ($file.Length -le 0) { throw "FAIL: out1.wav is empty" }

Write-Host "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=infer-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail
rm -f ./out1.wav

if [ ! -f ./input1.wav ]; then
  echo "FAIL: input1.wav not found in current directory"
  exit 1
fi

python ./infer.py

if [ ! -f ./out1.wav ]; then
  echo "FAIL: out1.wav was not created"
  exit 1
fi
if [ ! -s ./out1.wav ]; then
  echo "FAIL: out1.wav is empty"
  exit 1
fi

echo "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

### Gradio UI 데모 실행:

기본 스크립트 예제를 실행했으므로, 이제 작성한 코드를 기반으로 구축된 유용한 UI를 통해 실시간 음성-음성 번역을 쉽게 수행할 수 있습니다.

#### Gradio 로컬 실행

```bash
python ./gradio_demo.py --no-share
```
그런 다음 웹 브라우저에서 `http://127.0.0.1:7860`을 열어 UI에 접속합니다.


### Gradio UI 예시:

<p align="center">
  <img src="assets/gradio.png" alt="gradio UI" width="600"/>
</p>

<!-- @os:windows -->
<!-- @test:id=gradio-ui-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
'@

$tempPy = Join-Path $env:TEMP "gradio_ui_smoke_ci.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy

if ($LASTEXITCODE -ne 0) {
  Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
  throw "gradio UI smoke test failed"
}

Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=gradio-ui-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail

python - <<'PY'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
PY
```
<!-- @test:end --> 
<!-- @os:end -->


## 다음 단계

- 수십 가지 언어 간에 자유롭게 조합하여 빠른 번역을 수행하세요.
- 데모를 다른 사람과 공유하세요: --share를 추가하여 누구나 원격으로 접속할 수 있는 공개 링크를 생성하거나, Hugging Face Spaces를 사용하여 영구적으로 배포하세요.

## 리소스

음성-음성 번역에 대해 더 알아볼 수 있는 추가 리소스입니다:  
* 저장소는 여기에 있습니다 https://huggingface.co/facebook/seamless-m4t-v2-large 
* "Seamless: Multilingual Expressive and Streaming Speech Translation"과 관련된 연구 학술 자료
* Gradio 공유 및 배포: [앱 공유 가이드](https://www.gradio.app/guides/sharing-your-app) 및 [Hugging Face Spaces에 배포](https://shafiqulai.github.io/blogs/blog_5.html)