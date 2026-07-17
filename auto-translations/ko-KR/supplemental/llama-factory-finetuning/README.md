## 개요

효율적인 파인튜닝은 대규모 언어 모델(LLM)을 다운스트림 작업에 적용하는 데 필수적입니다. LLaMA-Factory는 대규모 언어 모델 및 멀티모달 모델의 학습과 파인튜닝을 간소화하는 오픈소스 사용자 친화적 플랫폼입니다. 최소한의 코딩으로 수백 개의 사전 학습된 모델을 로컬에서 커스터마이징할 수 있습니다.

이 플레이북은 로컬 AMD 하드웨어에서 LLaMA-Factory를 사용하여 LLM을 파인튜닝하는 방법을 안내합니다.

<!-- @device:stx,krk -->
> **참고:** 이 플레이북의 파인튜닝 기법을 사용하려면 최소 **32GB의 시스템 RAM**이 필요하며, 그 중 최소 **16GB가 GPU에서 사용 가능**해야 합니다(16GB는 32GB의 일부이며, 추가로 필요한 것이 아닙니다).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **참고:** 이 플레이북의 파인튜닝 기법을 사용하려면 최소 **16GB의 총 GPU 메모리**와 **32GB의 시스템 RAM**이 필요합니다.
> - Windows에서 총 GPU 메모리는 그래픽 카드의 전용 VRAM과 공유 GPU 메모리(시스템 RAM에서 빌려온 것)를 합산합니다.
> - 따라서 전용 VRAM이 16GB 미만인 카드도 공유 GPU 메모리를 활용하여 부족한 용량을 보완함으로써 이 플레이북을 실행할 수 있습니다.
<!-- @os:end -->

<!-- @os:linux -->
> **참고:** 이 플레이북의 파인튜닝 기법을 사용하려면 최소 **16GB의 전용 GPU 메모리**를 갖춘 그래픽 카드와 **32GB의 시스템 RAM**이 필요합니다.
> - Linux에서는 학습이 전적으로 그래픽 카드의 전용 VRAM에서 실행됩니다.
> - VRAM이 부족할 경우 공유 GPU 메모리(시스템 RAM)로 폴백되지 않습니다.
> - 전용 VRAM이 16GB 미만인 카드는 시스템에 RAM이 충분하더라도 Linux에서 학습 중 메모리 부족이 발생합니다.
<!-- @os:end -->
<!-- @device:end -->

## 학습 내용

- AMD ROCm™ 소프트웨어와 함께 LLaMA-Factory를 설정하는 방법
- LLM 파인튜닝 파라미터 구성 방법 (Qwen/Qwen3-4B-Instruct-2507을 예시로 사용)
- LLaMA-Factory 파인튜닝 실행 방법
- 파인튜닝된 모델로 추론을 실행하는 방법
- 파인튜닝된 모델을 내보내는 방법

## 예상 소요 시간

- 소요 시간: 이 플레이북을 실행하는 데 약 60분이 소요됩니다(모델/데이터셋 크기 및 네트워크 속도에 따라 다를 수 있습니다).
- 자세한 내용은 [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory)를 참조하세요.

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### 가상 환경 생성

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPU 장치에 대한 사용자 접근 권한 부여** (적용되려면 로그아웃 후 다시 로그인하세요):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### 기본 종속성 설치

<!-- @require:pytorch,driver -->
 
### 추가 종속성 설치

> **참고**: Python 버전이 3.11, 3.12 또는 3.13인지 확인하세요.

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### LLaMA Factory 설치

LLaMA-Factory는 PyTorch에 의존합니다. 위의 요구 사항에 따라 이미 설치되어 있어야 합니다.

[LLaMA Factory 공식 GitHub 저장소](https://github.com/hiyouga/LlamaFactory)에서 소스 코드를 다운로드하고 종속성을 설치합니다.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

`llamafactory-cli`가 실행 가능한지 확인합니다.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

출력 예시:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

LLaMA-Factory를 성공적으로 설치했으니, 이제 파인튜닝을 실행해 보겠습니다.

## 파인튜닝을 위한 LLaMA Factory CLI 사용

이 섹션에서는 파인튜닝 데이터셋 준비, LoRA/QLoRA 파라미터 구성, LoRA 파인튜닝 실행 방법을 다룹니다.

### 데이터셋 준비

LLaMA-Factory는 Alpaca 형식과 ShareGPT 형식의 파인튜닝 데이터셋을 지원합니다. 사용 가능한 모든 데이터셋은 [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json)에 정의되어 있습니다. 커스텀 데이터셋을 사용하는 경우, `dataset_info.json`에 데이터셋 설명을 추가하고 학습 전에 데이터셋 이름을 지정해야 합니다. 자세한 내용은 [공식 문서](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html)에서 확인할 수 있습니다.

이 플레이북에서는 identity 및 alpaca_en_demo 데이터셋을 예시로 사용하며, 다음 단계에서 데이터셋 정보를 구성합니다.


### 파인튜닝 파라미터 구성

LLaMA-Factory는 여러 파인튜닝 방식을 지원합니다.

| 파인튜닝 방식 | LLaMA Factory 예시 |
|-----------|------|
| 전체 파라미터 | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA 파인튜닝 | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA 파인튜닝 | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

이 예시 구성 파일에는 모델 파라미터, 파인튜닝 방법 파라미터, 데이터셋 파라미터, 평가 파라미터 등이 지정되어 있습니다. 필요에 따라 구성할 수 있습니다. 이 플레이북에서는 [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml)을 사용합니다.

**주요 파라미터 설명:**
- `model_name_or_path` - Hugging Face 모델 이름 또는 로컬 모델 파일 경로.
- `stage` - 학습 단계. 옵션: rm (보상 모델링), pt (사전 학습), sft (지도 파인튜닝), PPO, DPO, KTO, ORPO.
- `do_train` - 학습은 true, 평가는 false
- `finetuning_type` - 파인튜닝 방법. 옵션: freeze, lora, full
- `lora_rank` - LoRA에서 사용되는 저랭크 행렬의 차원. 일반적인 값: 4, 6, 8, 16 (값이 작을수록 파라미터 수가 적고 파인튜닝이 빠름; 값이 클수록 작업 적응력이 높지만 리소스 사용량이 증가).
- `lora_target` - LoRA 방법의 대상 모듈. 기본값: all.
- `dataset` - 사용할 데이터셋. 여러 데이터셋을 구분하려면 ","를 사용
- `output_dir` - 파인튜닝 출력 경로
- `logging_steps` - 스텝 단위 로깅 간격
- `save_steps` - 모델 체크포인트 저장 간격.
- `overwrite_output_dir` - 출력 디렉터리 덮어쓰기 허용 여부.
- `per_device_train_batch_size` - 장치당 학습 배치 크기.
- `gradient_accumulation_steps` - 그래디언트 누적 스텝 수.
- `learning_rate` - 학습률
- `num_train_epochs` - 학습 에포크 수
- `lr_scheduler_type` - 학습률 스케줄. 옵션: linear, cosine, polynomial, constant 등.
- `warmup_ratio` - 학습률 워밍업 비율

<!-- @os:linux -->
AMD Ryzen™ 및 AMD Radeon™ GPU에서 파인튜닝을 실행하기 위해 `lora_rank`의 기본값을 수정합니다.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
AMD Ryzen™ 및 AMD Radeon™ GPU와의 호환성을 높이기 위해 기본 LoRA 파인튜닝 구성을 다음과 같이 업데이트합니다:
- 파인튜닝 중 메모리 사용량을 줄이기 위해 `lora_rank`를 `8`에서 `6`으로 변경합니다.
- 더 넓은 AMD GPU 호환성과 낮은 메모리 사용량을 위해 `bf16` 대신 `fp16`을 사용합니다.
- 멀티프로세싱 데이터 로딩으로 인한 `"Can't pickle local object<>"` 오류를 방지하기 위해 Windows에서 `dataloader_num_workers`를 `0`으로 설정합니다.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### LLaMA Factory 파인튜닝 실행

**llamafactory-cli**는 LLaMA-Factory의 공식 명령줄 인터페이스(CLI) 도구로, 복잡한 코드 작성 없이 엔드투엔드 LLM 워크플로우(데이터 준비 → 파인튜닝 → 평가 → 배포)를 간소화하기 위해 개발되었습니다.

학습/파인튜닝의 경우, **llamafactory-cli train**은 LLaMA Factory CLI의 핵심 서브커맨드입니다. 데이터 전처리, 하이퍼파라미터 튜닝, 하드웨어 최적화 등의 파인튜닝 워크플로우를 단일 CLI 명령으로 추상화하며, 여러 파인튜닝 패러다임(LoRA/QLoRA/전체 파인튜닝)을 지원하고 저사양 GPU(예: 16GB VRAM에서의 QLoRA)에 최적화되어 있습니다.

수정된 Qwen3 LoRA 파인튜닝 구성 파일을 기반으로 다음 명령을 사용하여 LLaMA-Factory 파인튜닝을 실행할 수 있습니다.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

LLM 파인튜닝 실행 후, 모델 체크포인트 파일, 구성 파일, 학습 메트릭을 포함한 모든 생성된 출력물이 "output_dir"에 저장됩니다.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### 파인튜닝된 모델 테스트

**llamafactory-cli chat**은 LLM(기본 모델 및 LoRA 파인튜닝 모델 모두)과의 대화형 채팅/추론을 위해 설계되었습니다. LLaMA-Factory는 [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference)에서 파인튜닝된 모델의 추론을 실행하기 위한 샘플 구성을 제공합니다. 추론 백엔드 등의 설정을 변경하기 위해 이 샘플 구성을 수정할 수도 있습니다.

다음 명령을 사용하여 Qwen3 파인튜닝 모델을 테스트합니다:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
파인튜닝된 모델을 사용한 채팅 예시는 아래와 같습니다:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### 파인튜닝된 모델 내보내기

프로덕션 사용 사례의 경우, 사전 학습된 모델과 LoRA 어댑터를 병합하여 단일 모델로 내보내야 합니다. 이 병합된 모델은 일반 Hugging Face 모델 파일로 사용할 수 있습니다. LLaMA-Factory는 [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora)에서 샘플 구성을 제공합니다.

다음 명령을 사용하여 Qwen3 파인튜닝 모델을 내보냅니다:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
파인튜닝된 모델 내보내기 결과는 아래와 같습니다.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 

## LLaMA Factory GUI 사용

`LLaMA-Factory`는 브라우저의 웹 UI를 통한 코드 없는 LLM 파인튜닝도 지원합니다.

다음 명령을 사용하여 실행합니다:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI`는 학습, 평가, 예측, 채팅, 모델 내보내기를 포함한 머신러닝 워크플로우 관리를 위한 간소화된 인터페이스를 제공합니다. 각 탭에 대한 간략한 소개는 다음과 같습니다:

* **Train**: 이 탭에서는 모델과 데이터셋을 선택하고, 학습 파라미터를 구성하며, 학습 프로세스를 시작할 수 있습니다. 학습 설정을 최적화하려면 필수 및 선택적 파라미터를 이해하는 것이 중요합니다.
* **Evaluate & Predict**: 학습 후 이 탭을 사용하여 모델의 성능을 평가하고 예측을 수행할 수 있습니다. 새로운 데이터에 대한 모델의 정확도와 효과성에 대한 인사이트를 제공합니다.
* **Chat**: 학습이 완료되면 Chat 탭에서 모델을 로드하여 상호작용하고 작업 결과를 확인합니다. 이 기능을 통해 학습된 모델과 실시간으로 대화할 수 있습니다.
* **Export**: 이 탭은 배포 또는 추가 사용을 위한 학습된 모델 내보내기를 지원합니다. 다양한 애플리케이션에 적합한 여러 형식으로 모델을 저장할 수 있습니다.

자세한 안내는 [LlamaFactory GitHub 저장소](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio)와 [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest)의 공식 문서를 참조하시기 바랍니다. 또한 [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui)에서 인터페이스와 기능에 대한 유용한 정보를 확인할 수 있습니다.

## 다음 단계
- `gpt-oss` 및 기타 최신 모델을 사용해 보세요.
- 파인튜닝된 모델에서 다양한 백엔드를 실험해 보세요.
 
더 많은 문서는 다음을 방문하세요: https://llamafactory.readthedocs.io/en/latest/