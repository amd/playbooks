<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje GPT-OSS 120B modela u LM Studio

Da biste preuzeli GPT-OSS 120B model:

1. Pritisnite "Ctrl" + "Shift" + "M" na tastaturi ili kliknite na karticu "Discover" (ikonica lupe) u levom bočnom meniju
2. Pretražite `ggml-org/gpt-oss-120b-GGUF`
3. Izaberite `mxfp4` i kliknite na Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio će automatski preuzeti model i smestiti ga u odgovarajući direktorijum.

Ukoliko želite da preuzmete dodatne modele, možete ih pretražiti na kartici Discover, a LM Studio će se pobrinuti za ostalo.

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