<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos Qwen3-Coder 30B v LM Studio

Za prenos modela Qwen3-Coder 30B:

1. Pritisnite "Ctrl" + "Shift" + "M" na tipkovnici ali kliknite na zavihek "Discover" (ikona povečevalnega stekla) v levi stranski vrstici
2. Poiščite `Qwen3-Coder-30B-A3B`
3. Izberite kvantizacijo (priporočena `Q4_K_M` je dobro ravnovesje med velikostjo in kakovostjo) in kliknite Download

LM Studio bo samodejno prenesel model in ga postavil v ustrezen imenik.

Če želite prenesti dodatne modele, jih lahko poiščete v zavihku Discover, LM Studio pa bo poskrbel za preostalo.

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