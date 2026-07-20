<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження Qwen3.5 9B у LM Studio

Щоб завантажити модель Qwen3.5 9B:

1. Натисніть "Ctrl" + "Shift" + "M" на клавіатурі або клацніть на вкладку "Discover" (значок лупи) на лівій бічній панелі
2. Виконайте пошук `Qwen3.5 9B`
3. Виберіть квантування (рекомендоване `Q4_K_M` є хорошим балансом розміру та якості) і натисніть Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio автоматично завантажить модель і розмістить її у відповідному каталозі.

Якщо ви бажаєте завантажити додаткові моделі, ви можете знайти їх на вкладці Discover, а решту зробить LM Studio.

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