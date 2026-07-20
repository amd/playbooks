<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 플랫폼 구성

이 문서는 이 플레이북을 실행하기 위한 예상 플랫폼 구성을 설명합니다.

## 필수 앱/프레임워크

### Windows/Linux

GAIA는 [GAIA 설치 가이드](../../dependencies/gaia.md)에 제공된 지침에 따라 사전 설치되어 있어야 합니다.

Lemonade Server는 [Lemonade 설치 가이드](../../dependencies/lemonade.md)에 제공된 지침에 따라 사전 설치되어 있어야 합니다.

## 필수 모델

### Windows/Linux

Hardware Advisor Agent는 에이전트 추론을 위해 **Qwen3-Coder-30B**를 사용합니다. 이 모델은 `gaia init` 실행 시 자동으로 다운로드됩니다. 수동으로 모델을 다운로드할 필요는 없습니다.