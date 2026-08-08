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

## 필수 앱/프레임워크

### Windows/Linux

GAIA는 [GAIA 설치 가이드](../../dependencies/gaia.md)에 제공된 지침에 따라 사전 설치되어 있어야 합니다.

Lemonade Server는 [Lemonade 설치 가이드](../../dependencies/lemonade.md)에 제공된 지침에 따라 사전 설치되어 있어야 합니다.

## 필수 모델

### Windows/Linux

Hardware Advisor Agent는 에이전트 추론을 위해 **Qwen3-Coder-30B**를 사용합니다. 이 모델은 `gaia init` 실행 시 자동으로 다운로드됩니다. 수동으로 모델을 다운로드할 필요는 없습니다.