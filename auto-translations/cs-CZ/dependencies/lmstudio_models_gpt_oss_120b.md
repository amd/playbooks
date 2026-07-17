<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stahování GPT-OSS 120B v LM Studio

Postup stažení modelu GPT-OSS 120B:

1. Stiskněte „Ctrl" + „Shift" + „M" na klávesnici nebo klikněte na záložku „Discover" (ikona lupy) v levém postranním panelu
2. Vyhledejte `ggml-org/gpt-oss-120b-GGUF`
3. Vyberte `mxfp4` a klikněte na Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio automaticky stáhne model a umístí ho do správného adresáře.

Pokud si přejete stáhnout další modely, můžete je vyhledat na záložce Discover a LM Studio se postará o zbytek.

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