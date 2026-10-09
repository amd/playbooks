<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení Qwen3-Coder 30B v LM Studio

Pro stažení modelu Qwen3-Coder 30B:

1. Stiskněte na klávesnici "Ctrl" + "Shift" + "M" nebo klikněte na kartu "Discover" (ikona lupy) v levém postranním panelu
2. Vyhledejte `Qwen3-Coder-30B-A3B`
3. Vyberte kvantizaci (doporučená `Q4_K_M` nabízí dobrý poměr velikosti a kvality) a klikněte na Download

LM Studio automaticky stáhne model a umístí jej do správného adresáře.

Pokud budete chtít stáhnout další modely, můžete je vyhledat na kartě Discover a LM Studio se postará o zbytek.

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