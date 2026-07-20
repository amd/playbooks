<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Scaricare GPT-OSS 120B su LM Studio

Per scaricare il modello GPT-OSS 120B:

1. Premi "Ctrl" + "Shift" + "M" sulla tastiera oppure clicca sulla scheda "Discover" (icona della lente d'ingrandimento) nella barra laterale sinistra
2. Cerca `ggml-org/gpt-oss-120b-GGUF`
3. Seleziona `mxfp4` e clicca su Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio scaricherà automaticamente il modello e lo posizionerà nella directory corretta.

Se desideri scaricare modelli aggiuntivi, puoi cercarli nella scheda Discover e LM Studio si occuperà del resto.

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