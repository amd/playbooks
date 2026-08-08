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

### Windows

| 구성 요소 | 버전 | 참고 사항 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Developer Platform에는 사전 설치되어 PATH에서 사용 가능하지만, 다른 모든 장치에서는 수동으로 설치해야 합니다 |
| **Lemonade Server** | latest | `http://localhost:13305/api/v1`에서 실행 중 |

### Linux

| 구성 요소 | 버전 | 참고 사항 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Developer Platform에는 사전 설치되어 PATH에서 사용 가능하지만, 다른 모든 장치에서는 수동으로 설치해야 합니다 |
| **Lemonade Server** | latest | `http://localhost:13305/api/v1`에서 실행 중 |


## Lemonade LLM

Lemonade 서버는 장치에 적합한 모델이 로드된 상태로 실행되어야 합니다(사용 중인 장치의 `lemonade run` 명령은 README를 참조하세요):

| 장치 | 엔드포인트 | 모델 |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |