<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Baixando o Qwen3-Coder 30B no LM Studio

Para baixar o modelo Qwen3-Coder 30B:

1. Pressione "Ctrl" + "Shift" + "M" no teclado ou clique na aba "Discover" (ícone de lupa) na barra lateral esquerda
2. Pesquise por `Qwen3-Coder-30B-A3B`
3. Selecione uma quantização (a recomendada `Q4_K_M` oferece um bom equilíbrio entre tamanho e qualidade) e clique em Download

O LM Studio baixará automaticamente o modelo e o colocará no diretório correto.

Caso deseje baixar modelos adicionais, você pode pesquisá-los na aba Discover, e o LM Studio cuidará do restante.

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