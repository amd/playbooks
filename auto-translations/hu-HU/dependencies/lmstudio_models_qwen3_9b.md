<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A Qwen3.5 9B letöltése LM Studio-ban

A Qwen3.5 9B modell letöltéséhez:

1. Nyomja meg a "Ctrl" + "Shift" + "M" billentyűkombinációt, vagy kattintson a bal oldalsávon található "Discover" fülre (Nagyító ikon)
2. Keressen rá a `Qwen3.5 9B` kifejezésre
3. Válasszon egy kvantálást (az ajánlott `Q4_K_M` jó egyensúlyt kínál a méret és a minőség között), majd kattintson a Download gombra

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

Az LM Studio automatikusan letölti a modellt, és a megfelelő könyvtárba helyezi.

Ha további modelleket szeretne letölteni, a Discover fülön kereshet rájuk, és az LM Studio elvégzi a többit.

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