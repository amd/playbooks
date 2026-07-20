<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos modela Qwen3.5 9B v LM Studio

Za prenos modela Qwen3.5 9B:

1. Pritisnite "Ctrl" + "Shift" + "M" na tipkovnici ali kliknite na zavihek "Discover" (ikona povečevalnega stekla) v levi stranski vrstici
2. Poiščite `Qwen3.5 9B`
3. Izberite kvantizacijo (priporočena `Q4_K_M` predstavlja dobro ravnovesje med velikostjo in kakovostjo) in kliknite Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio bo samodejno prenesel model in ga postavil v ustrezno mapo.

Če želite prenesti dodatne modele, jih lahko poiščete v zavihku Discover, LM Studio pa bo poskrbel za preostalo.

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