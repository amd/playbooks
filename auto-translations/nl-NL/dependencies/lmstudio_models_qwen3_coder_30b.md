<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3-Coder 30B downloaden op LM Studio

Om het Qwen3-Coder 30B-model te downloaden:

1. Druk op "Ctrl" + "Shift" + "M" op je toetsenbord of klik op het tabblad "Discover" (vergrootglas-icoon) in de linkerzijbalk
2. Zoek naar `Qwen3-Coder-30B-A3B`
3. Selecteer een quantisatie (de aanbevolen `Q4_K_M` biedt een goede balans tussen grootte en kwaliteit) en klik op Download

LM Studio zal het model automatisch downloaden en in de juiste map plaatsen.

Mocht je aanvullende modellen willen downloaden, kun je ernaar zoeken in het tabblad Discover en LM Studio regelt de rest.

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