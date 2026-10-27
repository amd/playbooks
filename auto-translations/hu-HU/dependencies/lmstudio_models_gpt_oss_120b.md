<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B letöltése LM Studio-ban

<!-- @device:halo_box -->
> **Megjegyzés:** Ha ez a modell már elérhető az LM Studio-ban, akkor ezt a szakaszt kihagyhatja. Egyéb esetben kövesse az alábbi lépéseket a letöltéséhez.
<!-- @device:end -->

A GPT-OSS 120B modell letöltéséhez:

1. Nyomja meg a "Ctrl" + "Shift" + "M" billentyűkombinációt a billentyűzetén, vagy kattintson a "Discover" fülre (nagyítóüveg ikon) a bal oldali oldalsávon
2. Keressen rá a következőre: `ggml-org/gpt-oss-120b-GGUF`
3. Válassza ki a `mxfp4` opciót, majd kattintson a Download gombra

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

Az LM Studio automatikusan letölti és elhelyezi a modellt a megfelelő könyvtárban.

Ha további modelleket szeretne letölteni, rákereshet azokra a Discover fülön, és az LM Studio elvégzi a többit.

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