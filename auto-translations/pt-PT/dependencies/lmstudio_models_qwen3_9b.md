<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o Qwen3.5 9B no LM Studio

Para transferir o modelo Qwen3.5 9B:

1. Prima "Ctrl" + "Shift" + "M" no teclado ou clique no separador "Discover" (ícone de lupa) na barra lateral esquerda
2. Pesquise por `Qwen3.5 9B`
3. Selecione uma quantização (a recomendada `Q4_K_M` é um bom equilíbrio entre tamanho e qualidade) e clique em Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

O LM Studio irá transferir automaticamente o modelo e colocá-lo na diretoria correta.

Caso deseje transferir modelos adicionais, pode pesquisá-los no separador Discover e o LM Studio tratará do resto.

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