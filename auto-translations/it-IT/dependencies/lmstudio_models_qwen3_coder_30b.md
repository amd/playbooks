<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Scaricamento di Qwen3-Coder 30B su LM Studio

Per scaricare il modello Qwen3-Coder 30B:

1. Premi "Ctrl" + "Shift" + "M" sulla tastiera oppure fai clic sulla scheda "Discover" (icona della lente d'ingrandimento) nella barra laterale sinistra
2. Cerca `Qwen3-Coder-30B-A3B`
3. Seleziona una quantizzazione (la raccomandata `Q4_K_M` offre un buon equilibrio tra dimensione e qualità) e fai clic su Download

LM Studio scaricherà automaticamente il modello e lo posizionerà nella directory corretta.

Se desideri scaricare altri modelli, puoi cercarli nella scheda Discover e LM Studio si occuperà del resto.

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