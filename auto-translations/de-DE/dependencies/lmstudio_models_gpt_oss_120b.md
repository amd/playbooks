<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B in LM Studio herunterladen

So laden Sie das GPT-OSS 120B-Modell herunter:

1. Drücken Sie „Strg" + „Umschalt" + „M" auf Ihrer Tastatur oder klicken Sie in der linken Seitenleiste auf die Registerkarte „Discover" (Lupensymbol)
2. Suchen Sie nach `ggml-org/gpt-oss-120b-GGUF`
3. Wählen Sie `mxfp4` aus und klicken Sie auf „Download"

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio lädt das Modell automatisch herunter und legt es im richtigen Verzeichnis ab.

Wenn Sie weitere Modelle herunterladen möchten, können Sie in der Registerkarte „Discover" danach suchen, und LM Studio erledigt den Rest.

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