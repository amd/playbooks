<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка Qwen3-Coder 30B в LM Studio

Чтобы загрузить модель Qwen3-Coder 30B:

1. Нажмите "Ctrl" + "Shift" + "M" на клавиатуре или щёлкните по вкладке "Discover" (значок лупы) на боковой панели слева
2. Выполните поиск `Qwen3-Coder-30B-A3B`
3. Выберите квантование (рекомендуемый вариант `Q4_K_M` обеспечивает хороший баланс размера и качества) и нажмите Download

LM Studio автоматически загрузит модель и поместит её в нужный каталог.

Если вы хотите загрузить дополнительные модели, вы можете найти их на вкладке Discover, а LM Studio сделает всё остальное.

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