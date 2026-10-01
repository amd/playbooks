<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Для Ryzen AI Halo обсяг виділеної пам'яті GPU за замовчуванням становить 64 ГБ, чого достатньо для більшості робочих навантажень. Для більших моделей або довших контекстів збільшення цього значення може допомогти. Щоб налаштувати це, відкрийте **AMD Software: Adrenalin Edition™** і перейдіть до **Performance → Tuning → AMD Variable Graphics Memory**. Перезавантажте систему, щоб зміни набули чинності.

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

У Linux, щоб запускати більші моделі, збільшіть пул **спільної пам'яті**, доступний GPU. Для цього може знадобитися встановити в BIOS мінімальне значення виділеної пам'яті GPU, щоб можна було максимізувати пул спільної пам'яті.

<!-- @device:halo_box -->

Для AMD Ryzen™ AI Halo, щоб змінити налаштування за замовчуванням, відкрийте **AMD Ryzen™ AI Developer Center** і перейдіть на вкладку **Settings**. У розділі **Graphics Performance Settings** збільшіть повзунок **Shared Video Memory**, потім натисніть **Apply Changes** і перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Збільшіть пул спільної пам'яті, змінивши налаштування сторінок Translation Table Manager (TTM) ядра. AMD рекомендує встановити в BIOS мінімальний обсяг виділеної відеопам'яті (0.5 ГБ), щоб максимальний обсяг був доступний як спільна пам'ять.

1. Встановіть утиліту `pipx` і додайте шлях для встановлених через pipx пакетів (wheels) до системного шляху пошуку:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Встановіть пакет (wheel) `amd-debug-tools` з PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Перевірте поточні налаштування спільної пам'яті:

   ```bash
   amd-ttm
   ```

4. Збільшіть виділення спільної пам'яті (одиниці в ГБ):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Перезавантажте систему, щоб зміни набули чинності.

<!-- @device:end -->

<!-- @os:end -->