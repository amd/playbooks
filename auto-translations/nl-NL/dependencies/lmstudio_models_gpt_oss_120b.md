<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Downloaden van GPT-OSS 120B op LM Studio

<!-- @device:halo_box -->
> **Opmerking:** Als dit model al beschikbaar is in LM Studio, kunt u deze sectie overslaan. Volg anders de onderstaande stappen om het te downloaden.
<!-- @device:end -->

Om het GPT-OSS 120B model te downloaden:

1. Druk op "Ctrl" + "Shift" + "M" op uw toetsenbord of klik op het tabblad "Discover" (vergrootglas-icoon) in de linker zijbalk
2. Zoek naar `ggml-org/gpt-oss-120b-GGUF`
3. Selecteer `mxfp4` en klik op Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio downloadt het model automatisch en plaatst het in de juiste map.

Als u aanvullende modellen wilt downloaden, kunt u ernaar zoeken in het tabblad Discover en LM Studio handelt de rest af.

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