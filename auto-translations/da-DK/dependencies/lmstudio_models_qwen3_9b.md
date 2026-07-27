<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Sådan downloader du Qwen3.5 9B i LM Studio

Sådan downloader du Qwen3.5 9B-modellen:

1. Tryk på "Ctrl" + "Shift" + "M" på tastaturet, eller klik på fanen "Discover" (ikonet med forstørrelsesglasset) i venstre sidebjælke
2. Søg efter `Qwen3.5 9B`
3. Vælg en kvantisering (den anbefalede `Q4_K_M` giver en god balance mellem størrelse og kvalitet), og klik på Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio downloader automatisk modellen og placerer den i den korrekte mappe.

Hvis du ønsker at downloade flere modeller, kan du søge efter dem i fanen Discover, så klarer LM Studio resten.

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