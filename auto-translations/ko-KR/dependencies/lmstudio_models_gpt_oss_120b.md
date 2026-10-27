<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B을 LM Studio에서 다운로드하기

<!-- @device:halo_box -->
> **참고:** 이 모델이 이미 LM Studio에서 사용 가능하다면 이 섹션을 건너뛸 수 있습니다. 그렇지 않다면 아래 단계를 따라 다운로드하세요.
<!-- @device:end -->

GPT-OSS 120B 모델을 다운로드하려면:

1. 키보드에서 "Ctrl" + "Shift" + "M"을 누르거나 왼쪽 사이드바에서 "Discover" 탭(돋보기 아이콘)을 클릭합니다
2. `ggml-org/gpt-oss-120b-GGUF`를 검색합니다
3. `mxfp4`를 선택하고 Download를 클릭합니다

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio가 자동으로 모델을 다운로드하여 올바른 디렉터리에 배치합니다.

추가 모델을 다운로드하고 싶다면 Discover 탭에서 검색할 수 있으며, 나머지는 LM Studio가 처리합니다.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->