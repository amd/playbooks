<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie GPT-OSS 120B v LM Studio

Ak chcete stiahnuť model GPT-OSS 120B:

1. Stlačte „Ctrl" + „Shift" + „M" na klávesnici alebo kliknite na kartu „Discover" (ikona lupy) v ľavom bočnom paneli
2. Vyhľadajte `ggml-org/gpt-oss-120b-GGUF`
3. Vyberte `mxfp4` a kliknite na Stiahnuť

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio automaticky stiahne model a umiestni ho do správneho adresára.

Ak si želáte stiahnuť ďalšie modely, môžete ich vyhľadať na karte Discover a LM Studio sa postará o zvyšok.

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