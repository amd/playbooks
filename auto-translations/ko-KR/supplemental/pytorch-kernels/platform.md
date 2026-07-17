<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위한 예상 플랫폼 구성을 설명합니다.

## 필수 앱 / 프레임워크

| 구성 요소       | 예상 구성                               | 참고                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | `venv` 지원이 포함된 Python         | `kernel-env` 생성 및 활성화에 사용됨                                     |
| ROCm Python SDK | ROCm 7.13 패키지 패밀리             | 플레이북 의존성 흐름을 통해 설치됨                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`, HIP 런타임, JIT 컴파일 및 `CUDAExtension`에 필요 |
| GPU Driver      | ROCm/HIP 지원이 포함된 AMD GPU 드라이버 | PyTorch가 AMD GPU를 감지하기 전에 필요                               |

> 참고: AMD Ryzen™ AI Halo 개발자 플랫폼에서 실행 중인 경우, AMD ROCm™ 소프트웨어와 PyTorch가 사전 설치되어 있습니다.

## Linux 사전 요구 사항

다음 시스템 패키지가 필요합니다:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv`는 `kernel-env`를 생성하는 데 필요합니다.
* `build-essential`, `gcc`, `g++`는 C++ 확장 연습에 필요합니다.
* `amd-smi`는 Linux GPU 가시성/사용률 확인에 사용됩니다.

C++ 확장 예제는 PyTorch의 `CUDAExtension` 경로를 사용하여 `.cu` 파일에서 네이티브 `.so` 모듈을 빌드합니다.

## Windows 사전 요구 사항

Windows 실행 환경에는 다음이 필요합니다:

* `python`을 통해 Python 사용 가능
* 최신 버전 설치: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* **C++를 사용한 데스크톱 개발** 워크로드가 포함된 [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 또는 [최신 버전](https://visualstudio.microsoft.com/vs/community/)

Visual Studio C++ 환경은 다음을 제공해야 합니다:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK 포함 및 라이브러리 경로

C++ 확장 예제는 PyTorch의 `CUDAExtension` 경로를 사용하여 `.cu` 파일에서 네이티브 `.pyd` 모듈을 빌드합니다.