<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження GPT-OSS 120B у LM Studio

<!-- @device:halo_box -->
> **Примітка:** Якщо ця модель вже доступна в LM Studio, можна пропустити цей розділ. В іншому випадку виконайте наведені нижче кроки, щоб завантажити її.
<!-- @device:end -->

Щоб завантажити модель GPT-OSS 120B:

1. Натисніть "Ctrl" + "Shift" + "M" на клавіатурі або натисніть на вкладку "Discover" (піктограма лупи) на лівій бічній панелі
2. Виконайте пошук `ggml-org/gpt-oss-120b-GGUF`
3. Виберіть `mxfp4` і натисніть Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio автоматично завантажить модель і розмістить її у відповідному каталозі.

Якщо потрібно завантажити додаткові моделі, їх можна знайти на вкладці Discover, а LM Studio подбає про решту.

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