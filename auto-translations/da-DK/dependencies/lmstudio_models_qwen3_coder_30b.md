<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af Qwen3-Coder 30B i LM Studio

For at downloade Qwen3-Coder 30B-modellen:

1. Tryk på "Ctrl" + "Shift" + "M" på dit tastatur, eller klik på fanen "Discover" (forstørrelsesglas-ikon) i venstre sidebjælke
2. Søg efter `Qwen3-Coder-30B-A3B`
3. Vælg en kvantisering (den anbefalede `Q4_K_M` giver en god balance mellem størrelse og kvalitet), og klik på Download

LM Studio downloader automatisk modellen og placerer den i den korrekte mappe.

Hvis du ønsker at downloade yderligere modeller, kan du søge efter dem under fanen Discover, og LM Studio klarer resten.

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