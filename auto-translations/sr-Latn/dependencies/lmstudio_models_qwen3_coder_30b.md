<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje Qwen3-Coder 30B modela na LM Studio

Da biste preuzeli Qwen3-Coder 30B model:

1. Pritisnite "Ctrl" + "Shift" + "M" na tastaturi ili kliknite na karticu "Discover" (ikonica lupe) na levoj bočnoj traci
2. Pretražite `Qwen3-Coder-30B-A3B`
3. Izaberite kvantizaciju (preporučena `Q4_K_M` predstavlja dobar balans veličine i kvaliteta) i kliknite na Download

LM Studio će automatski preuzeti model i smestiti ga u odgovarajući direktorijum.

Ukoliko želite da preuzmete dodatne modele, možete ih pretražiti na kartici Discover, a LM Studio će se pobrinuti za ostalo.

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