<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea Qwen3-Coder 30B în LM Studio

Pentru a descărca modelul Qwen3-Coder 30B:

1. Apăsați „Ctrl” + „Shift” + „M” pe tastatură sau faceți clic pe fila „Discover” (pictograma lupă) din bara laterală din stânga
2. Căutați `Qwen3-Coder-30B-A3B`
3. Selectați o cuantizare (cea recomandată, `Q4_K_M`, oferă un echilibru bun între dimensiune și calitate) și faceți clic pe Download

LM Studio va descărca automat modelul și îl va plasa în directorul corect.

Dacă doriți să descărcați modele suplimentare, le puteți căuta în fila Discover, iar LM Studio se va ocupa de restul.

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