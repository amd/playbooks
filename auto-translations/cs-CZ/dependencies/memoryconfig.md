<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pro Ryzen AI Halo je vyhrazená paměť GPU ve výchozím nastavení 64 GB, což je dostatečné pro většinu pracovních zátěží. Pro větší modely nebo delší kontexty může pomoci zvýšení na 96 GB. Chcete-li provést úpravu, otevřete **AMD Software: Adrenalin Edition™** a přejděte na **Performance → Tuning → AMD Variable Graphics Memory**. Pro uplatnění změn restartujte počítač.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Chcete-li změnit hodnotu vyhrazené paměti GPU, otevřete **AMD Software: Adrenalin Edition™** a přejděte na **Performance → Tuning → AMD Variable Graphics Memory**. Pro uplatnění změn restartujte počítač.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V systému Linux zvyšte pro spouštění větších modelů fond **sdílené paměti** dostupný pro GPU. To může zahrnovat nastavení vyhrazené paměti GPU v BIOSu na minimum, aby bylo možné maximalizovat fond sdílené paměti.

<!-- @device:halo_box -->

Pro AMD Ryzen™ AI Halo je výchozí hodnota 96 GB sdílené paměti. Chcete-li toto nastavení změnit, otevřete **AMD Ryzen™ AI Developer Center** a přejděte na kartu **Settings**. V části **Graphics Performance Settings** zvyšte posuvník **Shared Video Memory**, poté klikněte na **Apply Changes** a restartujte počítač, aby se změny projevily.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Zvyšte fond sdílené paměti změnou nastavení stránek správce překladových tabulek (TTM) jádra. AMD doporučuje nastavit v BIOSu minimální vyhrazenou paměť VRAM (0,5 GB), aby bylo maximum dostupné jako sdílená paměť.

1. Nainstalujte nástroj `pipx` a přidejte cestu pro kolečka nainstalovaná přes pipx do systémové vyhledávací cesty:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Nainstalujte kolečko `amd-debug-tools` z PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Zjistěte aktuální nastavení sdílené paměti:

   ```bash
   amd-ttm
   ```

4. Zvyšte přidělení sdílené paměti (jednotky v GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Pro uplatnění změn restartujte počítač.

<!-- @device:end -->

<!-- @os:end -->