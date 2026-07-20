<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pro Ryzen AI Halo je vyhrazená paměť GPU standardně nastavena na 64 GB, což postačuje pro většinu úloh. U větších modelů nebo delších kontextů může pomoci zvýšení této hodnoty na 96 GB. Chcete-li ji upravit, otevřete **AMD Software: Adrenalin Edition™** a přejděte na **Performance → Tuning → AMD Variable Graphics Memory**. Aby se změny projevily, restartujte počítač.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Chcete-li změnit hodnotu vyhrazené paměti GPU, otevřete **AMD Software: Adrenalin Edition™** a přejděte na **Performance → Tuning → AMD Variable Graphics Memory**. Aby se změny projevily, restartujte počítač.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V systému Linux, chcete-li spouštět větší modely, zvyšte **fond sdílené paměti** dostupný pro GPU. To může vyžadovat nastavení vyhrazené paměti GPU v BIOSu na minimum, aby bylo možné maximalizovat fond sdílené paměti.

<!-- @device:halo_box -->

Pro AMD Ryzen™ AI Halo je výchozí hodnota 96 GB sdílené paměti. Chcete-li ji upravit, otevřete **AMD Ryzen™ AI Developer Center** a přejděte na kartu **Settings**. V části **Graphics Performance Settings** zvyšte posuvník **Shared Video Memory**, poté klikněte na **Apply Changes** a restartujte počítač, aby se změny projevily.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zvyšte fond sdílené paměti změnou nastavení stránek Translation Table Manager (TTM) v jádru. Společnost AMD doporučuje nastavit v BIOSu minimální vyhrazenou paměť VRAM (0,5 GB), aby bylo jako sdílená paměť k dispozici co nejvíce prostoru.

1. Nainstalujte nástroj `pipx` a přidejte cestu k balíčkům nainstalovaným pomocí pipx do systémové vyhledávací cesty:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Nainstalujte balíček `amd-debug-tools` z PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Zjistěte aktuální nastavení sdílené paměti:

   ```bash
   amd-ttm
   ```

4. Zvyšte přidělenou sdílenou paměť (jednotky v GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Aby se změny projevily, restartujte počítač.

<!-- @device:end -->

<!-- @os:end -->