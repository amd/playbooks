<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Baixando o GPT-OSS 120B no LM Studio

Para baixar o modelo GPT-OSS 120B:

1. Pressione "Ctrl" + "Shift" + "M" no teclado ou clique na aba "Discover" (ícone de Lupa) na barra lateral esquerda
2. Pesquise por `ggml-org/gpt-oss-120b-GGUF`
3. Selecione `mxfp4` e clique em Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

O LM Studio irá baixar e colocar automaticamente o modelo no diretório correto.

Caso deseje baixar modelos adicionais, você pode pesquisá-los na aba Discover e o LM Studio cuidará do restante.

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