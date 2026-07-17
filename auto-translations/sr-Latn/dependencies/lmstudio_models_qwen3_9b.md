<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje Qwen3.5 9B u LM Studio

Da biste preuzeli model Qwen3.5 9B:

1. Pritisnite "Ctrl" + "Shift" + "M" na tastaturi ili kliknite na karticu "Discover" (ikona lupe) na levoj bočnoj traci
2. Potražite `Qwen3.5 9B`
3. Izaberite kvantizaciju (preporučena `Q4_K_M` predstavlja dobar balans između veličine i kvaliteta) i kliknite na Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio će automatski preuzeti model i smestiti ga u odgovarajući direktorijum.

Ako želite da preuzmete dodatne modele, možete ih potražiti u kartici Discover i LM Studio će se pobrinuti za ostalo.

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