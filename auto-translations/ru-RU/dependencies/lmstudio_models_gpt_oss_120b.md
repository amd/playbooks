<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка GPT-OSS 120B в LM Studio

Чтобы загрузить модель GPT-OSS 120B:

1. Нажмите "Ctrl" + "Shift" + "M" на клавиатуре или щёлкните на вкладку "Discover" (значок лупы) на левой боковой панели
2. Найдите `ggml-org/gpt-oss-120b-GGUF`
3. Выберите `mxfp4` и нажмите Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio автоматически загрузит модель и поместит её в нужную директорию.

Если вы захотите загрузить дополнительные модели, вы можете найти их на вкладке Discover, и LM Studio сделает всё остальное.

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