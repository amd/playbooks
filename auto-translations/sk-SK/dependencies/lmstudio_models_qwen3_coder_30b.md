<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie modelu Qwen3-Coder 30B v LM Studio

Ak chcete stiahnuť model Qwen3-Coder 30B:

1. Stlačte "Ctrl" + "Shift" + "M" na klávesnici alebo kliknite na kartu "Discover" (ikona lupy) na ľavom bočnom paneli
2. Vyhľadajte `Qwen3-Coder-30B-A3B`
3. Vyberte kvantizáciu (odporúčaná `Q4_K_M` predstavuje dobrý pomer medzi veľkosťou a kvalitou) a kliknite na Download

LM Studio automaticky stiahne model a umiestni ho do správneho adresára.

Ak si želáte stiahnuť ďalšie modely, môžete ich vyhľadať na karte Discover a LM Studio sa postará o zvyšok.

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