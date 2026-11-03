<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Za Ryzen AI Halo je namenski pomnilnik GPE privzeto nastavljen na 64 GB, kar zadostuje za večino delovnih obremenitev. Pri večjih modelih ali daljših kontekstih lahko pomaga povečanje te vrednosti. Za prilagoditev odprite **AMD Software: Adrenalin Edition™** in pojdite na **Performance → Tuning → AMD Variable Graphics Memory**. Za uveljavitev sprememb ponovno zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Za spremembo vrednosti namenskega pomnilnika GPE odprite **AMD Software: Adrenalin Edition™** in pojdite na **Performance → Tuning → AMD Variable Graphics Memory**. Za uveljavitev sprememb ponovno zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

V sistemu Linux za zagon večjih modelov povečajte nabor **deljenega pomnilnika**, ki je na voljo GPE. To lahko vključuje nastavitev namenskega pomnilnika GPE v BIOS-u na minimalno vrednost, da se lahko nabor deljenega pomnilnika kar najbolj poveča.

<!-- @device:halo_box -->

Za AMD Ryzen™ AI Halo za spremembo privzete nastavitve odprite **AMD Ryzen™ AI Developer Center** in pojdite na zavihek **Settings**. Pod **Graphics Performance Settings** povečajte drsnik **Shared Video Memory**, nato kliknite **Apply Changes** in za uveljavitev sprememb ponovno zaženite sistem.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Povečajte nabor deljenega pomnilnika s spremembo nastavitve strani upravitelja Translation Table Manager (TTM) v jedru. AMD priporoča, da v BIOS-u nastavite najmanjšo vrednost namenskega pomnilnika VRAM (0,5 GB), da je na voljo največja količina kot deljeni pomnilnik.

1. Namestite pripomoček `pipx` in dodajte pot za kolute (wheels), nameščene s pipx, v sistemsko iskalno pot:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Namestite kolut `amd-debug-tools` iz PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Poizvedite trenutne nastavitve deljenega pomnilnika:

   ```bash
   amd-ttm
   ```

4. Povečajte dodelitev deljenega pomnilnika (enote v GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Za uveljavitev sprememb ponovno zaženite sistem.

<!-- @device:end -->

<!-- @os:end -->