<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Az Ryzen AI Halo esetében a dedikált GPU memória alapértelmezés szerint 64 GB, ami a legtöbb munkaterheléshez elegendő. Nagyobb modellek vagy hosszabb kontextusok esetén érdemes lehet ezt 96 GB-ra növelni. A módosításhoz nyisd meg az **AMD Software: Adrenalin Edition™** alkalmazást, és navigálj a **Performance → Tuning → AMD Variable Graphics Memory** menüponthoz. A változtatások érvénybe lépéséhez indítsd újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

A dedikált GPU memória értékének módosításához nyisd meg az **AMD Software: Adrenalin Edition™** alkalmazást, és navigálj a **Performance → Tuning → AMD Variable Graphics Memory** menüponthoz. A változtatások érvénybe lépéséhez indítsd újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linuxon a nagyobb modellek futtatásához növeld a GPU számára elérhető **megosztott memória** készletet. Ehhez szükséges lehet a BIOS-ban a dedikált GPU memóriát a minimumra állítani, hogy a megosztott memória készlet maximalizálható legyen.

<!-- @device:halo_box -->

Az AMD Ryzen™ AI Halo esetében az alapértelmezett érték 96 GB megosztott memória. Ennek módosításához nyisd meg az **AMD Ryzen™ AI Developer Center** alkalmazást, és lépj a **Settings** fülre. A **Graphics Performance Settings** alatt növeld a **Shared Video Memory** csúszkát, majd kattints az **Apply Changes** gombra, és a változtatások érvénybe lépéséhez indítsd újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Növeld a megosztott memória készletet a kernel Translation Table Manager (TTM) lapbeállításának módosításával. Az AMD azt javasolja, hogy a BIOS-ban állítsd be a minimális dedikált VRAM-ot (0,5 GB), hogy a maximális mennyiség álljon rendelkezésre megosztott memóriaként.

1. Telepítsd a `pipx` segédprogramot, és add hozzá a pipx által telepített wheel-ek elérési útját a rendszer keresési útvonalához:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Telepítsd az `amd-debug-tools` wheel-t a PyPI-ról:

   ```bash
   pipx install amd-debug-tools
   ```

3. Kérdezd le az aktuális megosztott memória beállításokat:

   ```bash
   amd-ttm
   ```

4. Növeld a megosztott memória kiosztást (a mértékegység GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. A változtatások érvénybe lépéséhez indítsd újra a rendszert.

<!-- @device:end -->

<!-- @os:end -->