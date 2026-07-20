<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Для Ryzen AI Halo выделенная память GPU по умолчанию составляет 64 ГБ, чего достаточно для большинства рабочих нагрузок. Для более крупных моделей или более длинных контекстов может помочь увеличение этого значения до 96 ГБ. Чтобы изменить это значение, откройте **AMD Software: Adrenalin Edition™** и перейдите в **Performance → Tuning → AMD Variable Graphics Memory**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Чтобы изменить значение выделенной памяти GPU, откройте **AMD Software: Adrenalin Edition™** и перейдите в **Performance → Tuning → AMD Variable Graphics Memory**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

В Linux для запуска более крупных моделей увеличьте пул **общей памяти**, доступной GPU. Это может потребовать установки минимального значения выделенной памяти GPU в BIOS, чтобы можно было максимально увеличить пул общей памяти.

<!-- @device:halo_box -->

Для AMD Ryzen™ AI Halo значение по умолчанию составляет 96 ГБ общей памяти. Чтобы изменить это значение, откройте **AMD Ryzen™ AI Developer Center** и перейдите на вкладку **Settings**. В разделе **Graphics Performance Settings** увеличьте ползунок **Shared Video Memory**, затем нажмите **Apply Changes** и перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Увеличьте пул общей памяти, изменив настройку страниц диспетчера таблиц трансляции (TTM) ядра. AMD рекомендует установить в BIOS минимальный объём выделенной видеопамяти (0,5 ГБ), чтобы максимальный объём был доступен в качестве общей памяти.

1. Установите утилиту `pipx` и добавьте путь к установленным через pipx пакетам в системный путь поиска:

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

4. Увеличьте объём выделяемой общей памяти (в ГБ):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Перезагрузите систему, чтобы изменения вступили в силу.

<!-- @device:end -->

<!-- @os:end -->