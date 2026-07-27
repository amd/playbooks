<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Для Ryzen AI Halo обсяг виділеної пам'яті GPU за замовчуванням становить 64 ГБ, чого достатньо для більшості робочих навантажень. Для більших моделей або довших контекстів може допомогти збільшення цього значення до 96 ГБ. Щоб змінити налаштування, відкрийте **AMD Software: Adrenalin Edition™** і перейдіть до **Performance → Tuning → AMD Variable Graphics Memory**. Перезавантажте систему, щоб зміни набули чинності.

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

У Linux для запуску більших моделей збільшіть пул **спільної пам'яті**, доступний для GPU. Це може вимагати встановлення мінімального значення виділеної пам'яті GPU в BIOS, щоб максимізувати пул спільної пам'яті.

<!-- @device:halo_box -->

Для AMD Ryzen™ AI Halo за замовчуванням встановлено 96 ГБ спільної пам'яті. Щоб змінити це значення, відкрийте **AMD Ryzen™ AI Developer Center** і перейдіть на вкладку **Settings**. У розділі **Graphics Performance Settings** збільшіть повзунок **Shared Video Memory**, потім натисніть **Apply Changes** і перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Збільшіть пул спільної пам'яті, змінивши налаштування сторінок Translation Table Manager (TTM) ядра. AMD рекомендує встановити мінімальний обсяг виділеної відеопам'яті в BIOS (0,5 ГБ), щоб максимальний обсяг був доступний як спільна пам'ять.

1. Встановіть утиліту `pipx` та додайте шлях для встановлених через pipx пакетів wheel до системного шляху пошуку:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Встановіть пакет `amd-debug-tools` з PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Перевірте поточні налаштування спільної пам'яті:

   ```bash
   amd-ttm
   ```

4. Збільшіть обсяг виділеної спільної пам'яті (одиниці в ГБ):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Перезавантажте систему, щоб зміни набули чинності.

<!-- @device:end -->

<!-- @os:end -->