<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

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