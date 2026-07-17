<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pre Ryzen AI Halo je vyhradená pamäť GPU predvolene nastavená na 64 GB, čo je dostatočné pre väčšinu pracovných záťaží. Pre väčšie modely alebo dlhšie kontexty môže pomôcť zvýšenie na 96 GB. Ak chcete upraviť toto nastavenie, otvorte **AMD Software: Adrenalin Edition™** a prejdite na **Performance → Tuning → AMD Variable Graphics Memory**. Reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Ak chcete zmeniť hodnotu vyhradenej pamäte GPU, otvorte **AMD Software: Adrenalin Edition™** a prejdite na **Performance → Tuning → AMD Variable Graphics Memory**. Reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V systéme Linux, ak chcete spúšťať väčšie modely, zvýšte fond **zdieľanej pamäte** dostupnej pre GPU. Môže to zahŕňať nastavenie vyhradenej pamäte GPU v systéme BIOS na minimum, aby bolo možné maximalizovať fond zdieľanej pamäte.

<!-- @device:halo_box -->

Pre AMD Ryzen™ AI Halo je predvolená hodnota 96 GB zdieľanej pamäte. Ak chcete toto nastavenie zmeniť, otvorte **AMD Ryzen™ AI Developer Center** a prejdite na kartu **Settings**. V časti **Graphics Performance Settings** zvýšte posúvač **Shared Video Memory**, potom kliknite na **Apply Changes** a reštartujte systém, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zvýšte fond zdieľanej pamäte zmenou nastavenia stránky Translation Table Manager (TTM) jadra. AMD odporúča nastaviť minimálnu vyhradenú pamäť VRAM v systéme BIOS (0,5 GB), aby bolo maximálne množstvo dostupné ako zdieľaná pamäť.

1. Nainštalujte nástroj `pipx` a pridajte cestu pre kolieska nainštalované cez pipx do systémovej vyhľadávacej cesty:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Nainštalujte koliesko `amd-debug-tools` z PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Zobrazte aktuálne nastavenia zdieľanej pamäte:

   ```bash
   amd-ttm
   ```

4. Zvýšte pridelenie zdieľanej pamäte (jednotky v GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reštartujte systém, aby sa zmeny prejavili.

<!-- @device:end -->

<!-- @os:end -->