<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Za Ryzen AI Halo je privzeta namenjena pomnilnik GPU 64 GB, kar zadostuje za večino delovnih obremenitev. Pri večjih modelih ali daljših kontekstih je morda koristno povečanje na 96 GB. Za prilagoditev odprite **AMD Software: Adrenalin Edition™** in se pomaknite na **Performance → Tuning → AMD Variable Graphics Memory**. Za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Če želite spremeniti vrednost namenjenega pomnilnika GPU, odprite **AMD Software: Adrenalin Edition™** in se pomaknite na **Performance → Tuning → AMD Variable Graphics Memory**. Za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V sistemu Linux za zaganjanje večjih modelov povečajte skupni pomnilniški bazen (**shared memory**), ki je na voljo GPU. To lahko vključuje nastavitev namenjenega pomnilnika GPU v BIOS-u na najmanjšo vrednost, da je mogoče skupni pomnilniški bazen čim bolj povečati.

<!-- @device:halo_box -->

Za AMD Ryzen™ AI Halo je privzeta vrednost 96 GB skupnega pomnilnika. Če jo želite spremeniti, odprite **AMD Ryzen™ AI Developer Center** in pojdite na zavihek **Settings**. Pod razdelkom **Graphics Performance Settings** povečajte drsnik **Shared Video Memory**, nato kliknite **Apply Changes** in znova zaženite sistem, da spremembe začnejo veljati.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Povečajte skupni pomnilniški bazen s spremembo nastavitve strani Translation Table Manager (TTM) jedra. AMD priporoča, da v BIOS-u nastavite najmanjši namenski VRAM (0,5 GB), da bo največja možna količina na voljo kot skupni pomnilnik.

1. Namestite pripomoček `pipx` in dodajte pot za kolesa, nameščena s pipx, v sistemsko iskalno pot:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Namestite kolo `amd-debug-tools` iz PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Poizvedite o trenutnih nastavitvah skupnega pomnilnika:

   ```bash
   amd-ttm
   ```

4. Povečajte dodelitev skupnega pomnilnika (enote v GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Za uveljavitev sprememb znova zaženite sistem.

<!-- @device:end -->

<!-- @os:end -->