<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o GPT-OSS 120B no LM Studio

Para transferir o modelo GPT-OSS 120B:

1. Prima "Ctrl" + "Shift" + "M" no teclado ou clique no separador "Discover" (ícone de lupa) na barra lateral esquerda
2. Pesquise por `ggml-org/gpt-oss-120b-GGUF`
3. Selecione `mxfp4` e clique em Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

O LM Studio irá transferir automaticamente e colocar o modelo na diretoria correta.

Caso deseje transferir modelos adicionais, pode pesquisá-los no separador Discover e o LM Studio tratará do resto.

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