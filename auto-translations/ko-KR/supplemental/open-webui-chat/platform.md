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

## 필수 앱/프레임워크

### Windows/Linux
Lemonade는 [여기](https://lemonade-server.ai/install_options.html)에서 사전 설치되어야 합니다.

- **Open WebUI** (프론트엔드 웹 앱)
- **Lemonade Server** (백엔드 모델 서버)

> 이 플레이북은 **Lemonade**(Lemonade server/app)를 **네이티브**로 실행합니다. **Open WebUI**는 Linux에서는 (Podman을 통해) **컨테이너**로, Windows에서는 **Python 패키지**로 실행됩니다. `open-webui` PyPI 패키지는 Python ≤ 3.12만 지원하므로, Linux 컨테이너를 사용하면 이전 Python 버전을 관리할 필요가 없습니다.

## 모델 (Lemonade 내)

모델은 **Lemonade 앱** 내에서 (내장된 Model Manager를 사용하여) 다운로드하거나, Lemonade의 모델 관리 명령어(`lemonade pull <model_name>`)를 통해 다운로드해야 합니다. 이 플레이북은 아래 권장 모델이 다운로드되어 모델 목록 엔드포인트에 표시되어 있다고 가정합니다.

모델 가용성 확인:
- 열기: `http://localhost:13305/api/v1/models`
- 다운로드된 모델은 `"data"` 아래에 나열됩니다.

### 권장 모델

| 기능 | 모델 ID | 참고 사항 |
|---|----|-----|
| LLM (텍스트 입력 → 텍스트 출력) | `Qwen3-4B-Hybrid` (또는 유사 모델) | 채팅, 텍스트 완성, 코딩 또는 추론을 위한 모든 Lemonade LLM 모델 |
| VLM (이미지 → 텍스트) | `Qwen3.5-4B-GGUF` (또는 **Vision** 카테고리에 속한 모델) | 이미지를 입력의 일부로 받을 수 있는 모든 멀티모달/비전 지원 모델 |
| 이미지 생성 (텍스트 → 이미지) | `SDXL-Turbo` (또는 **Image** 카테고리에 속한 모델) | 텍스트 프롬프트에 대해 이미지를 생성하는 모든 Stable Diffusion 모델 |
| 오디오 (음성 → 텍스트) | `Whisper-Large-v3` (또는 **Audio** 카테고리에 속한 모델) | 오디오를 텍스트로 변환하는 모든 ASR 모델 |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 사용되는 포트

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

이 포트들이 시스템에서 이미 사용 중인 경우, 서버를 시작할 때 변경하십시오.