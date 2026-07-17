<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Laste ned GPT-OSS 120B i LM Studio

For å laste ned GPT-OSS 120B-modellen:

1. Trykk "Ctrl" + "Shift" + "M" på tastaturet, eller klikk på "Discover"-fanen (forstørrelsesglassikon) i venstre sidefelt
2. Søk etter `ggml-org/gpt-oss-120b-GGUF`
3. Velg `mxfp4` og klikk Last ned

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio vil automatisk laste ned og plassere modellen i riktig mappe.

Hvis du ønsker å laste ned flere modeller, kan du søke etter dem i Discover-fanen, og LM Studio vil håndtere resten.

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