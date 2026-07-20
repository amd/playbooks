<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von Qwen3.5 9B in LM Studio

So laden Sie das Qwen3.5 9B-Modell herunter:

1. Drücken Sie „Strg“ + „Umschalt“ + „M“ auf Ihrer Tastatur oder klicken Sie auf die Registerkarte „Discover“ (Lupensymbol) in der linken Seitenleiste
2. Suchen Sie nach `Qwen3.5 9B`
3. Wählen Sie eine Quantisierung aus (die empfohlene `Q4_K_M` bietet ein gutes Gleichgewicht zwischen Größe und Qualität) und klicken Sie auf Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio lädt das Modell automatisch herunter und legt es im richtigen Verzeichnis ab.

Wenn Sie weitere Modelle herunterladen möchten, können Sie diese in der Registerkarte „Discover“ suchen, und LM Studio übernimmt den Rest.

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