<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

För Ryzen AI Halo är standardvärdet för dedikerat GPU-minne 64 GB, vilket räcker för de flesta arbetsbelastningar. För större modeller eller längre kontext kan det hjälpa att öka detta till 96 GB. För att justera detta, öppna **AMD Software: Adrenalin Edition™** och navigera till **Performance → Tuning → AMD Variable Graphics Memory**. Starta om för att ändringarna ska börja gälla.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

För att ändra värdet för dedikerat GPU-minne, öppna **AMD Software: Adrenalin Edition™** och navigera till **Performance → Tuning → AMD Variable Graphics Memory**. Starta om för att ändringarna ska börja gälla.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

På Linux, för att köra större modeller, öka poolen med **delat minne** som är tillgänglig för GPU:n. Detta kan innebära att ställa in det dedikerade GPU-minnet i BIOS till minimum, så att poolen med delat minne kan maximeras.

<!-- @device:halo_box -->

För AMD Ryzen™ AI Halo är standardvärdet 96 GB delat. För att ändra detta, öppna **AMD Ryzen™ AI Developer Center** och gå till fliken **Settings**. Under **Graphics Performance Settings**, öka skjutreglaget **Shared Video Memory**, klicka sedan på **Apply Changes** och starta om för att ändringarna ska börja gälla.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Öka poolen med delat minne genom att ändra kärnans inställning för Translation Table Manager (TTM)-sidor. AMD rekommenderar att ställa in minsta dedikerade VRAM i BIOS (0,5 GB) så att maximal mängd blir tillgänglig som delat minne.

1. Installera verktyget `pipx` och lägg till sökvägen för pipx-installerade wheels till systemets sökväg:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installera wheelen `amd-debug-tools` från PyPI:

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

5. Starta om för att ändringarna ska börja gälla.

<!-- @device:end -->

<!-- @os:end -->