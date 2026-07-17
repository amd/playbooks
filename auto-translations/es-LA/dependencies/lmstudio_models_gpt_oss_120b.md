<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descarga de GPT-OSS 120B en LM Studio

Para descargar el modelo GPT-OSS 120B:

1. Presiona "Ctrl" + "Shift" + "M" en tu teclado o haz clic en la pestaña "Discover" (ícono de lupa) en la barra lateral izquierda
2. Busca `ggml-org/gpt-oss-120b-GGUF`
3. Selecciona `mxfp4` y haz clic en Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio descargará automáticamente el modelo y lo colocará en el directorio correcto.

Si deseas descargar modelos adicionales, puedes buscarlos en la pestaña Discover y LM Studio se encargará del resto.

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