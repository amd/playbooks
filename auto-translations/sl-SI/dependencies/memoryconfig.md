<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pri Ryzen AI Halo je namenski pomnilnik GPE privzeto nastavljen na 64 GB, kar zadošča za večino delovnih obremenitev. Pri večjih modelih ali daljših kontekstih lahko pomaga povečanje te vrednosti. Za prilagoditev odprite **AMD Software: Adrenalin Edition™** in pojdite na **Performance → Tuning → AMD Variable Graphics Memory**. Za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Za spremembo vrednosti namenskega pomnilnika GPE odprite **AMD Software: Adrenalin Edition™** in pojdite na **Performance → Tuning → AMD Variable Graphics Memory**. Za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V sistemu Linux za zagon večjih modelov povečajte nabor **skupnega pomnilnika**, ki je na voljo GPE. To lahko vključuje nastavitev namenskega pomnilnika GPE v BIOS-u na najmanjšo vrednost, da se lahko nabor skupnega pomnilnika poveča na največjo možno vrednost.

<!-- @device:halo_box -->

Za AMD Ryzen™ AI Halo za spremembo privzete nastavitve odprite **AMD Ryzen™ AI Developer Center** in pojdite na zavihek **Settings**. Pod **Graphics Performance Settings** povečajte drsnik **Shared Video Memory**, nato kliknite **Apply Changes** in za uveljavitev sprememb znova zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Povečajte nabor skupnega pomnilnika s spremembo nastavitve strani upravitelja prevajalnih tabel (Translation Table Manager, TTM) v jedru. AMD priporoča, da v BIOS-u nastavite najmanjši namenski pomnilnik VRAM (0,5 GB), tako da je na voljo največja možna količina kot skupni pomnilnik.

1. Namestite pripomoček `pipx` in dodajte pot za pakete, nameščene s pipx, v sistemsko iskalno pot:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Namestite paket `amd-debug-tools` iz PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Poizvedite po trenutnih nastavitvah skupnega pomnilnika:

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