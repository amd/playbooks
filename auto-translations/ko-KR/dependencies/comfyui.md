<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. [download.comfy.org](https://download.comfy.org/windows/nsis/x64)에서 최신 Windows ComfyUI 설치 프로그램을 다운로드합니다.
2. 하드웨어 설정을 선택합니다: `AMD ROCm`을 선택하세요.
3. ComfyUI를 설치할 위치를 선택합니다: 기본 경로 또는 원하는 폴더를 사용하세요.
4. 데스크톱 앱 설정: 권장 버전을 사용하고 있는지 확인하기 위해 "Automatic Updates"를 선택 해제하는 것을 권장합니다.
5. "Next"를 눌러 설치를 시작합니다.

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUI 복제
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