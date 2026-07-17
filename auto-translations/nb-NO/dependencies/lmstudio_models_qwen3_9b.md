<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Nedlasting av Qwen3.5 9B i LM Studio

For å laste ned Qwen3.5 9B-modellen:

1. Trykk "Ctrl" + "Shift" + "M" på tastaturet, eller klikk på "Discover"-fanen (forstørrelsesglassikon) i venstre sidefelt
2. Søk etter `Qwen3.5 9B`
3. Velg en kvantisering (den anbefalte `Q4_K_M` er en god balanse mellom størrelse og kvalitet) og klikk Last ned

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio vil automatisk laste ned og plassere modellen i riktig mappe.

Hvis du ønsker å laste ned flere modeller, kan du søke etter dem i Discover-fanen, og LM Studio vil håndtere resten.

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