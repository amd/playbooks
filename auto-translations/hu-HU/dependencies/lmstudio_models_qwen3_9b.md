<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A Qwen3.5 9B letöltése az LM Studio-ban

A Qwen3.5 9B modell letöltéséhez:

1. Nyomja meg a "Ctrl" + "Shift" + "M" billentyűkombinációt, vagy kattintson a bal oldali oldalsávon a "Discover" fülre (nagyítóikon)
2. Keressen rá erre: `Qwen3.5 9B`
3. Válasszon egy kvantálást (az ajánlott `Q4_K_M` jó egyensúlyt biztosít méret és minőség között), majd kattintson a Download gombra

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

Az LM Studio automatikusan letölti, és a megfelelő könyvtárba helyezi a modellt.

Ha további modelleket szeretne letölteni, kereshet rájuk a Discover fülön, és az LM Studio elvégzi a többi lépést.

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