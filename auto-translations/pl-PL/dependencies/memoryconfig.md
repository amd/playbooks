<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

W przypadku Ryzen AI Halo dedykowana pamięć GPU domyślnie wynosi 64 GB, co jest wystarczające dla większości obciążeń. W przypadku większych modeli lub dłuższych kontekstów zwiększenie tej wartości do 96 GB może być pomocne. Aby to zmienić, otwórz **AMD Software: Adrenalin Edition™** i przejdź do **Performance → Tuning → AMD Variable Graphics Memory**. Uruchom ponownie komputer, aby zmiany zostały zastosowane.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aby zmienić wartość dedykowanej pamięci GPU, otwórz **AMD Software: Adrenalin Edition™** i przejdź do **Performance → Tuning → AMD Variable Graphics Memory**. Uruchom ponownie komputer, aby zmiany zostały zastosowane.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

W systemie Linux, aby uruchamiać większe modele, zwiększ pulę **pamięci współdzielonej** dostępnej dla GPU. Może to wymagać ustawienia w BIOS-ie dedykowanej pamięci GPU na wartość minimalną, tak aby pula pamięci współdzielonej mogła zostać zmaksymalizowana.

<!-- @device:halo_box -->

W przypadku AMD Ryzen™ AI Halo domyślna wartość wynosi 96 GB pamięci współdzielonej. Aby ją zmienić, otwórz **AMD Ryzen™ AI Developer Center** i przejdź do zakładki **Settings**. W sekcji **Graphics Performance Settings** zwiększ suwak **Shared Video Memory**, a następnie kliknij **Apply Changes** i uruchom ponownie komputer, aby zmiany zostały zastosowane.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zwiększ pulę pamięci współdzielonej, zmieniając ustawienie stron Translation Table Manager (TTM) jądra systemu. AMD zaleca ustawienie minimalnej dedykowanej pamięci VRAM w BIOS-ie (0,5 GB), tak aby maksymalna ilość była dostępna jako pamięć współdzielona.

1. Zainstaluj narzędzie `pipx` i dodaj ścieżkę dla kół instalowanych przez pipx do systemowej ścieżki wyszukiwania:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Zainstaluj koło `amd-debug-tools` z PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Sprawdź bieżące ustawienia pamięci współdzielonej:

   ```bash
   amd-ttm
   ```

4. Zwiększ alokację pamięci współdzielonej (jednostki w GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Uruchom ponownie komputer, aby zmiany zostały zastosowane.

<!-- @device:end -->

<!-- @os:end -->