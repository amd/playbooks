<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu Qwen3-Coder 30B w LM Studio

Aby pobrać model Qwen3-Coder 30B:

1. Naciśnij "Ctrl" + "Shift" + "M" na klawiaturze lub kliknij kartę "Discover" (ikona lupy) na lewym pasku bocznym
2. Wyszukaj `Qwen3-Coder-30B-A3B`
3. Wybierz kwantyzację (zalecana `Q4_K_M` zapewnia dobrą równowagę między rozmiarem a jakością) i kliknij Download

LM Studio automatycznie pobierze model i umieści go we właściwym katalogu.

Jeśli chcesz pobrać dodatkowe modele, możesz wyszukać je w karcie Discover, a LM Studio zajmie się resztą.

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