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

이 플레이북은 AMD 하드웨어에서 Unsloth를 사용하여 로컬에서 언어 모델을 파인튜닝하는 방법을 보여줍니다.

`mlabonne/FineTome-100k` 데이터셋의 일부를 사용하여 `unsloth/gemma-4-E4B-it`에 LoRA 어댑터를 적용한 간단한 지도 미세 조정(Supervised Fine-Tuning, SFT) 예제를 사용합니다. 목표는 설정, 훈련, 추론, 파인튜닝된 결과 저장을 아우르는 간단한 엔드투엔드 워크플로를 제공하는 것입니다.

이 예제는 실용적이고 수정하기 쉽게 설계되었으므로, 여러분 자신의 데이터셋과 모델을 위한 출발점으로 활용할 수 있습니다.

## 배울 내용

- Unsloth 환경을 설정하는 방법
- Unsloth로 SFT를 사용하여 LLM을 파인튜닝하는 방법
- 파인튜닝된 결과를 로컬 스토리지에 저장하는 방법

<!-- @device:halo,stx,krk -->
> **참고:** 이 플레이북의 파인튜닝 기법은 최소 **64GB의 시스템 RAM**을 필요로 하며, 그중 최소 **24GB는 GPU에서 사용 가능**해야 합니다(이 24GB는 64GB의 일부이며, 별도로 추가되는 것이 아닙니다).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **참고:** 이 플레이북의 파인튜닝 기법은 최소 **총 24GB의 GPU 메모리**와 **32GB의 시스템 RAM**을 필요로 합니다.
> - Windows에서는 총 GPU 메모리가 그래픽 카드의 전용 VRAM과 공유 GPU 메모리(시스템 RAM에서 빌려온 메모리)를 합친 값입니다.
> - 따라서 전용 VRAM이 24GB 미만인 카드도 공유 GPU 메모리를 통해 부족분을 채워 이 플레이북을 실행할 수 있습니다.
<!-- @os:end -->

<!-- @os:linux -->
> **참고:** 이 플레이북의 파인튜닝 기법은 최소 **24GB의 전용 GPU 메모리**와 **32GB의 시스템 RAM**을 갖춘 그래픽 카드가 필요합니다.
> - Linux에서는 훈련이 전적으로 그래픽 카드의 전용 VRAM에서 실행됩니다.
> - VRAM이 부족할 때 공유 GPU 메모리(시스템 RAM)로 대체되지 않습니다.
> - 전용 VRAM이 24GB 미만인 카드는 시스템에 RAM이 충분하더라도 Linux에서 훈련 중 메모리 부족이 발생합니다.
<!-- @os:end -->
<!-- @device:end -->

## 왜 Unsloth인가?

Unsloth는 메모리 사용량을 줄이고 표준 설정 대비 훈련 속도를 높여 로컬 하드웨어에서 LLM 파인튜닝을 더 쉽게 실행할 수 있도록 해줍니다.

이 플레이북에서는 Unsloth를 **LoRA 기반 SFT**와 함께 사용합니다. 즉, 기본 모델은 대부분 고정된 상태로 유지되며, 훨씬 작은 어댑터 가중치 집합만 훈련됩니다. 이는 전체 파인튜닝보다 가볍고 반복 실험이 빠르기 때문에 로컬 개발 환경에 적합합니다.

Unsloth는 QLoRA 및 강화 학습 워크플로를 포함한 다른 훈련 방식도 지원합니다. 이 플레이북은 사용자가 실행하고, 이해하고, 확장할 수 있는 작은 LoRA 파인튜닝 예제라는 가장 단순한 경로에 먼저 초점을 맞춥니다.

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않다면 Ryzen AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

### 가상 환경 생성

<!-- @os:linux -->
<!-- @device:halo_box -->
터미널을 열고 AMD ROCm™ 소프트웨어와 PyTorch가 이미 설치된 venv를 생성합니다:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**사용자에게 GPU 장치 접근 권한 부여**(적용하려면 로그아웃 후 다시 로그인해야 합니다):

```bash
sudo usermod -aG render,video $LOGNAME
```

터미널을 열고 venv를 생성합니다:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **참고:** Windows에서는 Python 3.13이 필요합니다.

<!-- @device:halo_box -->
PowerShell 터미널을 열고 가상 환경을 생성합니다:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
PowerShell 터미널을 열고 가상 환경을 생성합니다:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### 기본 종속성 설치
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### 추가 종속성

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **참고:** 가져오기(import) 과정에서 Unsloth가 선택적 `bitsandbytes` 가속 경로를 탐색할 수 있습니다. 일부 ROCm 버전에서는 `bitsandbytes library load error: Configured ROCm binary not found`와 같은 메시지가 표시될 수 있습니다. 이 플레이북은 `optim="adamw_torch"`를 사용하는 표준 LoRA 파인튜닝을 사용하므로, `bitsandbytes` 옵티마이저나 4비트 QLoRA에 의존하지 않습니다. 이 메시지는 무시해도 안전합니다.

<!-- @os:windows -->
> **참고:** Windows ROCm에서는 Unsloth가 시작 시 여러 경고를 출력합니다 — 아래 [알려진 경고](#known-warnings) 항목을 참조하세요. 모두 무시해도 안전하며, 훈련은 정상적으로 동작합니다.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Unsloth 파인튜닝 스크립트 다운로드

각 단계를 수동으로 실행하는 대신, 이 플레이북은 여기 깔끔한 엔드투엔드 스크립트를 제공합니다: [test_unsloth.py](assets/test_unsloth.py).

다음 코드를 실행하여 스크립트를 실행합니다:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

이 플레이북의 나머지 부분에서는 개념적으로 스크립트의 각 주요 단계를 살펴봅니다.

## 작동 방식

test_unsloth.py 스크립트는 다음 단계를 수행합니다:
* **모델 로드**: FastModel을 사용하여 unsloth/gemma-4-E4B-it를 로드합니다.
* **데이터 준비**: 데이터셋(예: FineTome-100k)을 표준화하고 Gemma-4 채팅 템플릿을 적용합니다.
* **LoRA 적용**: 효율적인 훈련을 위해 언어, 어텐션, MLP 모듈에 어댑터를 추가합니다.
* **훈련**: 응답 전용 손실 마스킹을 적용한 SFTTrainer를 사용합니다.
* **추론**: 성능을 확인하기 위해 간단한 생성 테스트를 실행합니다.
* **저장**: LoRA 어댑터를 로컬에 내보냅니다.

## 주요 구성

실행을 사용자 지정하려면 다음 상수를 수정할 수 있습니다:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

모델 가중치를 로드할 때 표시되는 Unsloth 환영 메시지 및 출력 예시:

![alt text](assets/welcome.png)

## 데이터셋 준비

다음의 일부를 사용합니다:
```text
mlabonne/FineTome-100k
```
데이터셋은 다음과 같이 처리됩니다: 
* 채팅 형식으로 변환됨
* Gemma-4 채팅 템플릿을 사용하여 처리됨
* 중복된 BOS 토큰을 제거하도록 정리됨

## 모델 훈련

스크립트는 다음 매개변수로 짧은 훈련 데모를 실행합니다:
- 약 50 스텝
- 작은 배치 크기
- 그래디언트 누적

훈련 중에는 다음과 같은 로그가 표시됩니다:

![alt text](assets/training.png)


## 저장 및 배포
### 로컬 저장 (LoRA)

스크립트는 LoRA 어댑터를 OUTPUT_DIR에 자동으로 저장합니다.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### 병합된 모델 저장 (vLLM용) 

<!-- @os:windows -->
> **참고:** vLLM은 Windows를 지원하지 않습니다. 미세 조정된 모델을 Windows에 배포하려면 llama.cpp를 사용하거나(아래 [GGUF 내보내기](#export-gguf-for-llamacpp) 참조) 병합된 모델을 vLLM이 실행 중인 Linux 머신으로 전송하세요.
<!-- @os:end -->

<!-- @os:linux -->
vLLM으로 배포하려면 어댑터를 전체 모델로 병합하세요:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### GGUF 내보내기 (llama.cpp용)

로컬 추론을 위해 GGUF로 직접 변환합니다:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 알려진 경고

다음 경고는 Windows ROCm에서 Unsloth가 시작될 때 출력되며 모두 무시해도 안전합니다:

| 경고 | 원인 | 무시해도 안전한가? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes에는 Windows ROCm 빌드가 없음 | 예 — 이 플레이북은 bnb가 아닌 `adamw_torch`를 사용합니다 |
| `No ROCm platform found for torch.distributed` | Windows용 ROCm은 분산 학습을 지원하지 않음 | 예 — 단일 GPU 학습에는 영향이 없습니다 |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth가 Linux가 아닌 빌드를 표시함 | 예 — Windows ROCm은 단일 GPU SFT에서 작동합니다 |
| `triton is not available` | Triton에는 Windows 빌드가 없음 | 예 — Unsloth가 PyTorch 커널로 대체됩니다 |

이러한 경고에도 불구하고 학습은 정상적으로 진행됩니다.
<!-- @os:end -->

## 다음 단계
- Unsloth를 위한 직관적인 GUI인 [Unsloth Studio](https://unsloth.ai/docs/new/studio)를 사용해 보세요
- 사용자 고유의 데이터셋으로 학습해 보세요
- 다양한 하이퍼파라미터로 미세 조정을 시도해 보세요
- vLLM 또는 llama.cpp로 배포해 보세요
- 메모리 사용량을 줄이기 위해 QLoRA를 시도해 보세요

## 리소스

Unsloth 및 미세 조정에 대해 더 알아볼 수 있는 추가 리소스는 다음과 같습니다:

* [Unsloth 문서](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth 미세 조정 가이드](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)