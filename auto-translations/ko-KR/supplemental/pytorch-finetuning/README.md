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

이 튜토리얼에서는 PyTorch와 ROCm을 사용하여 대규모 언어 모델(LLM)을 파인튜닝하는 단계별 예제를 제공합니다. 표준 파인튜닝부터 메모리 효율적인 매개변수 효율적 파인튜닝(PEFT) 전략에 이르기까지 다양한 기법을 다루므로, 필요에 맞게 모델을 손쉽게 조정할 수 있습니다.

**사용된 모델**: google/gemma-3-4b-it  *(게이트가 걸린 모델인 경우 [HF 인증 활성화](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) 참고)*  
**하드웨어**: ROCm을 지원하는 AMD Radeon™ GPU  
**프레임워크**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **참고:** 
> - 전체 파인튜닝을 수행하려면 최소 **64GB의 시스템 RAM**이 필요하며, 그중 최소 **32GB는 GPU에서 사용 가능**해야 합니다(이 32GB는 64GB에 포함된 것이며, 별도로 추가되는 것이 아닙니다).
> - 제공된 학습 스크립트에서 모델을 교체하여 **GPT-OSS-20B**를 비롯한 다른 모델 아키텍처도 시도해 볼 수 있습니다.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **참고:** LoRA 및 QLoRA 파인튜닝을 수행하려면 최소 **32GB의 시스템 RAM**이 필요하며, 그중 최소 **16GB는 GPU에서 사용 가능**해야 합니다(이 16GB는 32GB에 포함된 것이며, 별도로 추가되는 것이 아닙니다).
<!-- @os:end -->

<!-- @os:windows -->
> **참고:** LoRA 파인튜닝을 수행하려면 최소 **32GB의 시스템 RAM**이 필요하며, 그중 최소 **16GB는 GPU에서 사용 가능**해야 합니다(이 16GB는 32GB에 포함된 것이며, 별도로 추가되는 것이 아닙니다).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **참고:** LoRA 및 QLoRA 파인튜닝을 수행하려면 전용 GPU 메모리가 최소 **16GB**이고 시스템 RAM이 최소 **32GB**인 그래픽 카드가 필요합니다.
> - Linux에서는 학습이 전적으로 그래픽 카드의 전용 VRAM에서 실행됩니다.
> - VRAM이 부족해져도 공유 GPU 메모리(시스템 RAM)로 대체되지 않습니다.
> - 전용 VRAM이 16GB 미만인 카드는 시스템에 RAM이 충분하더라도 Linux에서 학습 도중 메모리 부족이 발생합니다.
<!-- @os:end -->

<!-- @os:windows -->
> **참고:** LoRA 파인튜닝을 수행하려면 전체 GPU 메모리가 최소 **16GB**이고 시스템 RAM이 최소 **32GB**여야 합니다.
> - Windows에서는 전체 GPU 메모리가 그래픽 카드의 전용 VRAM과 공유 GPU 메모리(시스템 RAM에서 빌려온 메모리)를 합산한 값입니다.
> - 따라서 전용 VRAM이 16GB 미만인 카드도 공유 GPU 메모리로 부족분을 보충하여 이 플레이북을 실행할 수 있습니다.
<!-- @os:end -->
<!-- @device:end -->

## 학습 내용

- PyTorch와 ROCm을 사용하여 LoRA, QLoRA, 전체 파인튜닝으로 LLM을 파인튜닝하는 방법
- 파인튜닝된 모델을 저장하고 배포하는 방법
- 학습을 모니터링하고 일반적인 문제를 디버깅하는 방법

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않다면 Ryzen AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

#### 가상 환경 만들기

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**사용자에게 GPU 장치 접근 권한 부여**(적용하려면 로그아웃 후 다시 로그인해야 합니다):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### 기본 종속성 설치
<!-- @require:pytorch -->

#### 추가 종속성

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** 여기서는 핵심 패키지만 테스트 및 지원됩니다. **bitsandbytes는 Windows에서 제대로 지원되지 않으므로** Windows 설치에는 이를 포함하지 않으며, Windows에서는 LoRA 또는 전체 파인튜닝을 사용하세요(QLoRA는 bitsandbytes가 필요하며 Linux용으로 설계되었습니다).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF 인증 활성화(게이트가 걸린 모델 또는 사전 설치되지 않은 사용자 지정 모델)

이 예제에서는 **게이트가 걸린(gated)** 모델인 **google/gemma-3-4b-it**를 사용합니다. Hugging Face에서 모델의 이용 약관에 동의한 다음 인증을 완료해야 학습 스크립트가 이 모델을 다운로드할 수 있습니다.

1. **라이선스 동의:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)를 열어 로그인(또는 계정 생성)한 후 모델 페이지에서 라이선스/이용 약관에 동의하세요(예: "Agree and access repository").
2. **설치 및 로그인:** Hugging Face CLI를 설치한 다음 표준 로그인을 실행합니다:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## 기법 이해하기

### LoRA란 무엇인가?

**LoRA(Low-Rank Adaptation)**는 기본 모델을 고정한 상태로 두고, 특정 레이어에 추가되는 작은 "어댑터" 행렬만 학습합니다.

- **핵심 아이디어**: 수백만 개의 매개변수를 가진 거대한 가중치 행렬을 업데이트하는 대신, 저순위 업데이트(곱했을 때 매개변수가 훨씬 적은 두 개의 작은 행렬)를 학습합니다. 이를 통해 학습 가능한 매개변수와 VRAM을 크게 줄이면서도 전체 파인튜닝 품질의 대부분을 유지할 수 있습니다.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRA란 무엇인가?

**QLoRA**는 **4비트 양자화**와 **LoRA**를 결합합니다. 기본 모델은 4비트로 로드되어(메모리를 크게 절약) LoRA 어댑터만 더 높은 정밀도로 학습됩니다. 따라서 LoRA의 매개변수 효율성과 훨씬 낮은 VRAM 사용량을 동시에 얻을 수 있으며, 전체 정밀도 LoRA에 비해 품질 면에서 약간의 손해를 감수해야 합니다. 4비트 양자화는 수치적 불안정성(손실 급등이나 NaN)을 유발할 수 있으므로, VRAM이 충분하다면 사용자는 **LoRA**를 선호하는 경우가 많습니다.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **참고**: `openai/gpt-oss-20b`와 같은 MXFP4 기본 모델의 경우, QLoRA 대신 **LoRA**(`train_lora.py`)를 사용하는 것이 좋습니다. QLoRA 스크립트의 `bitsandbytes` 4비트 경로는 일반적으로 MXFP4 가중치를 BF16으로 역양자화하므로, 실행 결과가 표준 LoRA와 동일하게 동작합니다. 네이티브 MXFP4를 사용하려면 소스에서 빌드한 `bitsandbytes`와 그에 맞는 Transformers/Triton/kernels 스택이 필요합니다. 자세한 내용은 [Transformers MXFP4 문서](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)를 참고하세요.

---
### 2. 학습 방법 선택

| 방법 | 메모리 | 속도 | 품질 | 최적 용도 |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux 전용) | 12-16GB | 가장 빠름 | 90-95% | 낮은 메모리 사용량 |
| **LoRA** | 24-32GB | 빠름 | 95-98% | 균형 잡힌 접근 방식 |
| **Full** | 80GB+ | 가장 느림 | 100% | 최고 품질 |

### 3. 학습 실행

**데이터셋 및 모델이 학습하는 내용**  
스크립트는 데이터셋을 채팅 예제로 변환합니다. 예를 들어, QLoRA 스크립트는 **Abirate/english_quotes**를 사용하며, 각 예제는 다음과 같은 사용자-어시스턴트 쌍이 됩니다:

- **사용자:** “Give me a quote about: &lt;tag&gt;”
- **어시스턴트:** “&lt;quote&gt; – &lt;author&gt;”

파인튜닝은 모델이 특정 주제에 대한 명언을 요청하는 프롬프트에 응답하고 이를 `<quote text> - <author>` 형식으로 반환하도록 학습시킵니다. LoRA 및 전체 파인튜닝 스크립트는 **databricks/databricks-dolly-15k**(일반적인 지시/응답 쌍)를 사용하므로 정확한 작업은 스크립트마다 다르지만, 아이디어는 동일합니다 - 선택한 데이터셋과 형식에 맞게 모델을 적응시키는 것입니다.

아래는 사용 가능한 학습 방법에 대한 요약입니다. 각 방법은 해당 스크립트로 연결되며, 올바른 접근 방식을 선택할 수 있도록 간단한 설명을 제공합니다.

| 스크립트                           | 방법            | 설명                                                                                                         | 일반적인 VRAM | 권장 대상                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | 기본 모델을 고정한 상태로 작은 어댑터 행렬을 학습합니다. 3~5배 더 빠르며 전체 품질의 약 95~98%를 유지합니다.                         | 24–32GB      | 고급 사용자; 다중 어댑터; 더 많은 VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux 전용)*             | **QLoRA**       | 4비트 양자화 + LoRA 어댑터. 가장 낮은 메모리 사용량과 가장 빠른 속도, 약간의 품질 저하가 있습니다. `bitsandbytes`가 필요합니다(Linux 전용).                            | 12–16GB      | 대부분의 사용자; 빠른 실험; 제한된 VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **전체 파인튜닝** | 모든 모델 파라미터를 업데이트합니다. 최고 품질이지만 메모리와 연산량이 가장 많이 필요합니다.                                    | 40GB+        | 최고 품질; 연구; 대용량 VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **참고:** 전체 파인튜닝(`train_full_finetuning.py`)은 64GB 이상의 시스템 RAM이 필요할 수 있으며, 이 장치에서는 실행이 불가능할 수 있습니다. 대신 LoRA 또는 QLoRA 사용을 고려하세요.
<!-- @os:end -->

<!-- @os:windows -->
> **참고:** 전체 파인튜닝(`train_full_finetuning.py`)은 64GB 이상의 시스템 RAM이 필요할 수 있으며, 이 장치에서는 실행이 불가능할 수 있습니다. 대신 LoRA 사용을 고려하세요.
<!-- @os:end -->
<!-- @device:end -->

원하는 `Training method`를 선택하고 해당 스크립트를 다운로드한 후, 가상 환경을 활성화한 상태에서 다음 명령어로 실행하기만 하면 됩니다:

```python
python3 train_<method_name>.py.
```

## 파인튜닝된 모델 사용하기

### 전체 파인튜닝 이후

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA/QLoRA 학습 이후

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA 어댑터를 기본 모델에 병합하기

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**참고:**  
- 모델 디렉터리 이름(`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`)이 학습 결과로 생성된 실제 출력 폴더와 일치하는지 확인하세요.  
- QLoRA 대신 LoRA를 사용한 경우, 경로만 그에 맞게 바꿔주면 됩니다.  
- 일부 Gemma 모델은 `from_pretrained`에서 `trust_remote_code=True`를 지정해야 할 수 있습니다. 관련 경고가 표시되면 추가하세요.

패딩 토큰, 장치 등 더 많은 사용자 지정 설정은 학습에 사용한 스크립트를 참조하세요.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## 사용자 지정 가이드

### 자체 데이터셋 사용하기

모든 스크립트는 동일한 데이터셋 형식을 사용합니다. 로딩 섹션을 다음과 같이 교체하세요:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**로컬 JSON/JSONL 파일용 데이터셋 형식:**

이 방법을 사용할 때는 파싱 오류를 방지하기 위해 JSON 파일이 올바르게 구성되어 있는지 확인하세요.

다음 지침을 반드시 준수해야 합니다:
* **파일 형식:** JSON 파일은 올바른 구조와 문법을 보장하기 위해 통합 개발 환경(IDE)에서 형식을 지정해야 합니다.
* **필수 키:** 사용자 지정 JSON 파일에는 `instruction`과 `response` 키가 포함되어야 합니다. 이 키들은 해당 방법이 올바르게 작동하는 데 필수적입니다.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Hugging Face Hub 데이터셋용 데이터셋 형식**

Hugging Face의 데이터셋을 사용할 때는 원활한 통합을 위해 데이터셋이 올바르게 구성되어 있는지 확인하세요.

다음 지침을 따라야 합니다:
* **지시-응답 쌍:** `instruction-response` 쌍이 포함된 데이터셋에 집중하세요. 이 구조는 의도된 기능을 위해 필수적입니다.
* **사용자 지정 키 수정:** 데이터셋이 `instruction-response` 구조를 따르지 않는 경우, `format_instruction()` 함수를 수정하는 옵션이 있습니다. 이를 통해 필요한 특정 키를 반영할 수 있습니다.

조정 예시: 데이터셋의 출력을 조정해야 하는 경우, format_instruction() 함수 내의 응답 섹션을 요구 사항에 맞게 수정할 수 있습니다.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSV 파일용 데이터셋 형식**

CSV 파일 형식을 사용하는 스크립트를 사용하려면 CSV 파일에 `instruction`과 `response`라는 이름의 열이 포함되어 있는지 확인해야 합니다.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### 학습 파라미터 조정하기

학습 스크립트를 편집하여 목표에 맞게 변수를 변경하세요: **학습률**(`LR`), **에포크**(`EPOCHS`), **배치 크기**(`BATCH_SIZE`), **그레이디언트 누적**(`GRAD_ACCUM_STEPS`), 그리고 LoRA/QLoRA의 경우 **랭크**(`LORA_R`)입니다. 더 빠른 실행을 원한다면 에포크 수를 줄이고 학습률(LR)을 높이세요. 더 나은 품질을 원한다면 에포크 수를 늘리고 LR을 낮추세요. 메모리 부족 오류가 발생하면 배치 크기나 시퀀스 길이를 줄이세요.
### 메모리 최적화 팁

메모리 부족 오류가 발생하는 경우:

**1. 배치 크기 줄이기:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. 시퀀스 길이 줄이기:**
```python
max_seq_length=256  # Instead of 512
```

**3. 더 적극적인 양자화 사용:**
```
Full → LoRA → QLoRA
```

**4. 그래디언트 체크포인팅 활성화(전체 파인튜닝에만 해당):**
```python
model.gradient_checkpointing_enable()
```

---

## 모니터링 및 디버깅

### GPU 메모리 확인

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (선택 사항) Weights & Biases로 실험 추적하기

[Weights & Biases](https://wandb.ai)에 실행 및 메트릭을 기록하려면:

```bash
pip install wandb
wandb login
```

학습 스크립트에서 트레이너 설정에 `report_to="wandb"`를 설정하고, 필요하다면 `run_name="your-experiment-name"`도 함께 설정하세요. Wandb를 사용하지 않으려면 `report_to`를 기본값으로 두거나 `"none"`으로 설정하세요.

### 일반적인 문제

#### 메모리 부족(OOM)

**해결 방법:** 배치 크기를 줄이거나 QLoRA를 사용하세요
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### 손실이 감소하지 않는 경우

**해결 방법:** 학습률을 조정하세요
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### 느린 학습 속도

**해결 방법:** 메모리 여유가 있다면 배치 크기를 늘리세요
```python
BATCH_SIZE = 8
```
## 다음 단계

성공적으로 파인튜닝을 완료한 후에는 모델을 더욱 효과적으로 활용하기 위해 다음 단계를 고려해 보세요:

1. **평가**: 보류된 테스트 데이터로 철저히 평가하여 일반화 성능을 측정하고 과적합을 방지하세요.
2. **실험**: 다양한 하이퍼파라미터 값을 시도하여 정확도, 속도, 메모리 간의 균형을 개선하세요.
3. **추적**: Weights & Biases로 모든 실험과 관련 메트릭을 기록하여 재현 가능한 연구를 수행하세요.
4. **시도**: 자체 커스텀 데이터셋으로 학습을 진행하여 모델을 사용 사례에 맞게 특화시키세요.
5. **배포**: vLLM과 같은 효율적인 백엔드를 사용하여 호환되는 하드웨어에서 파인튜닝된 모델을 빠르게 추론할 수 있도록 배포하세요.
6. **탐구**: 프롬프트 엔지니어링, 혼합 정밀도, 더 긴 시퀀스 길이 등의 고급 기법을 살펴보세요.
7. **학습**: 여러 작업이나 도메인에 맞는 다양한 LoRA 어댑터를 학습시키고 필요에 따라 교체하며 사용하세요.

---