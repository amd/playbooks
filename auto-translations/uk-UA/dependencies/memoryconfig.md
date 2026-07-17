<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Для Ryzen AI Halo виділена пам'ять GPU за замовчуванням становить 64 ГБ, чого достатньо для більшості робочих навантажень. Для більших моделей або довших контекстів може допомогти збільшення до 96 ГБ. Щоб налаштувати це, відкрийте **AMD Software: Adrenalin Edition™** і перейдіть до **Performance → Tuning → AMD Variable Graphics Memory**. Перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Щоб змінити значення виділеної пам'яті GPU, відкрийте **AMD Software: Adrenalin Edition™** і перейдіть до **Performance → Tuning → AMD Variable Graphics Memory**. Перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

У Linux для запуску більших моделей збільште пул **спільної пам'яті**, доступний для GPU. Це може передбачати встановлення мінімального значення виділеної пам'яті GPU у BIOS, щоб максимально збільшити пул спільної пам'яті.

<!-- @device:halo_box -->

Для AMD Ryzen™ AI Halo за замовчуванням доступно 96 ГБ спільної пам'яті. Щоб змінити це, відкрийте **AMD Ryzen™ AI Developer Center** і перейдіть на вкладку **Settings**. У розділі **Graphics Performance Settings** збільште повзунок **Shared Video Memory**, потім натисніть **Apply Changes** і перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Збільште пул спільної пам'яті, змінивши налаштування сторінок менеджера таблиць трансляції (TTM) ядра. AMD рекомендує встановити мінімальний обсяг виділеної VRAM у BIOS (0,5 ГБ), щоб максимальна кількість була доступна як спільна пам'ять.

1. Встановіть утиліту `pipx` і додайте шлях для пакетів, встановлених через pipx, до системного шляху пошуку:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Встановіть пакет `amd-debug-tools` з PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Перегляньте поточні налаштування спільної пам'яті:

   ```bash
   amd-ttm
   ```

4. Збільште обсяг виділеної спільної пам'яті (одиниці в ГБ):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Перезавантажте систему, щоб зміни набули чинності.

<!-- @device:end -->

<!-- @os:end -->