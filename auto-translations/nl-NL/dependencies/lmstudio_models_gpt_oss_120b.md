<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B downloaden in LM Studio

Om het GPT-OSS 120B-model te downloaden:

1. Druk op "Ctrl" + "Shift" + "M" op uw toetsenbord of klik op het tabblad "Discover" (vergrootglaspictogram) in de linker zijbalk
2. Zoek naar `ggml-org/gpt-oss-120b-GGUF`
3. Selecteer `mxfp4` en klik op Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio zal het model automatisch downloaden en in de juiste map plaatsen.

Als u aanvullende modellen wilt downloaden, kunt u ernaar zoeken in het tabblad Discover en LM Studio regelt de rest.

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