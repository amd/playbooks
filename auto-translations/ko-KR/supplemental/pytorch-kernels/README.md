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

처음부터 GPU 커널을 작성하고, 컴파일한 뒤, AMD GPU에서 실행하여 활용률이 치솟는 것을 확인해 보세요. 이 플레이북은 GPU 연산이 실제로 어떻게 작동하는지 보여줍니다. 즉, 커널 코드를 작성하고 수천 개의 스레드에서 병렬로 실행하는 방법입니다.

> **참고**: 이 플레이북은 다소 복잡하여 추가적인 디버깅과 수정이 필요할 수 있습니다.

## 배우게 될 내용

<!-- @os:windows -->
- GPU 커널의 작동 방식: 그리드, 블록, 스레드, 그리고 이를 데이터에 매핑하는 인덱싱 모델
- AMD ROCm/HIP 스택을 통해 CUDA 스타일 코드를 수정 없이 AMD GPU에서 실행하는 방법
- `torch.cuda._compile_kernel`을 사용하여 런타임에 커널을 컴파일하는 방법
- `CUDAExtension` + pybind11을 사용하여 Python에서 임포트 가능한 네이티브 C++ 커널 확장을 빌드하는 방법
<!-- @os:end -->
<!-- @os:linux -->
- GPU 커널의 작동 방식: 그리드, 블록, 스레드, 그리고 이를 데이터에 매핑하는 인덱싱 모델
- AMD ROCm/HIP 스택을 통해 CUDA 스타일 코드를 수정 없이 AMD GPU에서 실행하는 방법
- `torch.cuda._compile_kernel`을 사용하여 런타임에 커널을 컴파일하는 방법
- `CUDAExtension` + pybind11을 사용하여 Python에서 임포트 가능한 네이티브 C++ 커널 확장을 빌드하는 방법
- `amd-smi`로 커널 실행 시간을 측정하고 실시간 GPU 활용률을 모니터링하는 방법
<!-- @os:end -->

---

이 플레이북은 커널 개발을 위한 두 가지 접근 방식을 다룹니다:

<!-- @os:windows -->
| 접근 방식 | 진입점 |
|---|---|
| **JIT 컴파일** | `torch.cuda._compile_kernel`, 별도의 빌드 단계 없이 커널을 Python 문자열로 작성 |
| **C++ 확장** | `CUDAExtension` + pybind11: `.cu` 파일을 네이티브 `.pyd`로 컴파일하고 임포트 |
<!-- @os:end -->
<!-- @os:linux -->
| 접근 방식 | 진입점 |
|---|---|
| **JIT 컴파일** | `torch.cuda._compile_kernel`, 별도의 빌드 단계 없이 커널을 Python 문자열로 작성 |
| **C++ 확장** | `CUDAExtension` + pybind11: `.cu` 파일을 네이티브 `.so`로 컴파일하고 임포트 |
<!-- @os:end -->

두 접근 방식 모두 AMD GPU에서 실행됩니다. 이는 PyTorch의 ROCm 빌드가 전체 CUDA API 표면을 HIP에 매핑하기 때문에 가능합니다. 즉, `torch.cuda`, `CUDAExtension`, CUDA 커널 문법이 모두 AMD 하드웨어에서 투명하게 작동합니다.

---

## 배경 지식

### GPU 커널이란?

GPU 커널은 수천 개의 GPU 스레드에서 동시에 병렬로 실행되는 함수입니다. 호출당 한 번 실행되는 CPU 함수와 달리, 커널은 여러 개의 **스레드**를 포함하는 **블록**들의 **그리드**로 실행되며, 모든 스레드가 서로 다른 데이터에 대해 동일한 코드를 실행합니다.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### 스레드 인덱싱 모델

커널을 실행할 때 두 가지 차원을 지정합니다:

| 변수 | 의미 |
|---|---|
| `gridDim` | 그리드 내 블록 수 |
| `blockDim` | 블록당 스레드 수 |

각 스레드는 세 가지 내장 읽기 전용 변수에 접근할 수 있습니다:

| 변수 | 의미 |
|---|---|
| `blockIdx.x` | 이 스레드가 속한 블록 |
| `blockDim.x` | 한 블록 내 스레드 수 |
| `threadIdx.x` | 블록 내에서의 스레드 인덱스 |

### 전역 스레드 ID

이 변수들을 조합하여 전역적으로 고유한 스레드 인덱스를 계산합니다:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

전체 스레드 수 = `gridDim.x * blockDim.x`. 각 스레드는 하나의 요소를 독립적으로 처리합니다. 이것이 **데이터 병렬성**의 기본입니다. 스레드 간 의존성 없이 동일한 연산이 여러 요소에 대해 동시에 실행됩니다.

---

### GPU 실행 모델: 웨이브프론트

AMD GPU는 **웨이브프론트**라고 하는 **32**개 단위의 스레드 그룹으로 실행합니다. 웨이브프론트 내 모든 스레드는 동일한 명령어를 동시에 실행합니다. 이는 최적의 블록 크기 선택에 영향을 미칩니다(256개 스레드 = 8개 웨이브프론트 = 좋은 스케줄링 효율성).

### AMD GPU 프로그래밍: HIP + ROCm

**ROCm**은 AMD의 오픈소스 GPU 컴퓨팅 스택(드라이버, 컴파일러, 라이브러리, 런타임)입니다. **HIP**은 그 위에 위치하며, 문법적으로 CUDA와 동일하도록 설계되었습니다. PyTorch의 ROCm 빌드는 `torch.cuda.*`를 투명하게 HIP에 매핑하므로 동일한 코드가 AMD GPU에서 작동합니다.

---

### PyTorch + AMD/HIP

PyTorch는 CUDA API 표면(`torch.cuda.*`)이 HIP에 의해 투명하게 지원되는 ROCm 빌드를 제공합니다. 이는 다음을 의미합니다:

- `torch.cuda.is_available()`이 ROCm이 설치된 AMD GPU에서 작동합니다
- `tensor.to("cuda")`가 AMD GPU에 할당됩니다
- `torch.version.hip`이 HIP 버전을 노출합니다

또한 PyTorch는 `torch.cuda._compile_kernel()`을 제공하는데, 이는 별도의 빌드 단계 없이 원시 커널 문자열을 JIT 컴파일하여 호출 가능한 객체를 얻는 고수준 단축 방법입니다.

---

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 필수 구성 요소 - Windows
- 최신 버전 설치: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### 가상 환경 생성

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux에서는 원하는 디렉터리에서 터미널을 열고 아래 명령을 따라 ROCm+Pytorch가 이미 설치된 venv를 생성하세요.
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env --system-site-packages
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**사용자에게 GPU 장치 접근 권한 부여**(적용하려면 로그아웃 후 다시 로그인하세요):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux에서는 원하는 디렉터리에서 터미널을 열고 아래 명령을 따라 venv를 생성하세요.
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windows에서는 원하는 디렉터리에서 터미널을 열고 아래 명령을 따라 venv를 생성하세요.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **팁**: Windows 사용자는 일부 PowerShell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다(예: RemoteSigned 또는 Unrestricted로 설정).

<!-- @os:end -->
### 기본 종속성 설치

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:rocm,pytorch -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->

<!-- @device:halo_box -->
> **참고:** 이 플레이북에서는 커스텀 커널 컴파일에 전체 개발 헤더가 필요하기 때문에, Ryzen AI Halo에서도 ROCm과 PyTorch를 가상 환경에 설치해야 합니다.

ROCm 설치:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

PyTorch 설치:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```bash
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```powershell
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"
```
<!-- @test:end -->
<!-- @os:end -->
---

### 추가 종속성 설치

<!-- @os:linux -->
Linux C/C++ 빌드 툴체인을 설치합니다. 이는 시스템 수준 종속성으로, `CUDAExtension`이 `.cu` 파일에서 네이티브 `.so` 모듈을 빌드하기 때문에 C++ 확장 실습에 필요합니다.

생성한 Python 가상 환경 외부에서 Linux 머신에 한 번만 실행합니다:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

`kernel-env` 가상 환경을 활성화한 후, Python 빌드 종속성을 설치합니다:
<!-- @test:id=install-deps timeout=60 setup=activate-venv -->
```bash
python -m pip install "setuptools<82" wheel ninja
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-linux-build-tools timeout=60 hidden=True -->
```bash
set -euo pipefail

command -v gcc
command -v g++
gcc --version
g++ --version

echo "OK: Linux C/C++ build toolchain is available."
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
[Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 또는 [이후 버전](https://visualstudio.microsoft.com/vs/community/)이 **Desktop development with C++** 워크로드와 함께 설치되어 있는지 확인하세요.

> **참고**: 이 Visual Studio C++ 환경 설정은 **C++ Extension** 방식에서만 필요합니다. JIT Compilation 방식에서는 필요하지 않습니다.

PowerShell 터미널을 열고 C++ 확장을 빌드하기 전에 다음 명령을 실행합니다.

**1단계: 설치된 Visual Studio C++ 환경 찾기**

**(A) Visual Studio Installer와 함께 설치된 `vswhere.exe` 위치 찾기**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) C++ 빌드 도구가 포함된 Visual Studio 2022 이상 버전에서 `vcvars64.bat` 찾기**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) 사용 중인 Visual Studio C++ 환경 출력**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**2단계: Visual Studio C++ 빌드 환경 활성화**

**(A) `vcvars64.bat`를 실행하고 설정되는 환경 캡처**

이렇게 하면 `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH`, Windows SDK 경로를 사용할 수 있게 됩니다.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) 이 PowerShell 세션에 Visual Studio 환경 변수 가져오기**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**3단계: Microsoft C++ 컴파일러 사용 가능 여부 확인**

```powershell
where.exe cl
```

<!-- @test:id=verify-visual-studio-community timeout=60 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Detected Visual Studio installations:"
& $VsWhere -all -products * -format table | Out-Host

$VcvarsList = & $VsWhere `
  -all `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat"
if (-not $VcvarsList) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
$Vcvars = $VcvarsList | Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using vcvars64.bat from Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}

$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

where.exe cl

Write-Host "OK: Visual Studio C++ build environment is available."
```
<!-- @test:end -->
<!-- @os:end -->

#### 환경 변수 설정
<!-- @os:linux -->
<!-- @test:id=set-env-variables-linux timeout=300 setup=activate-venv -->
```bash
rocm-sdk init # Initialize the devel libraries

# Get the active Python version (e.g. "3.13") so the path works with any Python release
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"

# Set compiler and build settings
export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=set-env-variables-windows timeout=300 setup=activate-venv -->
```powershell
rocm-sdk init # Initialize the devel libraries

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
다음을 사용하여 AMD GPU가 인식되는지 확인합니다:
<!-- @test:id=amd-smi-linux timeout=60 setup=activate-venv -->
```bash
amd-smi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-setup-rocm-pytorch-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

echo "Installed ROCm/PyTorch packages:"
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true

test -d "$ROCM_HOME"
test -d "$ROCM_HOME/bin"
test -d "$ROCM_HOME/lib"

test -f "$ROCM_HOME/lib/libhiprtc.so" || ls "$ROCM_HOME/lib"/libhiprtc.so*
test -f "$ROCM_HOME/lib/libroctx64.so" || ls "$ROCM_HOME/lib"/libroctx64.so*

hipcc --version >/dev/null
rocminfo >/dev/null

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=env-setup-rocm-pytorch-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }
$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Write-Host "ROCM_ROOT=$ROCM_ROOT"
Write-Host "ROCM_BIN=$ROCM_BIN"

Write-Host "Installed ROCm/PyTorch packages:"
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"

Get-ChildItem -Path $ROCM_ROOT -Recurse -Filter "hiprtc*.dll" | Select-Object -First 10 FullName | Out-Host

hipcc --version | Out-Host
hipinfo | Out-Host

$code = @'
import os
import sys
import torch

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---

## 필수 파일 다운로드

**2개의 새 폴더**를 만들고 해당 파일을 다운로드하여 다음 디렉터리 구조를 생성합니다:

| 디렉터리 | 다운로드할 파일 | 설명 |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| 벡터 덧셈 커널을 위한 JIT 및 C++ 확장 파일 |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 행렬 곱셈 커널을 위한 JIT 및 C++ 확장 파일 |


## 실습

### 실습 1: 벡터 덧셈

#### 방식 A: JIT 컴파일

JIT(Just-In-Time) 컴파일은 커널을 Python 내부의 원시 C++ 문자열로 작성하고, 별도의 빌드 단계 없이 런타임에 컴파일하는 방식을 의미합니다.

[add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)를 사용하려면, 다운로드가 완료되었는지 확인한 후 다음을 실행합니다:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**주요 코드 스니펫**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        for (int i = 0; i < 1000; i++)
            data[idx] += 1.0f;
    }
}
"""


# Snippet 2: Compile the kernel string. PyTorch calls hipcc under the hood with ROCm
add_one_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "add_one")

x = torch.ones(100_000_000, dtype=torch.float32, device="cuda")
n = x.numel()
block_size = 256
grid_size = (n + block_size - 1) // block_size


# Snippet 3: Launch: specify the grid/block dimensions and pass tensor arguments directly
for _ in range(200):
    add_one_kernel(
        grid=(grid_size, 1, 1),
        block=(block_size, 1, 1),
        args=[x, n],
    )


# Snippet 4: Test the output
print("First 5 elements:", x[:5].cpu()) 
#Expected output: tensor([200001., 200001., 200001., 200001., 200001.])
```
<!-- @os:linux -->
> **팁**: 이 스크립트는 커널 실행 중 최대 및 평균 GPU 사용률을 기록하기 위해 100ms마다 `amd-smi`를 폴링하는 백그라운드 스레드도 생성합니다.
<!-- @os:end -->

> **참고**: **왜 블록 크기가 256인가요?** <br>
> - 이 커널은 **블록당 256개 스레드**를 사용하는데, 이는 **AMD GPU의 웨이브프론트 실행 모델**과 잘 맞기 때문입니다.
> - AMD 하드웨어는 32개 스레드 단위로 그룹화하여 스레드를 실행하므로, 블록당 8개의 웨이브프론트가 생성된다는 점을 기억하세요. (8 웨이브프론트 x 32 스레드 = 1블록)


**워크로드가 수행하는 작업:**

이 커널은 GPU 사용률을 보여주기 위해 인위적으로 추가 작업을 수행합니다:

- 텐서에 **100,000,000개의 요소**
- 커널 실행당 요소당 **내부 루프가 1,000회 실행**됨
- 총 **200회 커널 실행**

**연산:**  
- 각 요소: 1 × 1,000회 반복 × 200회 실행만큼 증가 = 200,000  
- 최종 결과: 1.0(초기값) + 200,000(덧셈) = 200,001.0

**내부 루프가 필요한 이유는 무엇인가요?**  
- `for (int i = 0; i < 1000; i++)` 루프가 없으면 200회 실행이 즉시 끝나버려서 모니터링 도구가 의미 있는 GPU 사용률을 포착하지 못합니다. 인위적인 작업을 통해 모니터링 도구가 성능을 측정할 수 있을 만큼 각 커널 실행 시간을 충분히 늘립니다.

<!-- @os:linux -->
**예상 출력:**[성능 수치는 환경에 따라 달라질 수 있습니다]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **참고**: Windows에서는 `amd-smi`가 지원되지 않습니다. GPU 사용률을 추적하려면 작업 관리자를 사용할 수 있으며, 프로그램을 실행하면 짧은 사용률 급증을 확인할 수 있습니다.

**예상 출력:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**잘하셨습니다! 첫 번째 GPU 커널을 실행하셨습니다.**

<!-- @os:linux -->
<!-- @test:id=vector-addition-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
'''

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-addition-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
"""

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
'@

$code | python -
```
<!-- @test:end -->
<!-- @os:end -->

---
#### 방법 B: C++ 확장

두 번째 방법은 좀 더 수동적입니다. 커널과 Python 바인딩을 하나의 `.cu` 파일에 작성하고, PyTorch의 빌드 시스템을 사용하여 네이티브로 컴파일한 다음 Python으로 가져옵니다.

<!-- @os:windows -->
> **참고**: C++ 확장 방법은 PyTorch가 `.cu` 소스 파일을 네이티브 `.pyd` 확장 모듈로 컴파일하기 때문에 Visual Studio C++ 빌드 환경이 필요합니다. 이 네이티브 확장을 빌드하려면 Visual Studio에서 제공하는 Microsoft C++ 툴체인(컴파일러, 링커, 빌드 도구)이 필요합니다. 확장을 빌드하기 전에 설정 섹션에 있는 Visual Studio 활성화 명령을 실행하세요.
<!-- @os:end -->

아직 다운로드하지 않았다면 다음 파일을 다운로드하세요:
<!-- @os:windows -->
| 파일 | 역할 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 커널 + 실행기 + pybind11 바인딩, 모두 한 파일에 포함 |
| [setup.py](assets/Vector_Addition/setup.py) | 빌드 스크립트, `CUDAExtension`을 사용해 `.cu`를 `.pyd`로 컴파일 |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 빌드된 아티팩트를 실행하는 Python 스크립트 |
<!-- @os:end -->

<!-- @os:linux -->
| 파일 | 역할 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 커널 + 실행기 + pybind11 바인딩, 모두 한 파일에 포함 |
| [setup.py](assets/Vector_Addition/setup.py) | 빌드 스크립트, `CUDAExtension`을 사용해 `.cu`를 `.so`로 컴파일 |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 빌드된 아티팩트를 실행하는 Python 스크립트 |
<!-- @os:end -->

#### **1단계: 커널, 실행기, 바인딩** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
// GPU kernel, one thread per element
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) data[idx] += 1.0f;
}

// Launcher, bridges torch::Tensor to raw pointer, sets grid/block, runs kernel
void add_one_launcher(torch::Tensor tensor) {
    int n = tensor.numel();
    float* data = tensor.data_ptr<float>();
    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;
    add_one<<<grid_size, block_size>>>(data, n);
    hipDeviceSynchronize();
}

// Python binding, exposes add_one_launcher as add_one_ext.add_one
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("add_one", &add_one_launcher, "Add one kernel (HIP)");
}
```

>**팁**: `hipDeviceSynchronize()`를 사용하는 이유는 무엇일까요? <br>
> - GPU 커널 실행은 비동기적입니다. CPU가 `add_one<<<grid_size, block_size>>>(data, n);`를 실행하면 GPU 작업이 끝나기를 기다리지 않고 즉시 다음 명령을 실행합니다. `hipDeviceSynchronize()`는 GPU 커널이 완료될 때까지 CPU가 대기하도록 강제합니다.

#### **2단계: 빌드**
```bash
pip install --no-build-isolation -v .
```
>**참고**: 이 명령은 현재 디렉터리에서 `setup.py`를 찾아 우리가 작성한 .cu 파일을 빌드합니다.


`CUDAExtension`은 `torch.utils.cpp_extension`에 있는 CUDA 빌드 헬퍼입니다. ROCm에서는 PyTorch가 `nvcc` 대신 `hipcc`를 사용하도록 **`CUDAExtension`을 다시 매핑**합니다. ROCm은 빌드 경로를 가로채서 HIP 컴파일러를 통해 라우팅하며, CUDA 코드를 AMD로 포팅합니다.

이 과정을 거치면 다음 파일이 생성됩니다:
<!-- @os:windows -->
- `build/`: `.pyd` 파일이 들어 있는 디렉터리
- `add_one_kernel.hip`: `.cu` 파일을 hipify한 결과로 생성된 HIP 소스; 실제로 `hipcc`가 컴파일한 대상
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: `.so` 파일이 들어 있는 디렉터리
- `add_one_kernel.hip`: `.cu` 파일을 hipify한 결과로 생성된 HIP 소스; 실제로 `hipcc`가 컴파일한 대상
<!-- @os:end -->

#### **3단계: Python에서 사용하기** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
이 스크립트를 실행하여 커널이 동작하는 모습을 확인하세요:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**예상 출력:**
```
Before: tensor([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], device='cuda:0')
After: tensor([2., 2., 2., 2., 2., 2., 2., 2., 2., 2.], device='cuda:0')
```

<!-- @os:linux -->
<!-- @test:id=vector-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Vector_Addition

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Vector_Addition"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

### 실습 2: 행렬 곱셈

행렬 곱셈은 다음과 같이 **C = A × B**를 계산합니다:
- **A**는 M×N (행 × 열)
- **B**는 N×K  
- **C**는 M×K (결과)

각 출력 요소는 다음과 같이 정의됩니다:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C의 각 요소는 독립적으로 계산되므로 GPU 병렬 처리에 매우 적합합니다.

#### GPU 스레드에 매핑되는 방식

벡터 덧셈(1D)과 달리 행렬 곱셈은 **2D 출력**을 생성하므로 **2D 스레드 그리드**를 사용합니다:

| | 벡터 덧셈 | 행렬 곱셈 |
|---|---|---|
| **출력 형태** | 1D 배열 | 2D 행렬 (M×K) |
| **스레드 매핑** | 스레드 1개 → 요소 1개 | 스레드 1개 → 출력 요소 1개 |
| **실행 패턴** | 1D 그리드: `(grid_x, 1, 1)` | 2D 그리드: `(grid_x, grid_y, 1)` |
| **블록 크기** | `(256, 1, 1)` | `(16, 16, 1)` = 256개 스레드 |

각 스레드는 출력 행렬 C의 요소 하나를 계산합니다. `(row, col)` 위치에 있는 스레드는 A의 해당 행과 B의 해당 열을 곱하여 `C[row][col]`을 계산합니다.

**메모리 레이아웃**: GPU 메모리는 평평한(1D) 구조이지만, 행렬은 행 단위로 저장됩니다. `A[row][col]`에 접근하기 위해 커널은 `A[row * N + col]`을 사용합니다.


#### 방법 A: JIT 컴파일:

실습 1과 마찬가지로, 커널은 Python 내부에 원시 C++ 문자열로 작성되며 PyTorch에 내장된 JIT를 통해 런타임에 컴파일됩니다.


[matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)를 사용하려면, 먼저 다운로드했는지 확인한 후 다음을 실행하세요:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**주요 코드 스니펫**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

# Snippet 2: Creating the Matrix - 2D indexing to map threads onto the M×K output matrix
# Inputs: A is M x N, B is N x K, C is M x K
M, N, K = 1024, 512, 768

A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK


# Snippet 3: Compile the kernel string
matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")


# Snippet 4:. Launch with a 2D grid, grid_x covers columns (K), grid_y covers rows (M)
BLOCK = 16
matmul_kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()
print(f"Max error vs torch.mm: {max_err:.6f}")
```

스크립트는 작은 허용 오차 범위 내에서 결과를 `torch.mm`과 비교하여 검증합니다. GPU에서의 부동 소수점 연산은 병렬 리덕션 순서로 인해 CPU 구현과 비교했을 때 작은 수치적 차이가 발생할 수 있습니다.

<!-- @os:linux -->
**예상 출력:**[성능 수치는 달라질 수 있습니다]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **참고**: Windows에서는 `amd-smi`가 지원되지 않습니다. GPU 사용률을 확인하려면 작업 관리자를 사용할 수 있으며, 프로그램을 실행하면 사용률이 잠깐 급증하는 것을 볼 수 있습니다.

**예상 출력:**
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
No GPU Usage captured.
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=matmul-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
'''

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---
#### 방법 B: C++ Extension

두 번째 방법은 좀 더 수동적입니다. 커널과 Python 바인딩을 하나의 `.cu` 파일에 작성하고, PyTorch의 빌드 시스템을 사용해 네이티브로 컴파일한 다음 Python으로 가져오는 방식입니다.

<!-- @os:windows -->
> **참고**: C++ Extension 방식은 Visual Studio C++ 빌드 환경이 필요합니다. PyTorch가 `.cu` 소스 파일을 네이티브 `.pyd` 확장 모듈로 컴파일하기 때문입니다. 이 네이티브 확장을 빌드하려면 Visual Studio에서 제공하는 Microsoft C++ 도구 체인(컴파일러, 링커, 빌드 도구)이 필요합니다. 확장 모듈을 빌드하기 전에 설정 섹션에 나온 Visual Studio 활성화 명령을 실행하세요.
<!-- @os:end -->

아직 다운로드하지 않았다면 다음 파일들을 다운로드하세요:
<!-- @os:windows -->
| 파일 | 역할 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 커널 + 런처 + pybind11 바인딩 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 빌드 스크립트, `CUDAExtension`을 사용해 `.cu`를 `.pyd`로 컴파일 |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 빌드된 산출물을 실행하는 Python 스크립트 |
<!-- @os:end -->
<!-- @os:linux -->
| 파일 | 역할 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 커널 + 런처 + pybind11 바인딩 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 빌드 스크립트, `CUDAExtension`을 사용해 `.cu`를 `.so`로 컴파일 |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 빌드된 산출물을 실행하는 Python 스크립트 |
<!-- @os:end -->

#### **1단계: 커널, 런처, 바인딩** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
#define BLOCK 16

// GPU kernel, one thread per output element of C
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}

// Launcher, extracts dims from torch::Tensor, allocates C, sets 2D grid/block
torch::Tensor matmul_launcher(torch::Tensor A, torch::Tensor B) {
    int M = A.size(0), N = A.size(1), K = B.size(1);
    auto C = torch::zeros({M, K}, A.options());

    dim3 block(BLOCK, BLOCK);
    dim3 grid((K + BLOCK - 1) / BLOCK, (M + BLOCK - 1) / BLOCK);

    matmul<<<grid, block>>>(A.data_ptr<float>(), B.data_ptr<float>(),
                            C.data_ptr<float>(), M, N, K);
    hipDeviceSynchronize();
    return C;
}

// Python binding, exposes matmul_launcher as matmul_ext.matmul
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("matmul", &matmul_launcher, "Naive matmul kernel (HIP): A(M,N) @ B(N,K) -> C(M,K)");
}
```

연습 1의 `add_one_launcher`와 비교했을 때, 이번 런처는:
- 입력 텐서를 하나가 아니라 두 개 받습니다
- 세 가지 차원(M, N, K) 모두를 텐서 형태에서 유도하며, Python에서 크기를 수동으로 전달하지 않습니다
- 제자리에서 값을 변경하는 대신 출력 텐서 C를 할당하고 반환합니다
- 2D 실행 형태를 표현하기 위해 그리드와 블록 모두에 `dim3`를 사용합니다

#### **2단계: 빌드**
```bash
pip install --no-build-isolation -v .
```
>**참고**: 이 명령은 현재 디렉터리에서 `setup.py`를 찾아 우리가 작성한 .cu 파일을 빌드합니다.


이 과정을 거치면 다음 파일들이 생성됩니다:
<!-- @os:windows -->
- `build/`: `.pyd` 파일들이 포함된 디렉터리
- `matmul_kernel.hip`: `.cu` 파일을 hipify하여 생성된 HIP 소스로, 실제로 `hipcc`가 컴파일한 대상입니다
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: `.so` 파일들이 포함된 디렉터리
- `matmul_kernel.hip`: `.cu` 파일을 hipify하여 생성된 HIP 소스로, 실제로 `hipcc`가 컴파일한 대상입니다
<!-- @os:end -->

#### **3단계: Python에서 사용하기** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
이 스크립트를 실행하여 커널이 작동하는 모습을 확인하세요:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**예상 출력:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**축하합니다! 방금 GPU에서 행렬 곱셈을 구현했습니다.** 행렬 곱셈은 다음과 같은 현대 머신러닝 연산의 근간이기 때문에 이는 중요한 이정표입니다:
- 신경망 레이어
- 어텐션 메커니즘
- 임베딩
- 트랜스포머

<!-- @os:linux -->
<!-- @test:id=matmul-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Matrix_Multiplication

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Matrix_Multiplication"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

## 다음 단계

이제 JIT 컴파일과 C++ 확장 모듈 두 가지 방식 모두를 사용해 기본적인 병렬 연산을 위한 GPU 커널을 작성, 컴파일, 실행하는 방법을 배웠습니다.

**성능 최적화:**
- **공유 메모리 타일링** - 전역 메모리 접근을 줄이기 위해 데이터 블록을 캐싱
- **메모리 코얼레싱** - 대역폭을 위해 메모리 접근 패턴 최적화

**실제 알고리즘:**
- **2D 컨볼루션** - 작은 필터(커널)가 이미지를 가로질러 슬라이딩하며, 이웃 픽셀의 가중합으로 각 출력 픽셀을 계산합니다. 이는 스텐실 연산과 공유 메모리 타일링을 소개하며, 여기서 스레드들은 전역 메모리 접근을 줄이기 위해 겹치는 이미지 영역을 재사용합니다.
- **소프트맥스 함수**: 소프트맥스는 숫자 벡터를 합이 1이 되는 확률로 변환하며, 신경망 출력에서 흔히 사용됩니다. GPU에서 이를 효율적으로 구현하려면 대규모 벡터를 처리하면서 병렬 리덕션과 수치 안정성 기법을 도입해야 합니다.

**프로덕션 고려사항:**
- **오류 처리** - 경계 검사와 디바이스 관리
- **PyTorch 통합** - autograd를 지원하는 커스텀 연산자