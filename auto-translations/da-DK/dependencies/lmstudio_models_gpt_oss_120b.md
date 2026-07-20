<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af GPT-OSS 120B i LM Studio

Sådan downloader du GPT-OSS 120B-modellen:

1. Tryk på "Ctrl" + "Shift" + "M" på tastaturet, eller klik på fanen "Discover" (forstørrelsesglas-ikonet) i venstre sidepanel
2. Søg efter `ggml-org/gpt-oss-120b-GGUF`
3. Vælg `mxfp4`, og klik på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio downloader automatisk modellen og placerer den i den korrekte mappe.

Hvis du ønsker at downloade yderligere modeller, kan du søge efter dem i fanen Discover, og LM Studio klarer resten.

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