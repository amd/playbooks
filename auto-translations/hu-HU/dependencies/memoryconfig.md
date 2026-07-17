<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

A Ryzen AI Halo esetén a dedikált GPU memória alapértelmezés szerint 64 GB, ami a legtöbb munkaterheléshez elegendő. Nagyobb modellek vagy hosszabb kontextusok esetén ennek 96 GB-ra növelése segíthet. A módosításhoz nyissa meg az **AMD Software: Adrenalin Edition™** alkalmazást, és navigáljon a **Performance → Tuning → AMD Variable Graphics Memory** menüponthoz. A változtatások érvénybe lépéséhez indítsa újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

A dedikált GPU memória értékének módosításához nyissa meg az **AMD Software: Adrenalin Edition™** alkalmazást, és navigáljon a **Performance → Tuning → AMD Variable Graphics Memory** menüponthoz. A változtatások érvénybe lépéséhez indítsa újra a rendszert.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linux rendszeren a nagyobb modellek futtatásához növelje a GPU számára elérhető **megosztott memória** készletet. Ez magában foglalhatja a BIOS-ban a dedikált GPU memória minimumra állítását, hogy a megosztott memória készlet maximalizálható legyen.

<!-- @device:halo_box -->

Az AMD Ryzen™ AI Halo esetén az alapértelmezett érték 96 GB megosztott memória. Ennek módosításához nyissa meg az **AMD Ryzen™ AI Developer Center** alkalmazást, és lépjen a **Settings** fülre. A **Graphics Performance Settings** alatt növelje a **Shared Video Memory** csúszkát, majd kattintson az **Apply Changes** gombra, és indítsa újra a rendszert a változtatások érvénybe lépéséhez.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Növelje a megosztott memória készletet a kernel Translation Table Manager (TTM) oldal beállításának módosításával. Az AMD azt javasolja, hogy a BIOS-ban állítsa be a minimális dedikált VRAM értéket (0,5 GB), hogy a maximális mennyiség megosztott memóriaként legyen elérhető.

1. Telepítse a `pipx` segédprogramot, és adja hozzá a pipx által telepített csomagok elérési útját a rendszer keresési útvonalához:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Telepítse az `amd-debug-tools` csomagot a PyPI-ről:

   ```bash
   pipx install amd-debug-tools
   ```

3. Kérdezze le az aktuális megosztott memória beállításokat:

   ```bash
   amd-ttm
   ```

4. Növelje a megosztott memória kiosztását (egység: GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. A változtatások érvénybe lépéséhez indítsa újra a rendszert.

<!-- @device:end -->

<!-- @os:end -->