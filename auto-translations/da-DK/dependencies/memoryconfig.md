<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

For Ryzen AI Halo er den dedikerede GPU-hukommelse som standard 64 GB, hvilket er tilstrækkeligt til de fleste arbejdsbelastninger. For større modeller eller længere kontekster kan det være en fordel at øge denne værdi. For at justere den skal du åbne **AMD Software: Adrenalin Edition™** og navigere til **Performance → Tuning → AMD Variable Graphics Memory**. Genstart for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

For at ændre værdien for den dedikerede GPU-hukommelse skal du åbne **AMD Software: Adrenalin Edition™** og navigere til **Performance → Tuning → AMD Variable Graphics Memory**. Genstart for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

På Linux skal du, for at køre større modeller, øge puljen af **delt hukommelse (shared memory)**, der er tilgængelig for GPU'en. Dette kan indebære, at den dedikerede GPU-hukommelse i BIOS sættes til minimum, så puljen af delt hukommelse kan maksimeres.

<!-- @device:halo_box -->

For AMD Ryzen™ AI Halo skal du, for at ændre standardindstillingen, åbne **AMD Ryzen™ AI Developer Center** og gå til fanen **Settings**. Under **Graphics Performance Settings** skal du øge skyderen **Shared Video Memory**, derefter klikke på **Apply Changes** og genstarte for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Øg puljen af delt hukommelse ved at ændre kernens indstilling for Translation Table Manager (TTM)-sider. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS (0,5 GB), så det maksimale beløb er tilgængeligt som delt hukommelse.

1. Installer værktøjet `pipx`, og tilføj stien for pipx-installerede wheels til systemets søgesti:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installer `amd-debug-tools`-wheelen fra PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Forespørg de aktuelle indstillinger for delt hukommelse:

   ```bash
   amd-ttm
   ```

4. Øg allokeringen af delt hukommelse (enheder i GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Genstart for at ændringerne træder i kraft.

<!-- @device:end -->

<!-- @os:end -->