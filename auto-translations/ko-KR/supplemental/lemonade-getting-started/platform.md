<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

# 플랫폼 구성 — Lemonade Local AI

이 문서는 이 플레이북에서 전제로 하는 사전 설치 소프트웨어, 모델 경로, 플랫폼별 필수 조건을 설명합니다.

## 사전 설치 소프트웨어

| 소프트웨어 | 버전 | 용도 |
|----------|---------|---------|
| Lemonade Server | 최신 릴리스 | OpenAI 호환 API를 제공하는 로컬 LLM 서버 |
| Python | 3.10–3.13 | OpenAI Python 클라이언트 예제에 필요 |

## 기본 모델 저장 위치

Lemonade를 통해 다운로드한 모델은 Hugging Face Hub 사양을 사용하여 저장됩니다:

| 플랫폼 | 기본 경로 |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

저장 위치를 변경하려면 `HF_HOME` 환경 변수를 설정하세요.

## 하드웨어 요구 사항

| 하드웨어 대상 | 요구 사항 |
|----------------|-------------|
| **CPU** | 최신 x86-64 프로세서(AMD 또는 Intel) 모두 지원 |
| **GPU (Vulkan)** | Vulkan 드라이버를 지원하는 모든 GPU |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 시리즈 또는 Radeon PRO W7000 시리즈; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 시리즈 프로세서, Windows 11 |

## 네트워크 요구 사항

- 최초 모델 다운로드 시 인터넷 연결 필요(모델에 따라 1~25GB)
- 모델 다운로드 후에는 인터넷 연결이 필요하지 않음