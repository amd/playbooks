<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка Qwen3.5 9B в LM Studio

Чтобы загрузить модель Qwen3.5 9B:

1. Нажмите «Ctrl» + «Shift» + «M» на клавиатуре или щёлкните на вкладке «Discover» (значок лупы) на левой боковой панели
2. Найдите `Qwen3.5 9B`
3. Выберите квантизацию (рекомендуемый вариант `Q4_K_M` обеспечивает хороший баланс между размером и качеством) и нажмите Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio автоматически загрузит модель и поместит её в нужную директорию.

Если вы хотите загрузить дополнительные модели, вы можете найти их на вкладке Discover, и LM Studio сделает всё остальное.

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