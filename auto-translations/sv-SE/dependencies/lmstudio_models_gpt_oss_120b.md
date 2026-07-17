<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner GPT-OSS 120B i LM Studio

För att ladda ner GPT-OSS 120B-modellen:

1. Tryck på "Ctrl" + "Shift" + "M" på tangentbordet eller klicka på fliken "Discover" (förstoringsglas-ikonen) i vänster sidofält
2. Sök efter `ggml-org/gpt-oss-120b-GGUF`
3. Välj `mxfp4` och klicka på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio laddar automatiskt ner och placerar modellen i rätt katalog.

Om du vill ladda ner ytterligare modeller kan du söka efter dem i fliken Discover och LM Studio hanterar resten.

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