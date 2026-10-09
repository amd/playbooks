<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o Qwen3-Coder 30B no LM Studio

Para transferir o modelo Qwen3-Coder 30B:

1. Prima "Ctrl" + "Shift" + "M" no teclado ou clique no separador "Discover" (ícone de lupa) na barra lateral esquerda
2. Procure por `Qwen3-Coder-30B-A3B`
3. Selecione uma quantização (a recomendada `Q4_K_M` oferece um bom equilíbrio entre tamanho e qualidade) e clique em Download

O LM Studio irá transferir automaticamente e colocar o modelo na diretoria correta.

Caso pretenda transferir modelos adicionais, pode procurá-los no separador Discover e o LM Studio trata do resto.

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