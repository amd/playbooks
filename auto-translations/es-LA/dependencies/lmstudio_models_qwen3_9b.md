<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descargando Qwen3.5 9B en LM Studio

Para descargar el modelo Qwen3.5 9B:

1. Presiona "Ctrl" + "Shift" + "M" en tu teclado o haz clic en la pestaña "Discover" (ícono de lupa) en la barra lateral izquierda
2. Busca `Qwen3.5 9B`
3. Selecciona una cuantización (la recomendada `Q4_K_M` ofrece un buen equilibrio entre tamaño y calidad) y haz clic en Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio descargará automáticamente el modelo y lo colocará en el directorio correcto.

Si deseas descargar modelos adicionales, puedes buscarlos en la pestaña Discover y LM Studio se encargará del resto.

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