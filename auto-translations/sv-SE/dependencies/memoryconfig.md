<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

För Ryzen AI Halo är det dedikerade GPU-minnet som standard inställt på 64 GB, vilket räcker för de flesta arbetsbelastningar. För större modeller eller längre kontexter kan det hjälpa att öka detta. För att justera det öppnar du **AMD Software: Adrenalin Edition™** och navigerar till **Performance → Tuning → AMD Variable Graphics Memory**. Starta om för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

För att ändra värdet för det dedikerade GPU-minnet öppnar du **AMD Software: Adrenalin Edition™** och navigerar till **Performance → Tuning → AMD Variable Graphics Memory**. Starta om för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

På Linux, för att köra större modeller, öka poolen med **delat minne** som är tillgänglig för GPU:n. Detta kan innebära att du ställer in det dedikerade GPU-minnet i BIOS till minimum, så att poolen med delat minne kan maximeras.

<!-- @device:halo_box -->

För AMD Ryzen™ AI Halo, för att ändra standardinställningen, öppnar du **AMD Ryzen™ AI Developer Center** och går till fliken **Settings**. Under **Graphics Performance Settings** ökar du skjutreglaget **Shared Video Memory**, klickar sedan på **Apply Changes** och startar om för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Öka poolen med delat minne genom att ändra kärnans inställning för Translation Table Manager (TTM)-sidor. AMD rekommenderar att ställa in det dedikerade minimum-VRAM:et i BIOS (0,5 GB) så att den maximala mängden blir tillgänglig som delat minne.

1. Installera verktyget `pipx` och lägg till sökvägen för pipx-installerade wheels till systemets sökväg:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installera `amd-debug-tools`-wheelen från PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Fråga efter de aktuella inställningarna för delat minne:

   ```bash
   amd-ttm
   ```

4. Öka tilldelningen av delat minne (enheter i GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Starta om för att ändringarna ska träda i kraft.

<!-- @device:end -->

<!-- @os:end -->