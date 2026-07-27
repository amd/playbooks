<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di Qwen3.5 9B su LM Studio

Per scaricare il modello Qwen3.5 9B:

1. Premi "Ctrl" + "Shift" + "M" sulla tastiera oppure fai clic sulla scheda "Discover" (icona a lente d'ingrandimento) nella barra laterale sinistra
2. Cerca `Qwen3.5 9B`
3. Seleziona una quantizzazione (la scelta consigliata `Q4_K_M` offre un buon equilibrio tra dimensione e qualità) e fai clic su Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio scaricherà automaticamente il modello e lo posizionerà nella directory corretta.

Se desideri scaricare altri modelli, puoi cercarli nella scheda Discover e LM Studio si occuperà del resto.

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