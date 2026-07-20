<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북에는 GitHub에서 렌더링할 수 없는 특수 태그가 사용됩니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문해 주세요.
<!-- @github-only:end -->

# RPC를 이용한 두 대의 Ryzen™ AI Halo 클러스터링

## 개요

Ryzen™ AI Halo는 이미 대규모 언어 모델을 로컬에서 실행할 수 있는 성능을 갖추고 있습니다. 클러스터링을 활용하면 로컬 네트워크를 통해 여러 시스템의 GPU 메모리를 결합함으로써, 더 뛰어난 추론 능력, 향상된 코드 생성, 그리고 더 깊은 다국어 이해력을 갖춘 훨씬 더 큰 모델을 온전히 자신의 하드웨어에서 사용할 수 있게 됩니다.

이 플레이북에서는 llama.cpp의 RPC 엔진을 사용하여 두 대의 Ryzen AI Halo 시스템을 클러스터링하고, AMD ROCm™ 가속을 통해 3,580억 개의 파라미터를 가진 GLM 4.7 모델을 두 대의 머신에서 실행하는 방법을 안내합니다.

## 학습 내용

- Ryzen AI Halo 시스템에서 VRAM 할당을 확장하는 방법
- ROCm 및 RPC 지원과 함께 llama.cpp 설치하기
- RPC 워커 구성 및 두 노드에 걸친 분산 추론 실행하기
- 네트워크로 연결된 두 대의 Ryzen AI Halo 시스템에서 3,580억 파라미터 모델 실행하기

## 메모리 구성 설정

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료해야 합니다.

<!-- @os:windows -->
Windows에서는 더 많은 메모리를 필요로 하는 대형 모델을 실행하기 위해 AMD Variable Graphics Memory(iGPU VRAM) 할당을 사용해야 합니다.

이 작업은 AMD Software: Adrenalin Edition 제어판을 열고 `Performance > Tuning > AMD Variable Graphics Memory`로 이동하여 수행할 수 있습니다. 값을 **96GB**로 설정하세요. 변경 사항을 적용하려면 시스템을 재부팅해 주세요.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Linux에서는 ROCm이 공유 시스템 메모리 풀을 사용하며, 이 풀은 기본적으로 시스템 메모리의 절반으로 구성됩니다.

이 용량은 다음 지침에 따라 커널의 Translation Table Manager(TTM) 페이지 설정을 변경하여 늘릴 수 있습니다. AMD는 BIOS에서 최소 전용 VRAM(0.5GB)을 설정할 것을 권장합니다.

* pipx 유틸리티를 설치하고 pipx로 설치된 wheel의 경로를 시스템 검색 경로에 추가하세요.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI에서 amd-debug-tools wheel을 설치하세요.
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttm 도구를 실행하여 공유 메모리의 현재 설정을 조회하세요.
  ```bash
  amd-ttm
  ```

* 공유 메모리 설정을 **120GB**로 재구성하세요:
  ```bash
  amd-ttm --set 120
  ```

* 변경 사항을 적용하려면 시스템을 재부팅하세요.


<!-- @os:end -->
<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->
## 사전 준비 사항

### 하드웨어

이 플레이북을 진행하려면 두 대의 Ryzen AI Halo 유닛과 한 대의 이더넷 스위치가 필요하며, 각 유닛을 스위치에 직접 연결하는 스타 토폴로지 구성으로 연결해야 합니다.

| 구성 요소 | 수량 | 설명 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 클러스터를 구성하는 컴퓨팅 노드 |
| 10Gbps 이더넷 스위치 | 1 | 다중 노드 Ryzen AI Halo 통신을 지원하는 중앙 스위치(최소 2개 포트) |
| 이더넷 케이블 | 2 | 각 Halo 유닛을 스위치에 연결(Cat 7 이상 권장) |

> **참고**: 두 대의 Ryzen AI Halo 유닛을 연결하려면 이더넷 스위치 포트 2개가 필요합니다. Halo 유닛 중 하나가 아닌 별도의 클라이언트 머신에서 모델에 액세스하려는 경우 세 번째 포트가 필요합니다.

### 소프트웨어
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
다음을 설치해 주세요:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- **Desktop Development with C++** 워크로드가 포함된 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 물리적 하드웨어 설정

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료해야 합니다.

각 Ryzen AI Halo 유닛을 Cat 7(또는 그 이상) 케이블을 사용하여 이더넷 스위치에 연결하세요. 이를 통해 노드 간 고속 통신에 사용되는 10Gbps 링크가 구성됩니다.
<!-- @os:linux -->
### 1. 네트워크 인터페이스 확인

각 머신에서 네트워크 인터페이스의 이름을 확인하고 기록해 두세요(이후 `IFNAME`으로 참조됩니다). 다음을 실행하세요:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

이 명령은 인터페이스 이름을 직접 출력합니다. 예:

```bash
enp191s0
```

### 2. 네트워크 링크 속도 확인

인터페이스의 속도를 확인하여 링크가 활성화되어 있고 최고 속도로 작동하는지 확인하세요:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **참고**: `<IFNAME>`을 [1. 네트워크 인터페이스 확인](#1-네트워크-인터페이스-확인)에서 확인한 출력 인터페이스 이름으로 바꾸세요.

`10000Mb/s`의 속도가 표시되어야 합니다:

```bash
	Speed: 10000Mb/s
```

> **참고**: 속도가 `10000Mb/s`보다 낮거나 링크가 활성화되지 않는 경우, 케이블 연결을 확인하고 스위치 포트가 10Gbps로 설정되어 있는지 확인하세요. 일부 스위치는 자동 협상(auto-negotiation)을 비활성화하고 링크 속도를 수동으로 설정해야 할 수 있습니다. 자세한 내용은 스위치 설명서를 참조하세요.

<!-- @os:end -->

<!-- @os:windows -->
### 네트워크 링크 속도 확인

각 머신에서 네트워크 인터페이스의 링크 속도를 확인하세요:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

이더넷 인터페이스는 `Up` 상태이며 `10 Gbps`로 작동해야 합니다:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **참고**: 속도가 `10 Gbps`보다 낮거나 링크가 활성화되지 않는 경우, 케이블 연결을 확인하고 스위치 포트가 10Gbps로 설정되어 있는지 확인하세요. 일부 스위치는 자동 협상(auto-negotiation)을 비활성화하고 링크 속도를 수동으로 설정해야 할 수 있습니다. 자세한 내용은 스위치 설명서를 참조하세요.

<!-- @os:end -->

## llama.cpp 설치

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료해야 합니다.

두 가지 설치 옵션을 사용할 수 있습니다:

- [옵션 1: Lemonade SDK(권장)](#option-1-lemonade-sdk-recommended) - 사전 빌드된 바이너리, 가장 빠른 설정
- [옵션 2: 수동 소스 빌드](#option-2-manual-source-build) - 빌드 플래그를 완전히 제어할 수 있는 소스 빌드

### 옵션 1: Lemonade SDK(권장)

Lemonade SDK는 gfx1151(Strix Halo / Ryzen AI Max+ 395)과 같은 GPU 및 기타 최신 Radeon 아키텍처를 대상으로 하는 AMD ROCm 7 가속이 적용된 llama.cpp의 나이틀리 빌드를 제공합니다.

<!-- @os:windows -->
#### Step 1: 사전 빌드된 바이너리 다운로드

최신 릴리스 페이지로 이동하여 플랫폼 및 GPU 대상에 맞는 아카이브를 다운로드합니다:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-windows-rocm-gfx1151-x64.zip` 파일을 다운로드합니다(여기서 `xxxx`는 빌드 번호입니다).

#### Step 2: 바이너리 압축 해제

다운로드한 아카이브의 압축을 해제합니다:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

이제 이 디렉터리에는 Ryzen AI Halo 시스템용으로 미리 컴파일된 ROCm 지원 `llama-cli.exe`, `llama-server.exe`, `rpc-server.exe` 빌드가 포함되어 있습니다.

#### Step 3: GPU 감지 확인

```bash
.\llama-cli.exe --list-devices
```

예상 출력:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: 사전 빌드된 바이너리 다운로드

최신 릴리스 페이지로 이동하여 플랫폼 및 GPU 대상에 맞는 아카이브를 다운로드합니다:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

`llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 파일을 다운로드합니다(여기서 `xxxx`는 빌드 번호입니다).

#### Step 2: 바이너리 압축 해제 및 준비

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

이제 이 디렉터리에는 Ryzen AI Halo 시스템용으로 미리 컴파일된 ROCm 지원 `llama-cli`, `llama-server`, `rpc-server` 빌드가 포함되어 있습니다.

#### Step 3: GPU 감지 확인

```bash
./llama-cli --list-devices
```

예상 출력:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
각 노드에서 llama.cpp 준비가 완료되면 [모델 다운로드하기](#downloading-the-model)로 진행합니다.

### 옵션 2: 수동 소스 빌드

<!-- @os:windows -->
#### Step 1: llama.cpp 빌드

**x64 Native Tools Command Prompt**(Visual Studio Build Tools와 함께 설치됨)를 열고 리포지토리를 클론합니다:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

HIP를 경로에 추가하고 ROCm 및 RPC 지원과 함께 빌드합니다:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 빌드 플래그 | 목적 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm/HIP 소프트웨어 스택을 활성화합니다 |
| `-DGGML_RPC=ON` | 분산 추론을 위한 RPC를 활성화합니다 |
| `-DGPU_TARGETS=gfx1151` | Ryzen AI Halo GPU(Radeon 8060s)를 대상으로 지정합니다 |
| `-G Ninja` | Ninja 빌드 시스템을 사용합니다 |

#### Step 2: GPU 감지 확인

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

예상 출력:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Step 3: 사용자 경로에 HIP 추가

위의 빌드 단계에서는 현재 세션에만 `%HIP_PATH%\bin`을 설정했습니다. HIP 라이브러리를 (x64 Native Tools Command Prompt뿐만 아니라) 모든 터미널에서 사용할 수 있도록 하려면 사용자 `PATH`에 영구적으로 추가하세요:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

각 노드에서 llama.cpp 준비가 완료되면 [모델 다운로드하기](#downloading-the-model)로 진행합니다.
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: llama.cpp 빌드

리포지토리를 클론합니다:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ROCm 및 RPC 지원과 함께 빌드합니다:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 빌드 플래그 | 목적 |
|-----------|---------|
| `-DGGML_HIP=ON` | ROCm 소프트웨어 스택을 활성화합니다 |
| `-DGGML_RPC=ON` | 분산 추론을 위한 RPC를 활성화합니다 |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | AMD GPU에서 향상된 Flash Attention을 위해 rocWMMA를 활성화합니다 |
| `-DAMDGPU_TARGETS="gfx1151"` | Ryzen AI Halo GPU(Radeon 8060s)를 대상으로 지정합니다 |

더 많은 빌드 옵션은 [llama.cpp 빌드 문서](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)를 참고하세요.

#### Step 2: GPU 감지 확인

```bash
cd rocm/bin
./llama-cli --list-devices
```

예상 출력:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

각 노드에서 llama.cpp 준비가 완료되면 [모델 다운로드하기](#downloading-the-model)로 진행합니다.
<!-- @os:end -->

## 모델 다운로드하기

이 플레이북은 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL)의 `Q4_K_XL` 양자화 버전인 3,580억 파라미터 모델 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)을 사용합니다. 이 양자화 수준에서 모델은 약 205GB의 저장 공간을 필요로 하며, 두 개의 Ryzen AI Halo 노드의 결합된 GPU 메모리 안에 들어갑니다.

Hugging Face CLI를 사용하여 GGUF 파일을 다운로드합니다:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **참고**: 모델 다운로드는 반드시 Machine 1(컨트롤러)에서 완료해야 합니다. RPC 워커 노드는 모델 파일의 로컬 사본이 필요하지 않습니다.

## 클러스터에서 모델 실행하기

llama.cpp RPC(원격 프로시저 호출) 엔진을 사용하면 단일 llama.cpp 인스턴스가 네트워크를 통해 모델 레이어를 원격 워커로 오프로드할 수 있습니다. 한 머신은 **컨트롤러**(Machine 1) 역할을 수행하며 토큰화, 스케줄링, 오케스트레이션을 담당합니다. 다른 머신은 경량 **RPC 서버**(Machine 2)를 실행하여 자신의 GPU 메모리와 연산 자원을 컨트롤러에 노출합니다.

로드 시점에 llama.cpp는 모델을 두 노드에 걸쳐 샤딩합니다. 로드가 완료되면 추론은 마치 단일 가속기에서 실행되는 것처럼 진행됩니다. RPC는 백그라운드에서 텐서 전송과 동기화를 처리합니다.

### Step 1: RPC 서버 시작하기(Machine 2)

Machine 2에서 RPC 서버를 시작하여 GPU 리소스를 컨트롤러에 노출합니다:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| 플래그 | 목적 |
|------|---------|
| `-p` | RPC 서버를 브로드캐스트할 포트 |
| `-c` | 모델 로딩 중 반복적인 네트워크 전송을 방지하기 위해 대형 텐서용 로컬 캐시를 활성화합니다 |
| `--host` | RPC 서버를 바인딩할 IP 주소(모든 인터페이스의 경우 `0.0.0.0`) |

더 많은 옵션은 [llama.cpp RPC 문서](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)를 참고하세요.

### Step 2: 모델 실행하기(Machine 1)

Machine 2에서 RPC 서버가 실행 중인 상태에서 `llama-cli` 또는 `llama-server`를 사용하여 Machine 1에서 추론을 실행합니다.

#### llama-cli

`llama-cli`는 모델과 직접 상호작용할 수 있는 터미널 기반 인터페이스를 제공합니다. 벤치마킹, 디버깅, 저수준 실험에 적합합니다.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` 찾기**: Machine 2에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인합니다.
<!-- @os:end -->

<!-- @os:windows -->
> **참고**: 이 명령은 터미널(Powershell)에서 실행하세요.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` 찾기**: Machine 2에서 터미널(Powershell)에서 `ipconfig | findstr /C:"IPv4"`를 실행하여 로컬 IP 주소를 확인합니다.

<!-- @os:end -->

실행되면 `llama-cli`는 모델 로딩 진행 상황을 표시하고 모델과 직접 대화할 수 있는 대화형 프롬프트로 진입합니다:

![두 노드에서 GLM 4.7을 실행하는 llama-cli](assets/llama-cli-example.png)
#### llama-server

`llama-server`는 통합 웹 UI와 OpenAI 호환 HTTP API를 갖춘 지속적인 서버 프로세스를 통해 동일한 추론 엔진을 노출합니다. 이는 장기 실행 배포, 다중 사용자 액세스, 외부 도구와의 통합에 선호되는 인터페이스입니다.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` 찾기**: Machine 2에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인하세요.
<!-- @os:end -->

<!-- @os:windows -->
> **참고**: 이 명령은 터미널(PowerShell)에서 실행하세요.

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` 찾기**: Machine 2에서 터미널(PowerShell)에서 `ipconfig | findstr /C:"IPv4"`를 실행하여 로컬 IP 주소를 확인하세요.
<!-- @os:end -->

시작한 후 브라우저에서 `http://<HOST_IP>:8081`을 열면 내장된 웹 UI에 액세스할 수 있습니다. 이는 모델과 상호작용할 수 있는 브라우저 기반 채팅 인터페이스를 제공합니다:

![두 노드에서 GLM 4.7을 실행하는 llama-server 웹 UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` 찾기**: Machine 1에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인하세요.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` 찾기**: Machine 1에서 터미널(PowerShell)에서 `ipconfig | findstr /C:"IPv4"`를 실행하여 로컬 IP 주소를 확인하세요.
<!-- @os:end -->

#### 매개변수 참조

| 플래그 | 목적 |
|------|---------|
| `-m` | GGUF 모델 파일 경로(첫 번째 샤드 `00001-of-00005` 사용) |
| `-c` | 토큰 단위의 컨텍스트 크기. 값이 클수록 더 많은 메모리를 사용합니다 |
| `-fa on` | AMD GPU에서 향상된 성능을 위해 rocWMMA Flash Attention을 활성화합니다 |
| `-ngl 999` | 모든 모델 레이어를 GPU로 오프로드합니다 |
| `--no-mmap` | 메모리 매핑을 비활성화하여, 모델 크기가 시스템 RAM을 초과하지만 VRAM에는 적합한 경우 로드 시간을 단축합니다 |
| `--host` | `llama-server`를 바인딩할 IP(`llama-server` 전용) |
| `--port` | HTTP API를 제공할 포트(`llama-server` 전용) |
| `--rpc` | 쉼표로 구분된 RPC 워커 엔드포인트 목록(`IP:port`) |

전체 매개변수 사용법은 [llama-cli 문서](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) 및 [llama-server 문서](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)를 참조하세요.

## 다음 단계

- **타사 애플리케이션 연결**: `llama-server`는 OpenAI 호환 API를 노출합니다. OpenAI 호환 애플리케이션(예: Open WebUI)을 `http://<HOST_IP>:8081`로 지정하고 임의의 자리 표시자 API 키(예: `none`)를 사용하여 클러스터에 연결하세요
- **다른 모델 탐색**: [Hugging Face](https://huggingface.co/models?search=gguf)에서 양자화된 GGUF를 검색하여 클러스터의 결합된 GPU 메모리에 맞는 모델을 찾아보세요
- **4개 노드로 확장**: 추가 RPC 워커로 Ryzen AI Halo 시스템 두 대를 더 추가하여 1조 매개변수 규모의 모델에 액세스하세요. `--rpc`에 쉼표로 구분된 목록 형태로 추가 엔드포인트를 전달하세요(예: `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)