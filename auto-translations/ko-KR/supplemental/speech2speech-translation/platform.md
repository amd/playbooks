<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위한 예상 플랫폼 구성을 설명합니다.

## 사전 요구 사항

ROCm을 지원하는 PyTorch는 AMD Ryzen™ AI Halo Developer Platform에 사전 설치되어 있습니다. 그 외 모든 디바이스에서는 사용자가 ROCm을 지원하는 PyTorch를 직접 설치해야 합니다. 사용 중인 운영 체제에 해당하는 섹션을 참조하시기 바랍니다:

### Windows

| 구성 요소     | 버전         | 참고             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 이상    | AMD Ryzen AI Halo Developer Platform에 사전 설치되어 있으며, 그 외 모든 디바이스에서는 수동으로 설치해야 함 |

### Linux

| 구성 요소     | 버전         | 참고             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 이상    | AMD Ryzen AI Halo Developer Platform에 사전 설치되어 있으며, 그 외 모든 디바이스에서는 수동으로 설치해야 함 |

## 필수 모델

다음 모델은 사용 중인 플랫폼에 대해 테스트 및 최적화되어 있습니다:

| 모델 | 파라미터 | 크기 | 다운로드 위치 |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | AMD Ryzen AI Halo Developer Platform에 사전 설치되어 있으며, 그 외 모든 디바이스에서는 수동으로 설치해야 함 |

모델은 Hugging Face 캐시 디렉터리에 자동으로 다운로드됩니다:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

모델 저장을 위해 최소 **20GB의 여유 공간**을 확보하시기 바랍니다.

## 네트워크 요구 사항

초기 설정 시 Hugging Face에서 모델을 다운로드하기 위해 인터넷 액세스가 필요합니다. 다운로드가 완료된 후에는 플레이북을 오프라인으로 실행할 수 있습니다.

- 최초 모델 다운로드는 모델 크기와 연결 속도에 따라 **5~10분** 정도 소요될 수 있습니다
- 모델은 로컬에 캐시되며 다시 다운로드할 필요가 없습니다