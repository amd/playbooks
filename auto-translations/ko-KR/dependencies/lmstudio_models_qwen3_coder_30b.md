<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio에서 Qwen3-Coder 30B 다운로드하기

Qwen3-Coder 30B 모델을 다운로드하려면:

1. 키보드에서 "Ctrl" + "Shift" + "M"을 누르거나 왼쪽 사이드바에서 "Discover" 탭(돋보기 아이콘)을 클릭합니다
2. `Qwen3-Coder-30B-A3B`를 검색합니다
3. 양자화 방식을 선택하고(권장되는 `Q4_K_M`이 크기와 품질 면에서 균형이 좋습니다) Download를 클릭합니다

LM Studio가 자동으로 모델을 다운로드하여 올바른 디렉터리에 배치합니다.

추가 모델을 다운로드하고 싶다면 Discover 탭에서 검색하면 LM Studio가 나머지를 처리해 줍니다.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->