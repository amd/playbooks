<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Voor de Ryzen AI Halo is het toegewezen GPU-geheugen standaard ingesteld op 64 GB, wat voldoende is voor de meeste werklasten. Voor grotere modellen of langere contexten kan het verhogen naar 96 GB helpen. Om dit aan te passen, opent u **AMD Software: Adrenalin Edition™** en navigeert u naar **Performance → Tuning → AMD Variable Graphics Memory**. Start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Om de waarde van het toegewezen GPU-geheugen te wijzigen, opent u **AMD Software: Adrenalin Edition™** en navigeert u naar **Performance → Tuning → AMD Variable Graphics Memory**. Start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Op Linux kunt u, om grotere modellen uit te voeren, de **gedeelde geheugen**pool die beschikbaar is voor de GPU vergroten. Dit kan inhouden dat u het toegewezen GPU-geheugen in het BIOS op het minimum instelt, zodat de gedeelde geheugenpool gemaximaliseerd kan worden.

<!-- @device:halo_box -->

Voor de AMD Ryzen™ AI Halo is de standaard 96 GB gedeeld. Om dit te wijzigen, opent u het **AMD Ryzen™ AI Developer Center** en gaat u naar het tabblad **Settings**. Vergroot onder **Graphics Performance Settings** de schuifregelaar **Shared Video Memory**, klik vervolgens op **Apply Changes** en start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Vergroot de gedeelde geheugenpool door de Translation Table Manager (TTM)-pagina-instelling van de kernel te wijzigen. AMD raadt aan om het minimale toegewezen VRAM in het BIOS in te stellen (0,5 GB), zodat de maximale hoeveelheid beschikbaar is als gedeeld geheugen.

1. Installeer het hulpprogramma `pipx` en voeg het pad voor door pipx geïnstalleerde wheels toe aan het zoekpad van het systeem:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installeer het `amd-debug-tools`-wheel van PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Raadpleeg de huidige instellingen voor gedeeld geheugen:

   ```bash
   amd-ttm
   ```

4. Vergroot de toewijzing van gedeeld geheugen (eenheden in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Start opnieuw op om de wijzigingen door te voeren.

<!-- @device:end -->

<!-- @os:end -->