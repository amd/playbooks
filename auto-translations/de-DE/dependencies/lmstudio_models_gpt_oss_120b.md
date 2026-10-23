<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von GPT-OSS 120B in LM Studio

<!-- @device:halo_box -->
> **Hinweis:** Wenn dieses Modell bereits in LM Studio verfügbar ist, können Sie diesen Abschnitt überspringen. Andernfalls folgen Sie den nachstehenden Schritten, um es herunterzuladen.
<!-- @device:end -->

So laden Sie das Modell GPT-OSS 120B herunter:

1. Drücken Sie "Strg" + "Umschalt" + "M" auf Ihrer Tastatur oder klicken Sie auf die Registerkarte "Discover" (Lupensymbol) in der linken Seitenleiste
2. Suchen Sie nach `ggml-org/gpt-oss-120b-GGUF`
3. Wählen Sie `mxfp4` aus und klicken Sie auf Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio lädt das Modell automatisch herunter und legt es im richtigen Verzeichnis ab.

Falls Sie weitere Modelle herunterladen möchten, können Sie diese in der Registerkarte "Discover" suchen, und LM Studio übernimmt den Rest.

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