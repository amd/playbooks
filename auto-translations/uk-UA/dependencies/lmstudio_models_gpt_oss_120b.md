<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження GPT-OSS 120B у LM Studio

Щоб завантажити модель GPT-OSS 120B:

1. Натисніть "Ctrl" + "Shift" + "M" на клавіатурі або клацніть на вкладку "Discover" (іконка лупи) на лівій бічній панелі
2. Знайдіть `ggml-org/gpt-oss-120b-GGUF`
3. Виберіть `mxfp4` і натисніть Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio автоматично завантажить модель і розмістить її в потрібному каталозі.

Якщо ви хочете завантажити додаткові моделі, ви можете знайти їх на вкладці Discover, а LM Studio зробить усе інше.

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