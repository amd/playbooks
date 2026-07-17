<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea Qwen3.5 9B în LM Studio

Pentru a descărca modelul Qwen3.5 9B:

1. Apăsați „Ctrl" + „Shift" + „M" pe tastatură sau faceți clic pe fila „Discover" (pictograma lupă) din bara laterală stângă
2. Căutați `Qwen3.5 9B`
3. Selectați o cuantizare (cea recomandată `Q4_K_M` reprezintă un echilibru bun între dimensiune și calitate) și faceți clic pe Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio va descărca automat modelul și îl va plasa în directorul corect.

Dacă doriți să descărcați modele suplimentare, le puteți căuta în fila Discover, iar LM Studio se va ocupa de restul.

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