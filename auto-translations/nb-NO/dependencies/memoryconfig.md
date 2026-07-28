<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

For Ryzen AI Halo er dedikert GPU-minne som standard satt til 64 GB, noe som er tilstrekkelig for de fleste arbeidsbelastninger. For større modeller eller lengre kontekster kan det hjelpe å øke dette til 96 GB. For å justere dette, åpne **AMD Software: Adrenalin Edition™** og naviger til **Performance → Tuning → AMD Variable Graphics Memory**. Start på nytt for at endringene skal tre i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

For å endre verdien for dedikert GPU-minne, åpne **AMD Software: Adrenalin Edition™** og naviger til **Performance → Tuning → AMD Variable Graphics Memory**. Start på nytt for at endringene skal tre i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

På Linux, for å kjøre større modeller, øk **delt minne**-poolen som er tilgjengelig for GPU-en. Dette kan innebære å sette dedikert GPU-minne i BIOS til minimum, slik at den delte minnepoolen kan maksimeres.

<!-- @device:halo_box -->

For AMD Ryzen™ AI Halo er standarden 96 GB delt. For å endre dette, åpne **AMD Ryzen™ AI Developer Center** og gå til fanen **Settings**. Under **Graphics Performance Settings**, øk glidebryteren **Shared Video Memory**, klikk deretter **Apply Changes** og start på nytt for at endringene skal tre i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Øk den delte minnepoolen ved å endre kjernens Translation Table Manager (TTM)-sideinnstilling. AMD anbefaler å sette minimum dedikert VRAM i BIOS (0,5 GB) slik at maksimal mengde er tilgjengelig som delt minne.

1. Installer verktøyet `pipx` og legg til stien for pipx-installerte wheels i systemets søkesti:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installer `amd-debug-tools`-wheelen fra PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Spør etter gjeldende innstillinger for delt minne:

   ```bash
   amd-ttm
   ```

4. Øk den delte minneallokeringen (enheter i GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Start på nytt for at endringene skal tre i kraft.

<!-- @device:end -->

<!-- @os:end -->