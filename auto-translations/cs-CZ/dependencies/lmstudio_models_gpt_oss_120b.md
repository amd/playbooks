<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stahování GPT-OSS 120B v LM Studio

<!-- @device:halo_box -->
> **Poznámka:** Pokud je tento model v LM Studio již k dispozici, můžete tuto část přeskočit. V opačném případě postupujte podle níže uvedených kroků a model stáhněte.
<!-- @device:end -->

Stažení modelu GPT-OSS 120B:

1. Stiskněte na klávesnici "Ctrl" + "Shift" + "M" nebo klikněte na kartu "Discover" (ikona lupy) na levém postranním panelu
2. Vyhledejte `ggml-org/gpt-oss-120b-GGUF`
3. Vyberte `mxfp4` a klikněte na Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio model automaticky stáhne a umístí do správného adresáře.

Pokud si přejete stáhnout další modely, můžete je vyhledat na kartě Discover a LM Studio se postará o zbytek.

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