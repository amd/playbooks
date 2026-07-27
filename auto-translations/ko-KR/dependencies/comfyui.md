<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. [download.comfy.org](https://download.comfy.org/windows/nsis/x64)에서 최신 Windows ComfyUI 설치 프로그램을 다운로드합니다.
2. 하드웨어 설정 선택: `AMD ROCm`을 선택합니다.
3. ComfyUI를 설치할 위치 선택: 기본 경로를 사용하거나 원하는 폴더를 사용합니다.
4. Desktop App 설정: 권장 버전의 앱을 사용하도록 "Automatic Updates"의 선택을 해제하는 것을 권장합니다.
5. 설치를 시작하려면 "Next"를 누릅니다.

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUI 클론
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (선택 사항) 특정 버전 체크아웃
```bash
git checkout v0.19.2
```

#### ComfyUI 요구 사항 설치

Python 가상 환경이 활성화된 상태에서 다음을 실행합니다:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **참고**: 자세한 내용은 [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI)를 참조하세요.

<!-- @os:end -->