<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження Qwen3-Coder 30B у LM Studio

Щоб завантажити модель Qwen3-Coder 30B:

1. Натисніть "Ctrl" + "Shift" + "M" на клавіатурі або клацніть на вкладку "Discover" (іконка лупи) на лівій бічній панелі
2. Знайдіть `Qwen3-Coder-30B-A3B`
3. Виберіть квантизацію (рекомендована `Q4_K_M` забезпечує гарний баланс розміру та якості) і натисніть Download

LM Studio автоматично завантажить і розмістить модель у правильному каталозі.

Якщо ви хочете завантажити додаткові моделі, ви можете знайти їх у вкладці Discover, а LM Studio подбає про решту.

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