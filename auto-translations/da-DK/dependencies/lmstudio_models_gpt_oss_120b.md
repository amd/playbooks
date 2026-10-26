<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af GPT-OSS 120B i LM Studio

<!-- @device:halo_box -->
> **Bemærk:** Hvis denne model allerede er tilgængelig i LM Studio, kan du springe dette afsnit over. Følg ellers trinene nedenfor for at downloade den.
<!-- @device:end -->

For at downloade GPT-OSS 120B-modellen:

1. Tryk på "Ctrl" + "Shift" + "M" på dit tastatur, eller klik på fanen "Discover" (forstørrelsesglas-ikonet) i venstre sidebjælke
2. Søg efter `ggml-org/gpt-oss-120b-GGUF`
3. Vælg `mxfp4`, og klik på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio downloader automatisk modellen og placerer den i den korrekte mappe.

Hvis du ønsker at downloade yderligere modeller, kan du søge efter dem under fanen Discover, og LM Studio klarer resten.

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