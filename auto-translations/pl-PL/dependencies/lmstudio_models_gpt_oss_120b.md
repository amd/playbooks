<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie GPT-OSS 120B w LM Studio

Aby pobrać model GPT-OSS 120B:

1. Naciśnij "Ctrl" + "Shift" + "M" na klawiaturze lub kliknij zakładkę "Discover" (ikona lupy) na lewym pasku bocznym
2. Wyszukaj `ggml-org/gpt-oss-120b-GGUF`
3. Wybierz `mxfp4` i kliknij Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio automatycznie pobierze model i umieści go we właściwym katalogu.

Jeśli chcesz pobrać dodatkowe modele, możesz wyszukać je w zakładce Discover, a LM Studio zajmie się resztą.

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