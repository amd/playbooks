<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pre Ryzen AI Halo je predvolená hodnota vyhradenej pamäte GPU 64 GB, čo je dostatočné pre väčšinu pracovných záťaží. Pri väčších modeloch alebo dlhších kontextoch môže pomôcť jej zvýšenie. Ak ju chcete upraviť, otvorte **AMD Software: Adrenalin Edition™** a prejdite na **Performance → Tuning → AMD Variable Graphics Memory**. Aby sa zmeny prejavili, reštartujte počítač.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Ak chcete zmeniť hodnotu vyhradenej pamäte GPU, otvorte **AMD Software: Adrenalin Edition™** a prejdite na **Performance → Tuning → AMD Variable Graphics Memory**. Aby sa zmeny prejavili, reštartujte počítač.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V systéme Linux, ak chcete spúšťať väčšie modely, zvýšte fond **zdieľanej pamäte** dostupný pre GPU. To si môže vyžadovať nastavenie vyhradenej pamäte GPU v BIOSe na minimum, aby sa fond zdieľanej pamäte mohol maximalizovať.

<!-- @device:halo_box -->

Pre AMD Ryzen™ AI Halo, ak chcete upraviť predvolené nastavenie, otvorte **AMD Ryzen™ AI Developer Center** a prejdite na kartu **Settings**. V časti **Graphics Performance Settings** zvýšte posuvník **Shared Video Memory**, potom kliknite na **Apply Changes** a reštartujte počítač, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zvýšte fond zdieľanej pamäte zmenou nastavenia stránok Translation Table Manager (TTM) v jadre. AMD odporúča nastaviť minimálnu vyhradenú VRAM v BIOSe (0,5 GB), aby bolo ako zdieľaná pamäť k dispozícii maximálne množstvo.

1. Nainštalujte nástroj `pipx` a pridajte cestu k balíkom (wheels) nainštalovaným pomocou pipx do systémovej vyhľadávacej cesty:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Nainštalujte balík `amd-debug-tools` z PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Zistite aktuálne nastavenia zdieľanej pamäte:

   ```bash
   amd-ttm
   ```

4. Zvýšte alokáciu zdieľanej pamäte (jednotky v GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Aby sa zmeny prejavili, reštartujte počítač.

<!-- @device:end -->

<!-- @os:end -->