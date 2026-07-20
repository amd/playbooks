<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

W przypadku Ryzen AI Halo dedykowana pamięć GPU domyślnie wynosi 64 GB, co jest wystarczające dla większości obciążeń. W przypadku większych modeli lub dłuższych kontekstów zwiększenie tej wartości do 96 GB może pomóc. Aby ją dostosować, otwórz **AMD Software: Adrenalin Edition™** i przejdź do **Performance → Tuning → AMD Variable Graphics Memory**. Uruchom ponownie komputer, aby zmiany zaczęły obowiązywać.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aby zmienić wartość dedykowanej pamięci GPU, otwórz **AMD Software: Adrenalin Edition™** i przejdź do **Performance → Tuning → AMD Variable Graphics Memory**. Uruchom ponownie komputer, aby zmiany zaczęły obowiązywać.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

W systemie Linux, aby uruchamiać większe modele, zwiększ pulę **pamięci współdzielonej** dostępną dla GPU. Może to wymagać ustawienia w BIOS-ie dedykowanej pamięci GPU na wartość minimalną, tak aby pula pamięci współdzielonej mogła zostać zmaksymalizowana.

<!-- @device:halo_box -->

W przypadku AMD Ryzen™ AI Halo domyślna wartość to 96 GB pamięci współdzielonej. Aby ją zmodyfikować, otwórz **AMD Ryzen™ AI Developer Center** i przejdź do zakładki **Settings**. W sekcji **Graphics Performance Settings** zwiększ suwak **Shared Video Memory**, a następnie kliknij **Apply Changes** i uruchom ponownie komputer, aby zmiany zaczęły obowiązywać.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zwiększ pulę pamięci współdzielonej, zmieniając ustawienie stron menedżera tabel translacji (Translation Table Manager, TTM) w jądrze systemu. AMD zaleca ustawienie w BIOS-ie minimalnej dedykowanej pamięci VRAM (0,5 GB), aby maksymalna dostępna ilość pamięci mogła zostać wykorzystana jako pamięć współdzielona.

1. Zainstaluj narzędzie `pipx` i dodaj ścieżkę dla pakietów wheel zainstalowanych przez pipx do systemowej ścieżki wyszukiwania:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Zainstaluj pakiet wheel `amd-debug-tools` z PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Sprawdź bieżące ustawienia pamięci współdzielonej:

   ```bash
   amd-ttm
   ```

4. Zwiększ przydział pamięci współdzielonej (jednostki w GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Uruchom ponownie komputer, aby zmiany zaczęły obowiązywać.

<!-- @device:end -->

<!-- @os:end -->