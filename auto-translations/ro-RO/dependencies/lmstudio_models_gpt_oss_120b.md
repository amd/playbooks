<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea GPT-OSS 120B pe LM Studio

Pentru a descărca modelul GPT-OSS 120B:

1. Apăsați „Ctrl" + „Shift" + „M" pe tastatură sau faceți clic pe fila „Discover" (pictograma cu lupă) din bara laterală din stânga
2. Căutați `ggml-org/gpt-oss-120b-GGUF`
3. Selectați `mxfp4` și faceți clic pe Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio va descărca automat și va plasa modelul în directorul corect.

Dacă doriți să descărcați modele suplimentare, le puteți căuta în fila Discover, iar LM Studio se va ocupa de restul.

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