<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Laste ned Qwen3-Coder 30B i LM Studio

Slik laster du ned Qwen3-Coder 30B-modellen:

1. Trykk "Ctrl" + "Shift" + "M" på tastaturet, eller klikk på "Discover"-fanen (forstørrelsesglass-ikonet) i venstre sidefelt
2. Søk etter `Qwen3-Coder-30B-A3B`
3. Velg en kvantisering (den anbefalte `Q4_K_M` gir en god balanse mellom størrelse og kvalitet), og klikk Download

LM Studio vil automatisk laste ned modellen og plassere den i riktig mappe.

Hvis du ønsker å laste ned flere modeller, kan du søke etter dem i Discover-fanen, så håndterer LM Studio resten.

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