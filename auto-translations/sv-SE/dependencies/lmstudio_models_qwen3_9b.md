<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner Qwen3.5 9B i LM Studio

Så här laddar du ner modellen Qwen3.5 9B:

1. Tryck på "Ctrl" + "Shift" + "M" på tangentbordet eller klicka på fliken "Discover" (förstoringsglasikonen) i sidofältet till vänster
2. Sök efter `Qwen3.5 9B`
3. Välj en kvantisering (den rekommenderade `Q4_K_M` ger en bra balans mellan storlek och kvalitet) och klicka på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio laddar automatiskt ner modellen och placerar den i rätt katalog.

Om du vill ladda ner ytterligare modeller kan du söka efter dem på fliken Discover, så tar LM Studio hand om resten.

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