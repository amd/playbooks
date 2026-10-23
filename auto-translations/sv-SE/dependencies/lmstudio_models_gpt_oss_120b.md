<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Nedladdning av GPT-OSS 120B i LM Studio

<!-- @device:halo_box -->
> **Obs!** Om den här modellen redan är tillgänglig i LM Studio kan du hoppa över det här avsnittet. Följ annars stegen nedan för att ladda ner den.
<!-- @device:end -->

För att ladda ner modellen GPT-OSS 120B:

1. Tryck på "Ctrl" + "Shift" + "M" på tangentbordet eller klicka på fliken "Discover" (förstoringsglas-ikonen) i det vänstra sidofältet
2. Sök efter `ggml-org/gpt-oss-120b-GGUF`
3. Välj `mxfp4` och klicka på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio laddar automatiskt ner och placerar modellen i rätt katalog.

Om du vill ladda ner ytterligare modeller kan du söka efter dem i fliken Discover, så sköter LM Studio resten.

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