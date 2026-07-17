<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení modelu Qwen3.5 9B v LM Studio

Postup stažení modelu Qwen3.5 9B:

1. Stiskněte „Ctrl" + „Shift" + „M" na klávesnici nebo klikněte na záložku „Discover" (ikona lupy) v levém postranním panelu
2. Vyhledejte `Qwen3.5 9B`
3. Vyberte kvantizaci (doporučená `Q4_K_M` představuje dobrý kompromis mezi velikostí a kvalitou) a klikněte na Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio automaticky stáhne model a umístí jej do správného adresáře.

Pokud si přejete stáhnout další modely, můžete je vyhledat na záložce Discover a LM Studio se postará o zbytek.

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