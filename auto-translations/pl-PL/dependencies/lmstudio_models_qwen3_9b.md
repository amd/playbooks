<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu Qwen3.5 9B w LM Studio

Aby pobrać model Qwen3.5 9B:

1. Naciśnij "Ctrl" + "Shift" + "M" na klawiaturze lub kliknij zakładkę "Discover" (ikona lupy) na lewym pasku bocznym
2. Wyszukaj `Qwen3.5 9B`
3. Wybierz kwantyzację (zalecana `Q4_K_M` zapewnia dobrą równowagę między rozmiarem a jakością) i kliknij Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio automatycznie pobierze model i umieści go we właściwym katalogu.

Jeśli chcesz pobrać dodatkowe modele, możesz wyszukać je w zakładce Discover, a LM Studio zajmie się resztą.

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