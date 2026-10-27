<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hämta GPT-OSS 120B i LM Studio

<!-- @device:halo_box -->
> **Obs!** Om den här modellen redan finns tillgänglig i LM Studio kan du hoppa över det här avsnittet. Annars följer du stegen nedan för att hämta den.
<!-- @device:end -->

Så här hämtar du modellen GPT-OSS 120B:

1. Tryck på "Ctrl" + "Shift" + "M" på tangentbordet eller klicka på fliken "Discover" (förstoringsglas-ikonen) i sidofältet till vänster
2. Sök efter `ggml-org/gpt-oss-120b-GGUF`
3. Välj `mxfp4` och klicka på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio hämtar automatiskt modellen och placerar den i rätt katalog.

Om du vill hämta fler modeller kan du söka efter dem på fliken Discover, så sköter LM Studio resten.

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