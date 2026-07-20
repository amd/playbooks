<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

For Ryzen AI Halo er den dedikerede GPU-hukommelse som standard 64 GB, hvilket er tilstrækkeligt til de fleste arbejdsbelastninger. Ved større modeller eller længere kontekster kan det hjælpe at øge dette til 96 GB. For at justere det skal du åbne **AMD Software: Adrenalin Edition™** og navigere til **Performance → Tuning → AMD Variable Graphics Memory**. Genstart, for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

For at ændre værdien for dedikeret GPU-hukommelse skal du åbne **AMD Software: Adrenalin Edition™** og navigere til **Performance → Tuning → AMD Variable Graphics Memory**. Genstart, for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

På Linux skal du, for at køre større modeller, øge den **delte hukommelsespulje**, der er tilgængelig for GPU'en. Dette kan indebære, at den dedikerede GPU-hukommelse i BIOS sættes til minimum, så den delte hukommelsespulje kan maksimeres.

<!-- @device:halo_box -->

For AMD Ryzen™ AI Halo er standarden 96 GB delt. For at ændre dette skal du åbne **AMD Ryzen™ AI Developer Center** og gå til fanen **Settings**. Under **Graphics Performance Settings** skal du øge skyderen **Shared Video Memory**, derefter klikke på **Apply Changes** og genstarte, for at ændringerne træder i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Øg den delte hukommelsespulje ved at ændre kernens indstilling for Translation Table Manager (TTM)-sider. AMD anbefaler at indstille den minimale dedikerede VRAM i BIOS (0,5 GB), så den maksimale mængde er tilgængelig som delt hukommelse.

1. Installer værktøjet `pipx`, og tilføj stien til pipx-installerede wheels til systemets søgesti:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installer `amd-debug-tools`-wheel'en fra PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Forespørg de nuværende indstillinger for delt hukommelse:

   ```bash
   amd-ttm
   ```

4. Øg tildelingen af delt hukommelse (enheder i GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Genstart, for at ændringerne træder i kraft.

<!-- @device:end -->

<!-- @os:end -->