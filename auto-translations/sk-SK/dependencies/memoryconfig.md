<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pre Ryzen AI Halo je vyhradená pamäť GPU predvolene nastavená na 64 GB, čo postačuje pre väčšinu pracovných úloh. Pri väčších modeloch alebo dlhších kontextoch môže pomôcť zvýšenie tejto hodnoty na 96 GB. Ak chcete túto hodnotu upraviť, otvorte **AMD Software: Adrenalin Edition™** a prejdite na **Performance → Tuning → AMD Variable Graphics Memory**. Reštartujte počítač, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Ak chcete zmeniť hodnotu vyhradenej pamäte GPU, otvorte **AMD Software: Adrenalin Edition™** a prejdite na **Performance → Tuning → AMD Variable Graphics Memory**. Reštartujte počítač, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V systéme Linux, ak chcete spúšťať väčšie modely, zväčšite **zdieľanú pamäť** dostupnú pre GPU. To si môže vyžadovať nastavenie vyhradenej pamäte GPU v BIOS-e na minimum, aby bolo možné maximalizovať fond zdieľanej pamäte.

<!-- @device:halo_box -->

Pre AMD Ryzen™ AI Halo je predvolená hodnota 96 GB zdieľanej pamäte. Ak ju chcete upraviť, otvorte **AMD Ryzen™ AI Developer Center** a prejdite na kartu **Settings**. V časti **Graphics Performance Settings** zvýšte posuvník **Shared Video Memory**, potom kliknite na **Apply Changes** a reštartujte počítač, aby sa zmeny prejavili.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zväčšite fond zdieľanej pamäte zmenou nastavenia stránok Translation Table Manager (TTM) v jadre. Spoločnosť AMD odporúča nastaviť v BIOS-e minimálnu vyhradenú pamäť VRAM (0,5 GB), aby bolo k dispozícii maximálne množstvo ako zdieľaná pamäť.

1. Nainštalujte nástroj `pipx` a pridajte cestu k balíčkom nainštalovaným pomocou pipx do systémovej cesty vyhľadávania:

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

5. Reštartujte počítač, aby sa zmeny prejavili.

<!-- @device:end -->

<!-- @os:end -->