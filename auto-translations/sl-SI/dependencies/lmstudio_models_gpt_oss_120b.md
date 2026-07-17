<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos GPT-OSS 120B v LM Studio

Za prenos modela GPT-OSS 120B:

1. Pritisnite "Ctrl" + "Shift" + "M" na tipkovnici ali kliknite zavihek "Discover" (ikona povečevalnega stekla) v levi stranski vrstici
2. Poiščite `ggml-org/gpt-oss-120b-GGUF`
3. Izberite `mxfp4` in kliknite Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio bo samodejno prenesel model in ga namestil v pravilni imenik.

Če želite prenesti dodatne modele, jih lahko poiščete v zavihku Discover in LM Studio bo poskrbel za ostalo.

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