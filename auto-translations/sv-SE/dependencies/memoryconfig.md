<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

För Ryzen AI Halo är det dedikerade GPU-minnet som standard 64 GB, vilket är tillräckligt för de flesta arbetsbelastningar. För större modeller eller längre kontexter kan det hjälpa att öka detta till 96 GB. För att justera, öppna **AMD Software: Adrenalin Edition™** och navigera till **Performance → Tuning → AMD Variable Graphics Memory**. Starta om datorn för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

För att ändra värdet för dedikerat GPU-minne, öppna **AMD Software: Adrenalin Edition™** och navigera till **Performance → Tuning → AMD Variable Graphics Memory**. Starta om datorn för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

På Linux, för att köra större modeller, öka den **delade minnespool** som är tillgänglig för GPU:n. Detta kan innebära att du ställer in det dedikerade GPU-minnet i BIOS till ett minimum, så att den delade minnespoolen kan maximeras.

<!-- @device:halo_box -->

För AMD Ryzen™ AI Halo är standardvärdet 96 GB delat minne. För att ändra detta, öppna **AMD Ryzen™ AI Developer Center** och gå till fliken **Settings**. Under **Graphics Performance Settings**, öka reglaget för **Shared Video Memory**, klicka sedan på **Apply Changes** och starta om datorn för att ändringarna ska träda i kraft.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Öka den delade minnespoolen genom att ändra kärnans inställning för Translation Table Manager (TTM)-sidor. AMD rekommenderar att du ställer in det minsta dedikerade VRAM i BIOS (0,5 GB) så att maximal mängd är tillgänglig som delat minne.

1. Installera verktyget `pipx` och lägg till sökvägen för pipx-installerade paket i systemets sökväg:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installera paketet `amd-debug-tools` från PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Fråga de aktuella inställningarna för delat minne:

   ```bash
   amd-ttm
   ```

4. Öka allokeringen av delat minne (enheter i GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Starta om datorn för att ändringarna ska träda i kraft.

<!-- @device:end -->

<!-- @os:end -->