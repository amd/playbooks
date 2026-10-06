<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von Qwen3-Coder 30B in LM Studio

So laden Sie das Qwen3-Coder 30B Modell herunter:

1. Drücken Sie „Strg“ + „Umschalt“ + „M“ auf Ihrer Tastatur oder klicken Sie auf die Registerkarte „Discover“ (Lupensymbol) in der linken Seitenleiste
2. Suchen Sie nach `Qwen3-Coder-30B-A3B`
3. Wählen Sie eine Quantisierung aus (die empfohlene `Q4_K_M` bietet eine gute Balance zwischen Größe und Qualität) und klicken Sie auf Download

LM Studio lädt das Modell automatisch herunter und legt es im richtigen Verzeichnis ab.

Falls Sie weitere Modelle herunterladen möchten, können Sie diese in der Registerkarte „Discover“ suchen, und LM Studio übernimmt den Rest.

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