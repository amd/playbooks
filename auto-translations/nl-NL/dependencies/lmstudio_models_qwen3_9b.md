<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3.5 9B downloaden in LM Studio

Om het Qwen3.5 9B-model te downloaden:

1. Druk op "Ctrl" + "Shift" + "M" op uw toetsenbord of klik op het tabblad "Discover" (vergrootglaspictogram) in de linker zijbalk
2. Zoek naar `Qwen3.5 9B`
3. Selecteer een kwantisering (de aanbevolen `Q4_K_M` is een goede balans tussen grootte en kwaliteit) en klik op Downloaden

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio downloadt het model automatisch en plaatst het in de juiste map.

Als u aanvullende modellen wilt downloaden, kunt u ernaar zoeken in het tabblad Discover en LM Studio regelt de rest.

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