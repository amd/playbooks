<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Для Ryzen AI Halo объем выделенной видеопамяти GPU по умолчанию составляет 64 ГБ, чего достаточно для большинства рабочих нагрузок. Для более крупных моделей или более длинных контекстов может помочь увеличение этого значения. Чтобы изменить его, откройте **AMD Software: Adrenalin Edition™** и перейдите в раздел **Performance → Tuning → AMD Variable Graphics Memory**. Для применения изменений перезагрузите систему.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Чтобы изменить значение выделенной видеопамяти GPU, откройте **AMD Software: Adrenalin Edition™** и перейдите в раздел **Performance → Tuning → AMD Variable Graphics Memory**. Для применения изменений перезагрузите систему.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

В Linux для запуска более крупных моделей увеличьте пул **общей памяти (shared memory)**, доступной GPU. Для этого может потребоваться установить в BIOS минимальный объем выделенной видеопамяти GPU, чтобы максимально увеличить пул общей памяти.

<!-- @device:halo_box -->

Для AMD Ryzen™ AI Halo, чтобы изменить настройку по умолчанию, откройте **AMD Ryzen™ AI Developer Center** и перейдите на вкладку **Settings**. В разделе **Graphics Performance Settings** увеличьте значение ползунка **Shared Video Memory**, затем нажмите **Apply Changes** и перезагрузите систему для применения изменений.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Увеличьте пул общей памяти, изменив настройку страниц диспетчера таблиц трансляции ядра (Translation Table Manager, TTM). AMD рекомендует установить в BIOS минимальный объем выделенной видеопамяти (0,5 ГБ), чтобы максимальный объем был доступен в качестве общей памяти.

1. Установите утилиту `pipx` и добавьте путь для установленных через pipx пакетов в системный путь поиска:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Установите пакет `amd-debug-tools` из PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Запросите текущие настройки общей памяти:

   ```bash
   amd-ttm
   ```

4. Увеличьте объем выделяемой общей памяти (единицы измерения — ГБ):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Перезагрузите систему для применения изменений.

<!-- @device:end -->

<!-- @os:end -->