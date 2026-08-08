<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위해 예상되는 플랫폼 구성을 설명합니다.

## 필수 앱 / 프레임워크

| 구성 요소       | 예상 구성               | 참고                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | `venv`를 지원하는 Python         | `kernel-env`를 생성하고 활성화하는 데 사용                                     |
| ROCm Python SDK | ROCm 7.13 패키지 제품군             | 플레이북 종속성 흐름을 통해 설치됨                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`, HIP 런타임, JIT 컴파일, `CUDAExtension`에 필요 |
| GPU 드라이버      | ROCm/HIP를 지원하는 AMD GPU 드라이버 | PyTorch가 AMD GPU를 감지하기 전에 필요                               |

> 참고: AMD Ryzen™ AI Halo Developer Platform에서 실행 중인 경우, AMD ROCm™ 소프트웨어와 PyTorch가 사전 설치되어 있습니다.

## Linux 필수 조건

다음 시스템 패키지가 필요합니다:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `kernel-env`를 생성하려면 `python3-venv`가 필요합니다.
* C++ 확장 안내서를 위해 `build-essential`, `gcc`, `g++`가 필요합니다.
* `amd-smi`는 Linux GPU 가시성/사용률 확인에 사용됩니다.

C++ 확장 예제는 PyTorch의 `CUDAExtension` 경로를 사용하여 `.cu` 파일로부터 네이티브 `.so` 모듈을 빌드합니다.

## Windows 필수 조건

Windows 러너에는 다음이 필요합니다:

* `python`을 통해 사용 가능한 Python
* 최신 버전 설치: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* **Desktop development with C++** 워크로드가 포함된 [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 또는 [최신 버전](https://visualstudio.microsoft.com/vs/community/)

Visual Studio C++ 환경은 다음을 제공해야 합니다:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK 포함 및 라이브러리 경로

C++ 확장 예제는 PyTorch의 `CUDAExtension` 경로를 사용하여 `.cu` 파일로부터 네이티브 `.pyd` 모듈을 빌드합니다.