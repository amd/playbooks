<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o GPT-OSS 120B no LM Studio

<!-- @device:halo_box -->
> **Nota:** Se este modelo já estiver disponível no LM Studio, pode ignorar esta secção. Caso contrário, siga os passos abaixo para o transferir.
<!-- @device:end -->

Para transferir o modelo GPT-OSS 120B:

1. Prima "Ctrl" + "Shift" + "M" no teclado ou clique no separador "Discover" (ícone da lupa) na barra lateral esquerda
2. Procure por `ggml-org/gpt-oss-120b-GGUF`
3. Selecione `mxfp4` e clique em Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

O LM Studio irá transferir automaticamente e colocar o modelo na diretoria correta.

Caso pretenda transferir modelos adicionais, pode procurá-los no separador Discover e o LM Studio tratará do resto.

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