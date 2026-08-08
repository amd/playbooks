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


강력한 AI 언어 모델을 직접 보유한 하드웨어에서 실행하고 싶으신가요? 이 가이드에서 방법을 알려드립니다.
이 튜토리얼에서는 AMD ROCm™ 소프트웨어로 구동되는 PyTorch를 사용하여 문서를 요약하고, 질문에 답하고, 텍스트를 생성하는 등의 작업을 모두 로컬에서 수행할 수 있는 모델을 실행합니다.

## 배우게 될 내용

- PyTorch와 ROCm을 사용하여 gpt-oss-20b, qwen3.5-4B와 같은 LLM을 로컬에서 실행
- LLM을 활용한 문서 요약 도구 만들기

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않은 경우 Ryzen AI Developer Center를 통해 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

### 가상 환경 생성

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 ROCm+Pytorch가 이미 설치된 venv를 생성하세요.
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPU 장치에 대한 사용자 액세스 권한 부여**(적용하려면 로그아웃 후 다시 로그인해야 합니다):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 venv를 생성하세요.
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
Windows에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 ROCm+Pytorch가 이미 설치된 venv를 생성하세요.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 따라 venv를 생성하세요.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **팁**: Windows 사용자는 일부 PowerShell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다(예: RemoteSigned 또는 Unrestricted로 설정).

<!-- @os:end -->

### 기본 종속성 설치
<!-- @require:driver,pytorch -->

### 추가 종속성 설치

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## 예제 스크립트로 빠르게 시작하기

이 플레이북에는 바로 사용할 수 있는 스크립트가 포함되어 있습니다. 클릭하여 미리 보고 생성한 환경과 동일한 디렉터리에 다운로드하세요.

| 스크립트 | 설명 | 사용법 |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | 기본 LLM 텍스트 생성 | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Harmony를 지원하는 문서 요약기 | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

두 스크립트 모두 다음을 지원합니다:
- `--model` 플래그를 통한 모델 선택
- 특히 문서 요약에 유용한, 적절한 모델 프롬프팅을 위한 채팅 템플릿 형식 지정

## 첫 번째 LLM 로드 및 실행

포함된 [run_llm.py](assets/run_llm.py) 스크립트는 PyTorch와 AMD ROCm을 사용하여 텍스트를 생성하는 방법을 보여줍니다.

> **참고:** 모델을 로드하면 Hugging Face Transformers는 먼저 로컬 캐시(Linux에서는 `~/.cache/huggingface/hub`, Windows에서는 `C:\Users\<user>\.cache\huggingface\hub`)를 확인합니다. 모델이 캐시되어 있지 않으면 huggingface.co에서 자동으로 다운로드됩니다. 모델 크기와 네트워크 속도에 따라 첫 실행에는 몇 분 정도 걸릴 수 있습니다.

아래 스니펫은 모델을 사용하고 질문을 사용자 지정하는 방법을 보여줍니다.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

다운로드한 스크립트를 사용해 보세요:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## 문서 요약기 만들기

로컬 LLM 출력을 생성해 보았으니, 이를 바탕으로 실용적인 문서 요약기를 만들어 보겠습니다. 이 섹션에서는 [summarizer.py](assets/summarizer.py) 스크립트를 사용하여 .txt 파일을 입력하고, GPU에서 로컬로 실행되는 간결한 요약을 자동으로 생성합니다.

이 스크립트는 별도의 설정 없이 바로 작동하도록 설계되었습니다. 에디터에서 스크립트를 열어 코드를 살펴보고, 프롬프트를 사용자 지정하며, 길이와 온도(temperature) 같은 매개변수를 조정해 보세요.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### 사용 예시

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## 생성 매개변수 알아보기

| 매개변수 | 제어하는 항목 | 일반적인 값 |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM 출력의 최대 길이 | 요약에는 50~500 토큰을 사용하세요. (토큰 1개는 약 0.75개의 영어 단어에 해당) |
| `temperature` | 창의성. 값이 낮으면 초점이 명확해지고, 값이 높으면 예측 불가능성이 커집니다 | - **0.1~0.3**: 초점이 명확하고 결정론적(요약에 적합) <br> **0.5~0.7**: 균형 잡힘(일반적인 용도) <br> **0.8~1.0**: 창의적이고 다양함(브레인스토밍) |
| `top_p` | 뉴클리어스 샘플링(Nucleus Sampling) - 값이 낮으면 모델의 출력이 더 좁게 제한됩니다 | **0.1-0.5**: 엄격하고 예측 가능함 <br> **0.9-0.95**: (표준적이고 자연스러운 대화형) |


## 실제 활용 사례

- **연구 논문 분석**: 복잡한 출판물에서 핵심 내용을 추출하여 빠르게 검토
- **뉴스 수집**: 뉴스 기사를 간단한 일일 다이제스트나 하이라이트로 요약
- **회의록**: 녹취록을 실행 가능한 항목과 간결한 요약으로 정리
- **법률 문서 검토**: 긴 법률 문서에서 관련 조항이나 의무 사항을 빠르게 추출
- **코드 문서화**: 간결한 저장소 개요와 함수 설명 생성

## 다음 단계

- **파인튜닝**: 특정 분야나 전문 용어에 맞게 모델을 조정하여 정확도를 높이세요(Fine-tuning Playbooks 참조)
- **RAG 시스템**: LLM과 문서 검색을 결합하여 맥락을 인식하는 답변과 검색 기능 구현
- **모델 탐색**: Llama 3, Phi-3, Qwen 등 새로운 모델을 실험하여 더 나은 결과 얻기
- **프로덕션 배포**: 조직 내 확장 가능한 LLM 서빙을 위해 vLLM과 같은 도구 사용

이 시스템을 통해 정교한 언어 모델을 로컬에서 실행할 수 있는 능력을 갖추게 됩니다. 다양한 모델, 프롬프트, 매개변수를 실험하며 애플리케이션에 가장 적합한 방법을 찾아보세요.