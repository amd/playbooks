<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio에서 Qwen3.5 9B 다운로드하기

Qwen3.5 9B 모델을 다운로드하려면:

1. 키보드에서 "Ctrl" + "Shift" + "M"을 누르거나 왼쪽 사이드바의 "Discover" 탭(돋보기 아이콘)을 클릭합니다
2. `Qwen3.5 9B`를 검색합니다
3. 양자화 방식을 선택하고(권장 사항인 `Q4_K_M`은 크기와 품질의 균형이 좋습니다) 다운로드를 클릭합니다

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio가 자동으로 모델을 다운로드하여 올바른 디렉터리에 배치합니다.

추가 모델을 다운로드하려면 Discover 탭에서 검색하면 LM Studio가 나머지를 처리합니다.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->