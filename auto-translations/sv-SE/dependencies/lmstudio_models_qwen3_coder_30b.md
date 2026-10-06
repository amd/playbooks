<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner Qwen3-Coder 30B i LM Studio

Så här laddar du ner modellen Qwen3-Coder 30B:

1. Tryck på "Ctrl" + "Shift" + "M" på tangentbordet eller klicka på fliken "Discover" (förstoringsglasikonen) i sidofältet till vänster
2. Sök efter `Qwen3-Coder-30B-A3B`
3. Välj en kvantisering (den rekommenderade `Q4_K_M` är en bra balans mellan storlek och kvalitet) och klicka på Download

LM Studio laddar automatiskt ner och placerar modellen i rätt katalog.

Om du vill ladda ner fler modeller kan du söka efter dem i fliken Discover, så sköter LM Studio resten.

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