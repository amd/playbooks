<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Sťahovanie Qwen3.5 9B v LM Studio

Ak chcete stiahnuť model Qwen3.5 9B:

1. Stlačte „Ctrl" + „Shift" + „M" na klávesnici alebo kliknite na kartu „Discover" (ikona lupy) v ľavom bočnom paneli
2. Vyhľadajte `Qwen3.5 9B`
3. Vyberte kvantizáciu (odporúčaná `Q4_K_M` predstavuje dobrý kompromis medzi veľkosťou a kvalitou) a kliknite na Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio automaticky stiahne model a umiestni ho do správneho adresára.

Ak si želáte stiahnuť ďalšie modely, môžete ich vyhľadať na karte Discover a LM Studio sa postará o zvyšok.

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