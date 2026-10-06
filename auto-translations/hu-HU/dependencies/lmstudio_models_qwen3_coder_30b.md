<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3-Coder 30B letöltése az LM Studio-ban

A Qwen3-Coder 30B modell letöltéséhez:

1. Nyomja meg a "Ctrl" + "Shift" + "M" billentyűkombinációt, vagy kattintson a bal oldali oldalsávon található "Discover" fülre (nagyítóüveg ikon)
2. Keressen rá a `Qwen3-Coder-30B-A3B` kifejezésre
3. Válasszon egy kvantálást (az ajánlott `Q4_K_M` jó egyensúlyt biztosít a méret és a minőség között), majd kattintson a Download gombra

Az LM Studio automatikusan letölti és a megfelelő könyvtárba helyezi a modellt.

Ha további modelleket szeretne letölteni, kereshet rájuk a Discover fülön, az LM Studio pedig elvégzi a többit.

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